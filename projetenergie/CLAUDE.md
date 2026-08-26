# CLAUDE.md — Contexte projet Smart Senelec

Ce fichier résume l'état du projet, les décisions techniques prises, et les pièges déjà rencontrés — pour qu'une session future (humaine ou IA) n'ait pas à tout redécouvrir.

## Vue d'ensemble

App fullstack de suivi énergétique : FastAPI + Angular + SQL Server + Redis, orchestrés via Docker Compose. Le projet part d'une base de données Excel (7 fichiers dans `backend/data/`) qui doit être importée en SQL Server au démarrage.

## Architecture des conteneurs

| Service | Image | Port hôte | Notes |
|---|---|---|---|
| db | mssql/server:2022-latest | 1433 | mdp `YourStrong!Pass`, DB `SmartSenelec` |
| redis | redis:7-alpine | 6379 | |
| backend | build local (Python 3.11) | 8000 | monte `./backend` et `./data` |
| frontend | build local (Nginx) | 8080 | sert le build Angular + proxy `/api/` |

Réseau Docker : `senelec-network`. Les conteneurs se résolvent par nom de service (`db`, `redis`, `backend`).

## Authentification

- JWT maison en HS256, secret hardcodé `"a_secret_key"` dans `app/core/security.py` **et** `app/api/api_v1/endpoints/login.py` — **doit matcher dans les deux fichiers**. À sortir en variable d'environnement avant prod.
- Un seul utilisateur hardcodé : `admin` / `admin123`. Pas de table utilisateurs.
- Vestiges de Keycloak dans le code (`OAuth2PasswordBearer`, `realm_access.roles`) — l'intégration a été abandonnée mais la structure du payload JWT a été gardée. Non bloquant, mais à nettoyer si Keycloak n'est définitivement plus prévu.
- Frontend : `authInterceptor` attache `Authorization: Bearer <token>` à chaque requête HTTP sortante. `authGuard` protège les routes. Token stocké dans `localStorage`.
- Proxy Nginx (`frontend/nginx.conf`) : toute requête `/api/` est redirigée vers `http://backend:8000/api/` — sans ce bloc, les appels API renvoient 405.

## Base de données — points importants

### `Base.metadata.create_all()` ne migre jamais un schéma existant
Ce projet n'utilise **pas Alembic**. Chaque changement de modèle SQLAlchemy nécessite de **DROP les tables manuellement** avant de relancer le backend, sinon erreurs `Invalid column name` ou contraintes obsolètes qui persistent.

**Commande de reset complet** (ordre important à cause des FK — enfants d'abord) :
```bash
docker exec -it projetenergie-db-1 /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Pass" -d SmartSenelec -C -Q "DROP TABLE IF EXISTS deplacement_groupes; DROP TABLE IF EXISTS groupes; DROP TABLE IF EXISTS production_mensuelle; DROP TABLE IF EXISTS centrales; DROP TABLE IF EXISTS rendements; DROP TABLE IF EXISTS recap_energie; DROP TABLE IF EXISTS type_reseau_producteurs;"
docker compose restart backend
```

**Vérifier le comptage de lignes** :
```bash
docker exec -it projetenergie-db-1 /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Pass" -d SmartSenelec -C -Q "SELECT t.name AS TableName, SUM(p.rows) AS NombreLignes FROM sys.tables t INNER JOIN sys.partitions p ON t.object_id = p.object_id WHERE p.index_id IN (0,1) GROUP BY t.name ORDER BY t.name;"
```

**Si erreur "Table already defined for this MetaData instance"** au démarrage : résidu de cache Docker, rebuild avec `docker compose build --no-cache backend`.

### Pourquoi des colonnes `id_*_externe` en `BigInteger` (pas `Integer`)

Les fichiers Excel sources utilisent des identifiants internes (`IDCentrale`, `IDGroupe`, `ID_Rendement`, `IDRecapEnergie`) qui **ne sont pas de simples compteurs** — certaines valeurs dépassent 2×10^17 (largement au-delà de la limite d'`Integer` en SQL Server, ~2,1 milliards). Toutes les colonnes `id_*_externe` sont donc en `BigInteger`. Origine de ces grandes valeurs non identifiée avec certitude (possiblement des IDs de réplication Access ou un artefact d'export).

Ces colonnes servent de **clé de dédoublonnage et de jointure** entre fichiers (ex: `ProductionMensuelle.ID_Centrale` référence `Centrale.IDCentrale`, pas le nom).

### Pourquoi les processeurs Excel utilisent un `seen_ids = set()` en mémoire

Certaines lignes du même fichier Excel partagent le **même ID externe** (probablement des entrées placeholder/génériques mal identifiées dans la source, ex: 4 centrales différentes — `Location Tamba`, `AGGREKO KOLDA`, etc. — partagent l'ID `218706056904179008`). La vérification `db.query(...).filter(id == X).first()` seule ne suffit pas car rien n'est encore committé pendant la boucle d'import d'un même fichier ; deux lignes avec le même ID dans le batch en cours ne se "voient" pas. D'où le `set()` Python qui garde uniquement la première occurrence par fichier.

**Conséquence connue** : les doublons intra-fichier au-delà du premier sont silencieusement perdus. Acceptable pour l'instant, mais si ces entrées sont importantes individuellement, il faudra un système d'ID de substitution généré côté application plutôt que de réutiliser l'ID Excel brut.

### `nom` sur `Centrale` n'est plus `unique`

Le fichier réel contient des centrales homonymes (ex: deux entrées `"Tobene Power"` avec des `IDCentrale` différents). La vraie clé d'unicité est `id_centrale_externe`, pas le nom.

### `Rendement.date` et `RecapEnergie.date` ne sont plus `unique`

Erreur initiale de conception : on avait supposé un enregistrement par date, mais chaque date apparaît en réalité plusieurs dizaines de fois dans ces fichiers (une ligne par centrale/poste source, pas une agrégation globale par date). Les vraies clés d'unicité sont `id_rendement_externe` (`ID_Rendement`) et `id_recap_externe` (`IDRecapEnergie`).

## Mapping colonnes Excel → modèles (état actuel)

| Fichier Excel | table_type | Statut |
|---|---|---|
| `TypeReseauProducteur.xlsx` | `type_reseau` | ✅ Import complet et fiable |
| `Centrale.xlsx` | `centrale` | ✅ 72/81 lignes (9 doublons d'ID filtrés, attendu) |
| `Production_Mensuelle_*.xlsx` | `production` | ✅ Import complet (3243/3243) |
| `Rendement_*.xlsx` | `rendement` | ✅ Import complet (123/123) |
| `Recap_Energie.xlsx` | `recap` | ⚠️ Import complet (74/74) mais **mapping approximatif** — voir ci-dessous |
| `Groupe.xlsx` | `groupe` | ⚠️ Import partiel (262/524) — cause exacte non investiguée |
| `Deplacement_groupe.xlsx` | `deplacement_groupe` | ✅ 752/766, cohérent (dépend de Groupe) |

### Colonnes réelles confirmées (extraites directement des fichiers, pas du PDF)

**Centrale.xlsx** : `IDCentrale, NomCentrale, IDTypeCentrale, IDCentraleMere, SenlecFournitCombLub, CentraleDeclassee, IDTypeReseauProducteur`
(⚠️ `SenlecFournitCombLub` — orthographe réelle du fichier, pas une faute de frappe du code)

**Production_Mensuelle**: `ID_ProductionMensuelle, Date_FinDuMois, Production_Centrale, ConsAux, ID_Centrale`

**Rendement**: `ID_Rendement, Date_Rendement, Vente_Woyofal, Vente_Energie_Classique_MT_BT, Production_Senelec, Production_IPP, Energie_ReseauHTA, Producteur_HTA, Energie_ReseauHTB, Producteur_HTB, Client_HTA, Client_HTB, Rendement_Global, Rendement_HTA, Rendement_HTB, ...` (colonnes supplémentaires non mappées : `MontantFactureTTC`, `MontantWoyofal`, `Auxiliaire_*`, `Date_Ecriture`, `PRODUCTION_IMPORTE`, `PRODUCTION_ACHAT_GLOBAL`, etc. — non utilisées dans le modèle actuel, à ajouter si besoin métier)

**Recap_Energie** (confirmé via script `check_columns.py` exécuté dans le conteneur) : `IDRecapEnergie, Date_Debut, Date_Fin, Poste Source, DEPART30KV, TAUXDEPART30KV, TRANSFOHTBHTAEMS, TAUXTRANSFOHTBHTAEMS, TRANSFOHTBHTA, TAUXTRANSFOHTBHTA, SCCNSCADA, TAUXSCCNSCADA, DEPART30KVDMS, TAUXDEPART30KVDMS, TRANSFOHTBHTADMS, TAUXTRANSFOHTBHTADMS, TRANSFOHTBHTADESA, TAUXTRANSFOHTBHTADESA, SOURCEDONNEES, EnergieValidee`

⚠️ **Le modèle `RecapEnergie` n'a qu'un seul champ pour `transformateur_htb_hta`, `dms`, `desa`** alors que le fichier a plusieurs variantes (`EMS`, `DMS`, `DESA` pour chaque mesure, avec leurs taux associés). Le mapping actuel dans `excel_service.py` a choisi une colonne par champ au jugé (`TRANSFOHTBHTA`, `DEPART30KVDMS`, `TRANSFOHTBHTADESA`, `TAUXDEPART30KV`) — **à valider avec un expert métier**, ce n'est probablement pas la source de vérité correcte pour chaque champ. Le modèle mériterait d'être enrichi pour capturer toutes les colonnes source si ces données sont utilisées pour du reporting précis.

**Groupe.xlsx** : `IDGroupe, NomGroupe, IDCentrale, EtatCompteurHeureMarche, EtatCompteurAuxiliare, EtatCompteurEnergie, DernierIndexEnergie, GroupeClasse, PuissanceNominale, IDMoteur, IDAlternateur, uniteCompteurUniHoraire, IDTypeDeProduction, CopieDeIDGroupe`
(colonnes déduites d'un export PDF partiellement corrompu — moins fiables que les autres, à revalider avec `check_columns.py` si des anomalies apparaissent)

**Deplacement_groupe.xlsx** : `IDDeplacementGroupes, DateDebut, DateFin, IDGroupe, IDCentrale` (fiable)

## Points ouverts / à investiguer

1. **`Groupe.xlsx` : 262/524 lignes importées.** Cause non confirmée — hypothèses : beaucoup de doublons `IDGroupe` légitimes dans le fichier (comme pour `Centrale`), ou lignes avec `IDGroupe` manquant/invalide. À creuser avec `check_columns.py` si cette table doit être fiable pour un usage métier.

2. **`Recap_Energie` : mapping des colonnes `TRANSFO*`/`DMS`/`DESA` à confirmer** avec un expert métier — actuellement un choix arbitraire parmi plusieurs colonnes candidates.

3. **Modèle `Rendement` incomplet** — le fichier source a ~2x plus de colonnes que ce qui est actuellement mappé (montants financiers, dates d'écriture, imports/achats). À enrichir si ces données doivent être exposées au frontend.

4. **Secret JWT hardcodé** — à déplacer en variable d'environnement (`.env` / `docker-compose.yml`) avant tout déploiement au-delà du dev local.

5. **Un seul utilisateur admin hardcodé** — pas de gestion d'utilisateurs. À prévoir si l'app doit supporter plusieurs comptes/rôles (les rôles `admin/analyste/manager/operateur` existent déjà dans le payload JWT mais ne sont pas exploités côté backend pour restreindre l'accès).

6. **Dashboards Angular pas encore connectés** — `dashboard-hta`, `dashboard-htb`, `production`, `ventes` existent comme pages mais n'affichent pas encore les données réelles issues de l'API.

## Outils de debug créés pendant le développement

`check_columns.py` — script à copier dans le conteneur backend pour inspecter les vraies colonnes/données d'un fichier Excel sans dépendre d'extraction PDF (peu fiable pour les tableaux complexes) :
```bash
docker cp backend/check_columns.py projetenergie-backend-1:/app/check_columns.py
docker exec -it projetenergie-backend-1 python check_columns.py
```

## Commandes utiles

```bash
# Logs backend en direct
docker compose logs -f backend

# État de tous les conteneurs
docker compose ps

# Rebuild complet sans cache (si comportement suspect après modif de fichiers)
docker compose build --no-cache backend
docker compose up

# Tester un import Excel isolé sans relancer tout Docker
# (via Swagger UI http://localhost:8080/api/v1/docs, endpoint POST /import/{table_type})
```

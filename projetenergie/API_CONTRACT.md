# API Contract — Smart Senelec

Base URL (via proxy Nginx, depuis le frontend) : `/api/v1`
Base URL (accès direct backend) : `http://localhost:8000/api/v1`

Documentation interactive : `/api/v1/docs` (Swagger UI)

## Authentification

Tous les endpoints listés plus bas (sauf `/login`) nécessitent un header :
```
Authorization: Bearer <token>
```

### POST /login

Authentifie un utilisateur et retourne un JWT.

**Content-Type** : `application/x-www-form-urlencoded`

**Body**
| Champ | Type | Requis |
|---|---|---|
| username | string | oui |
| password | string | oui |

**Réponse 200**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Réponse 400** — identifiants incorrects
```json
{ "detail": "Incorrect username or password" }
```

**Notes**
- Algorithme : HS256, clé secrète actuellement codée en dur (`"a_secret_key"`) — à déplacer en variable d'environnement avant mise en production.
- Expiration du token : 30 minutes.
- Le payload contient `sub` (username) et `realm_access.roles` (hérité d'une intégration Keycloak abandonnée — structure conservée mais non utilisée pour l'instant).
- Seul l'utilisateur `admin` / `admin123` existe (hardcodé). Pas de table utilisateurs pour l'instant.

---

## Centrales

### GET /centrales

Liste les centrales. 🔒 Authentifié. **Mis en cache Redis** (clé `centrales:{skip}:{limit}`, TTL 3600s).

**Query params** : `skip` (int, défaut 0), `limit` (int, défaut 100)

**Réponse 200** — tableau de `Centrale` (voir schéma ci-dessous)

---

## Rendements

### GET /rendements

Liste les enregistrements de rendement énergétique. 🔒 Authentifié. **Mis en cache Redis** (clé `rendements:{skip}:{limit}`, TTL 3600s).

**Query params** : `skip`, `limit`

**Réponse 200** — tableau de `Rendement`

---

## Récap énergie

### GET /recap-energie

Liste les récapitulatifs énergie par poste source. 🔒 Authentifié. **Mis en cache Redis** (clé `recap_energie:{skip}:{limit}`, TTL 3600s — voir `CLAUDE.md` pour les limites actuelles de cette implémentation).

**Query params** : `skip`, `limit`

**Réponse 200** — tableau de `RecapEnergie`

---

## Production mensuelle

### GET /production

Liste les enregistrements de production mensuelle par centrale. 🔒 Authentifié. **Mis en cache Redis** (clé `production:{skip}:{limit}:{centrale_id}`, TTL 3600s).

**Query params** : `skip`, `limit`, `centrale_id` (optionnel — filtre sur une centrale précise)

**Réponse 200** — tableau de `ProductionMensuelle`

---

## Groupes (équipements)

### GET /groupes

Liste les groupes (moteurs/alternateurs) rattachés aux centrales. 🔒 Authentifié. **Mis en cache Redis** (clé `groupes:{skip}:{limit}:{centrale_id}`, TTL 3600s).

**Query params** : `skip`, `limit`, `centrale_id` (optionnel)

**Réponse 200** — tableau de `Groupe`

---

## Déplacements de groupes

### GET /deplacement-groupes

Historique des déplacements de groupes entre centrales. 🔒 Authentifié. **Mis en cache Redis** (clé `deplacement_groupes:{skip}:{limit}:{groupe_id}`, TTL 3600s).

**Query params** : `skip`, `limit`, `groupe_id` (optionnel)

**Réponse 200** — tableau de `DeplacementGroupe`

---

## Type réseau producteur

### GET /type-reseau-producteurs

Table de correspondance type de réseau / producteur. 🔒 Authentifié. **Mis en cache Redis** (clé `type_reseau_producteurs:{skip}:{limit}`, TTL 3600s).

**Query params** : `skip`, `limit`

**Réponse 200** — tableau de `TypeReseauProducteur`

---

## Import Excel

### POST /import/{table_type}

Importe manuellement un fichier Excel dans la table correspondante. 🔒 Authentifié.

**Path param** `table_type` — une des valeurs :
| Valeur | Table cible |
|---|---|
| `centrale` | centrales |
| `production` | production_mensuelle |
| `rendement` | rendements |
| `recap` | recap_energie |
| `type_reseau` | type_reseau_producteurs |
| `groupe` | groupes |
| `deplacement_groupe` | deplacement_groupes |

**Body** : `multipart/form-data`, champ `file` (fichier `.xlsx`)

**Réponse 200**
```json
{
  "status": "success",
  "rows_read": 81,
  "rows_inserted": 72
}
```
`rows_inserted` peut être inférieur à `rows_read` : lignes sans identifiant exploitable, ou doublons (déjà en base ou dupliqués dans le fichier) sont ignorés silencieusement, sans faire échouer l'import.

**Réponse 400** — type de table inconnu

---

## Schémas de données (résumé)

> Champs `id_*_externe` : conservent l'identifiant du fichier Excel source, utilisés pour la déduplication et les jointures entre fichiers. Voir `CLAUDE.md` pour le détail.

### Centrale
`id, id_centrale_externe, nom, type_centrale, centrale_mere, reseau_producteur, lieu, parc, type_ipp, service_production, senelec_fournit_comb_lub, centrale_declassee`

### ProductionMensuelle
`id, centrale_id, reseau_producteur, consommation_auxiliaire, date, valeur_production`

### Rendement
`id, id_rendement_externe, date, vente_woyofal, vente_classique, production_senelec, production_ipp, energie_hta, energie_htb, producteur_hta, producteur_htb, client_hta, client_htb, rendement_global, rendement_hta, rendement_htb`

### RecapEnergie
`id, id_recap_externe, poste_source, depart_30kv, transformateur_htb_hta, sccn_scada, dms, desa, taux_energie, source_donnees, energie_validee, date`

### Groupe
`id, id_groupe_externe, nom, centrale_id, moteur, alternateur, type_production, puissance_nominale, compteur_energie`

### DeplacementGroupe
`id, groupe_id, centrale_source_id, date_debut, date_fin`

### TypeReseauProducteur
`id, type_reseau, producteur, libelle`

---

## Endpoints à venir (pas encore implémentés)

D'après les pages frontend existantes (`production`, `ventes`), des endpoints dédiés seront probablement nécessaires — actuellement le frontend ne consomme pas encore les données réelles sur ces pages.

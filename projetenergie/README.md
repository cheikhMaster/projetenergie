# Smart Senelec

Application fullstack de suivi énergétique (production, rendement, réseau HTA/HTB) pour Senelec.

## Stack technique

- **Backend** : FastAPI (Python 3.11), SQLAlchemy, JWT (HS256)
- **Frontend** : Angular (standalone components), Nginx (reverse proxy + serveur statique)
- **Base de données** : SQL Server 2022 (`mssql+pyodbc`, ODBC Driver 18)
- **Cache** : Redis 7
- **Orchestration** : Docker Compose

## Structure du projet

```
projetenergie/
├── backend/
│   ├── app/
│   │   ├── api/api_v1/          # routers FastAPI (endpoints)
│   │   ├── core/                # config, sécurité (JWT)
│   │   ├── db/                  # session SQLAlchemy, connexion Redis
│   │   ├── models/               # modèles SQLAlchemy (energy_system.py)
│   │   ├── schemas/              # schémas Pydantic
│   │   ├── services/             # excel_service.py, cache_service.py
│   │   ├── initial_data.py       # import automatique des fichiers Excel au démarrage
│   │   └── main.py
│   ├── data/                     # fichiers Excel sources (Centrale, Groupe, Rendement...)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── guards/                # authGuard
│   │   ├── interceptors/          # authInterceptor (attache le JWT)
│   │   ├── pages/                 # login, dashboard-hta, dashboard-htb, production, ventes
│   │   └── services/              # auth.service.ts
│   ├── nginx.conf                 # proxy /api/ -> backend:8000
│   └── Dockerfile
└── docker-compose.yml
```

## Démarrage

```bash
docker compose up --build
```

- Frontend : http://localhost:8080
- Backend (direct, hors proxy) : http://localhost:8000
- Swagger / docs API : http://localhost:8080/api/v1/docs
- SQL Server : localhost:1433
- Redis : localhost:6379

**Identifiants de connexion (dev uniquement)** : `admin` / `admin123`

## Import automatique des données

Au premier démarrage, `initial_data.py` scanne `backend/data/*.xlsx` et importe automatiquement 7 fichiers dans l'ordre suivant (dépendances) :

1. `TypeReseauProducteur.xlsx`
2. `Centrale.xlsx`
3. `Production_Mensuelle_*.xlsx`
4. `Rendement_*.xlsx`
5. `Recap_Energie.xlsx`
6. `Groupe.xlsx`
7. `Deplacement_groupe.xlsx`

L'import ne se relance **pas** automatiquement si des données existent déjà (vérifie `Centrale`). Pour forcer un ré-import complet, voir `CLAUDE.md` (section "Réinitialiser la base").

## État actuel / limitations connues

Voir `CLAUDE.md` pour le détail des choix techniques, des données atypiques rencontrées, et des points encore ouverts (notamment l'import partiel de `Groupe.xlsx`, et le mapping approximatif de `Recap_Energie`).

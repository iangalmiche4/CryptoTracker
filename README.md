# 🚀 CryptoTracker

Application full-stack moderne de suivi de cryptomonnaies avec authentification, portfolio personnel et alertes de prix.

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react) ![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)

## ✨ Fonctionnalités

- 🔐 **Authentification sécurisée** - JWT + bcrypt
- 📊 **Dashboard personnalisable** - Suivez vos cryptos
- 💼 **Portfolio** - Gérez vos investissements et suivez vos gains/pertes
- 🔔 **Alertes de prix** - Notifications quand un seuil est franchi
- 📈 **Graphiques interactifs** - Historique des prix sur 7/14/30/90 jours
- 🎨 **Thème clair/sombre** - Interface moderne avec Material-UI
- 🌍 **Multilingue** - Français et Anglais

## 🛠️ Stack Technique

**Frontend:** React 19, Vite, Material-UI, TanStack Query, Recharts
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
**API:** CoinGecko (gratuit, sans clé)

### 📚 Bibliothèques Principales

#### Frontend

| Bibliothèque | Rôle |
|--------------|------|
| **React 19** | Framework UI avec hooks modernes |
| **Vite** | Build tool ultra-rapide avec HMR |
| **Material-UI (MUI)** | Composants UI prêts à l'emploi (Card, Dialog, TextField...) |
| **TanStack Query** | Gestion du cache et des requêtes API (auto-retry, invalidation) |
| **React Router** | Navigation multi-pages avec routes protégées |
| **Recharts** | Graphiques React responsifs et personnalisables |
| **Axios** | Client HTTP avec intercepteurs pour JWT |
| **@dnd-kit** | Drag & drop accessible et performant |

#### Backend

| Bibliothèque | Rôle |
|--------------|------|
| **FastAPI** | Framework web Python async avec validation automatique |
| **PostgreSQL** | Base de données relationnelle robuste |
| **SQLAlchemy** | ORM Python pour manipuler la DB avec des objets |
| **Alembic** | Gestion des migrations de schéma DB |
| **Uvicorn** | Serveur ASGI haute performance |
| **python-jose** | Génération et validation de tokens JWT |
| **passlib + bcrypt** | Hachage sécurisé des mots de passe |
| **httpx** | Client HTTP async pour appeler CoinGecko |
| **Pydantic** | Validation des données avec type hints |

## 📦 Installation Rapide

### Prérequis

- Node.js ≥ 18
- Python ≥ 3.10
- PostgreSQL ≥ 14

### 1. Cloner le projet

```bash
git clone https://github.com/iangalmiche4/CryptoTracker
cd cryptotracker
```

### 2. Configuration PostgreSQL

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE cryptotracker;
\q
```

### 3. Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Installer les dépendances
pip install -r requirements.txt

# Configurer .env
# Éditer backend/.env et remplacer VOTRE_MOT_DE_PASSE par votre mot de passe PostgreSQL
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/cryptotracker
SECRET_KEY=votre-cle-secrete-generee  # Générer avec: python -c "import secrets; print(secrets.token_hex(32))"

# Créer les tables
alembic upgrade head
```

### 4. Frontend

```bash
cd frontend

# Installer les dépendances
npm install
```

## 🚀 Lancer l'Application

### Terminal 1 - Backend

```bash
cd backend
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
uvicorn main:app --reload --port 8000
```

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

### Accès

- **Application:** http://localhost:5173
- **API:** http://localhost:8000
- **Documentation API:** http://localhost:8000/docs

## 📖 Utilisation

1. **Créer un compte** sur http://localhost:5173
2. **Dashboard:** Recherchez et ajoutez des cryptos (bitcoin, ethereum, solana...)
3. **Portfolio:** Cliquez sur "My Portfolio" pour gérer vos investissements
4. **Alertes:** Configurez des alertes de prix via l'icône 🔔
5. **Détails:** Cliquez sur une carte pour voir les graphiques et métriques

## 📁 Structure du Projet

```
cryptotracker/
├── backend/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   ├── database.py          # Configuration DB
│   ├── core/
│   │   ├── security.py      # JWT + bcrypt
│   │   ├── cache.py         # Cache en mémoire
│   │   └── exceptions.py    # Exceptions personnalisées
│   ├── routers/
│   │   ├── auth.py          # Authentification
│   │   ├── user.py          # Données utilisateur
│   │   ├── coingecko.py     # Proxy CoinGecko
│   │   └── holdings.py      # Portfolio
│   ├── services/
│   │   └── coingecko_service.py  # Service API CoinGecko
│   └── alembic/             # Migrations DB
│
└── frontend/
    ├── src/
    │   ├── pages/           # Login, Register, Portfolio, CoinDetail
    │   ├── components/      # Composants réutilisables
    │   ├── contexts/        # Auth, Theme, Language
    │   ├── hooks/           # Custom hooks
    │   ├── api/             # Clients API
    │   └── locales/         # Traductions (fr, en)
    └── package.json
```

## 🧪 Tests

```bash
cd backend
pytest                    # Lancer tous les tests
pytest --cov             # Avec couverture
pytest -v                # Mode verbeux
```

## 🔧 Commandes Utiles

### Base de données

```bash
# Voir les tables
psql -U postgres -d cryptotracker -c "\dt"

# Créer une migration
cd backend
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Réinitialiser la DB
psql -U postgres -c "DROP DATABASE cryptotracker;"
psql -U postgres -c "CREATE DATABASE cryptotracker;"
alembic upgrade head
```

### Build Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 API Endpoints

### Authentification
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `GET /api/auth/me` - Utilisateur courant

### Données Utilisateur (protégées)
- `GET /api/user/data` - Toutes les données
- `POST /api/user/coins` - Ajouter un coin
- `DELETE /api/user/coins/{coin_id}` - Supprimer un coin
- `POST /api/user/alerts` - Créer une alerte

### Portfolio (protégées)
- `GET /api/holdings` - Liste des investissements
- `POST /api/holdings` - Créer un investissement
- `PUT /api/holdings/{id}` - Modifier un investissement
- `DELETE /api/holdings/{id}` - Supprimer un investissement
- `GET /api/holdings/summary` - Résumé du portfolio

### CoinGecko (proxy)
- `GET /api/prices?coins=bitcoin,ethereum` - Prix en temps réel
- `GET /api/search?q=cardano` - Recherche de coins
- `GET /api/history/{coin_id}?days=7` - Historique
- `GET /api/detail/{coin_id}` - Détails complets

## 🐛 Dépannage

**Erreur de connexion PostgreSQL:**
- Vérifier que PostgreSQL est démarré
- Vérifier le mot de passe dans `backend/.env`
- Vérifier que la base `cryptotracker` existe

**Port déjà utilisé:**
```bash
# Backend (port 8000)
uvicorn main:app --reload --port 8001

# Frontend (port 5173)
npm run dev -- --port 5174
```

**Erreur de migration:**
```bash
cd backend
alembic downgrade -1    # Revenir en arrière
alembic upgrade head    # Réappliquer
```
---


# 🚀 CryptoTracker - Application de Suivi de Cryptomonnaies

Application full-stack moderne pour suivre les prix des cryptomonnaies, gérer un portfolio et configurer des alertes de prix.

## 📋 Prérequis

Avant de commencer, installez :

1. **Python 3.11+** → [python.org/downloads](https://www.python.org/downloads/)
2. **Node.js 18+** → [nodejs.org](https://nodejs.org/)
3. **PostgreSQL 16+** → [postgresql.org/download](https://www.postgresql.org/download/)
4. **Docker Desktop** → [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) (pour Redis)

## ⚡ Démarrage Rapide

```powershell
# Windows PowerShell
.\setup.ps1    # Installation (première fois)
.\start.ps1    # Démarrage

# Windows CMD
setup.bat      # Installation (première fois)
start.bat      # Démarrage

# Linux/macOS
./setup.sh     # Installation (première fois)
./start.sh     # Démarrage
```

**Puis ouvrez** → http://localhost:5173

---

## 📋 Table des Matières

- [Stack Technique](#-stack-technique)
- [Architecture](#️-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)
- [Fonctionnalités](#-fonctionnalités)
- [Dépannage](#-dépannage)
- [Scripts Utiles](#-scripts-utiles)

---

## 📚 Stack Technique

**Backend**
- FastAPI (Python 3.11+) + SQLAlchemy ORM
- PostgreSQL + Redis (cache)
- JWT (authentification) + Bcrypt
- CoinGecko API

**Frontend**
- React 18 + Vite
- Material-UI + Tailwind CSS
- TanStack Query (cache client)
- Axios

---

## 🏗️ Architecture

### Structure Backend

```
backend/
├── main.py              # Point d'entrée FastAPI
├── config.py            # Configuration centralisée
├── models.py            # Modèles SQLAlchemy
├── schemas.py           # Schémas Pydantic
├── core/                # Infrastructure
│   ├── cache.py        # Redis avec fallback
│   ├── security.py     # JWT + Bcrypt
│   └── exceptions.py   # Exceptions personnalisées
├── services/           # Business Logic
│   └── coingecko_service.py
└── routers/            # Controllers REST
    ├── auth.py         # Authentification
    ├── user.py         # Données utilisateur
    ├── coingecko.py    # Prix cryptos
    └── holdings.py     # Portfolio
```

### Bonnes Pratiques

✅ Dependency Injection (FastAPI Depends)  
✅ Service Layer Pattern  
✅ Cache Redis (60-80% réduction appels API)  
✅ Validation Pydantic  
✅ Sécurité (JWT + Bcrypt + CORS)  
✅ Tests Unitaires (Pytest, 86% couverture)  
✅ Migrations DB (Alembic)  
✅ Principes SOLID

---

## 🚀 Installation

> ℹ️ **Les prérequis sont listés en haut du document**

### Installation Automatique

Les scripts `setup` installent automatiquement :
- Environnement virtuel Python
- Dépendances backend (pip)
- Base de données PostgreSQL
- Migrations Alembic
- Dépendances frontend (npm)
- Fichiers `.env`

```powershell
# Windows PowerShell
.\setup.ps1

# Windows CMD
setup.bat

# Linux/macOS
./setup.sh
```

### Installation Manuelle

<details>
<summary>Cliquez pour voir les étapes manuelles</summary>

#### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Redis
```bash
docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest
```
</details>

---

## 🔧 Configuration

### Backend (.env)

```env
# Base de données
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cryptotracker

# JWT
SECRET_KEY=votre-clé-secrète-32-caractères-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Cache TTL (secondes)
PRICES_TTL=120      # 2 minutes
SEARCH_TTL=600      # 10 minutes
HISTORY_TTL=600     # 10 minutes
DETAIL_TTL=300      # 5 minutes

# CORS
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## 📚 API Documentation

**Swagger UI** : http://localhost:8000/api/docs  
**ReDoc** : http://localhost:8000/api/redoc

### Endpoints Principaux

```
# Authentification
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

# Utilisateur
GET    /api/user/data
POST   /api/user/coins
DELETE /api/user/coins/{id}
PUT    /api/user/coins/reorder

# Alertes
POST   /api/user/alerts
PUT    /api/user/alerts/{id}
DELETE /api/user/alerts/{id}

# Prix Cryptos
GET    /api/prices
GET    /api/search
GET    /api/history/{coin_id}
GET    /api/detail/{coin_id}

# Portfolio
GET    /api/holdings/
POST   /api/holdings/
PUT    /api/holdings/{id}
DELETE /api/holdings/{id}
GET    /api/holdings/summary
```

---

## 🧪 Tests

### Exécution Rapide

```bash
# Tests complets
python run_all_tests.py

# Tests rapides (sans intégration)
python run_all_tests.py --fast

# Tests avec couverture
python run_all_tests.py --fast --coverage
```

### Tests Unitaires Backend

```bash
cd backend
pytest -v                                    # Tests simples
pytest -v --cov=. --cov-report=html         # Avec couverture
pytest tests/unit/routers/test_auth.py -v   # Module spécifique
```

**Couverture actuelle** : 86.34% (voir `backend/htmlcov/index.html`)

### Structure des Tests

```
tests/                  # Tests de validation
├── test_corrections.py
├── test_middlewares.py
└── test_integration.py

backend/tests/          # Tests unitaires
└── unit/
    ├── core/
    ├── routers/
    └── services/
```

---

## 🎯 Fonctionnalités

### Utilisateur
✅ Inscription / Connexion (JWT)  
✅ Gestion du profil

### Watchlist
✅ Recherche de cryptos  
✅ Ajout/suppression  
✅ Drag & drop  
✅ Prix en temps réel

### Alertes
✅ Alertes de prix (haute/basse)  
✅ Notifications visuelles  
✅ Gestion des alertes

### Portfolio
✅ Ajout d'investissements  
✅ Calcul gains/pertes  
✅ Statistiques  
✅ Historique des prix

### Interface
✅ Mode sombre/clair  
✅ Multilingue (FR/EN)  
✅ Design responsive  
✅ Animations fluides

---

## 🔒 Sécurité

- **JWT** : Tokens avec expiration (24h)
- **Bcrypt** : Hachage des mots de passe (12 rounds)
- **CORS** : Origines autorisées configurées
- **Validation** : Pydantic valide toutes les entrées
- **SQL Injection** : Protection via SQLAlchemy ORM
- **Rate Limiting** : Cache Redis pour éviter 429 CoinGecko
- **Variables d'environnement** : Secrets dans `.env`

---

## 📊 Performance

### Cache Redis
- **Stratégie** : Cache-Aside + Stale-While-Revalidate
- **TTL Optimisés** : 2-10 minutes selon volatilité
- **Résultat** : 60-80% réduction appels API
- **Fallback** : Mode dégradé si Redis indisponible

### Optimisations
- ✅ Requêtes DB optimisées (eager loading, indexes)
- ✅ TanStack Query (cache client)
- ✅ Debounce recherche (400ms)
- ✅ Lazy loading composants
- ✅ Code splitting (Vite)

---

## 🐛 Dépannage

### "429 Too Many Requests" (CoinGecko)

**Cause** : Redis non démarré → pas de cache → rate limit

**Solution** :
```bash
# Vérifier Redis
redis-cli ping  # Doit retourner PONG

# Démarrer Redis
docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest

# Redémarrer le backend
```

### "Port 8000 already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### "Module 'redis' not found"

```bash
cd backend
pip install redis==5.2.1
```

### "CORS error"

Vérifier `ALLOWED_ORIGINS` dans `backend/.env`

---

## 📝 Scripts Utiles

### Scripts Automatiques

```powershell
# Windows PowerShell
.\setup.ps1          # Installation complète
.\start.ps1          # Démarrage (Redis + Backend + Frontend)

# Windows CMD
setup.bat
start.bat
check-redis.bat      # Vérifier/démarrer Redis

# Linux/macOS
./setup.sh
./start.sh
./check-redis.sh
```

### Backend

```bash
cd backend
.venv\Scripts\activate              # Activer venv (Windows)
source .venv/bin/activate           # Activer venv (Linux/Mac)
uvicorn main:app --reload           # Démarrer serveur
pytest tests/ -v                    # Tests
alembic upgrade head                # Migrations
```

### Frontend

```bash
cd frontend
npm run dev         # Serveur dev
npm run build       # Build production
npm run lint        # Linting
```

### Redis

```bash
docker start cryptotracker-redis    # Démarrer
docker stop cryptotracker-redis     # Arrêter
docker logs cryptotracker-redis     # Logs
redis-cli ping                      # Vérifier connexion
redis-cli KEYS *                    # Voir cache
```

---

## 🚀 Déploiement

### Backend (Production)

```bash
pip install -r requirements.txt
export SECRET_KEY="votre-clé-forte"
export DATABASE_URL="postgresql://..."
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (Production)

```bash
npm run build
# Déployer le dossier dist/ (Vercel, Netlify, etc.)
```

**Version** : 3.1.0  
**Date** : 2026-04-24  
**Status** : ✅ Production Ready

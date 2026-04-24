# 🚀 CryptoTracker - Application de Suivi de Cryptomonnaies

Application full-stack moderne pour suivre les prix des cryptomonnaies, gérer un portfolio et configurer des alertes de prix.

## ⚡ Démarrage Ultra-Rapide

```bash
# Installation (première fois)
.\setup.bat

# Démarrage
.\start.bat
```

Ouvrez http://localhost:5173 dans votre navigateur.

> 💡 **Prérequis** : Docker Desktop → https://www.docker.com/products/docker-desktop/

---

## 📋 Table des Matières

- [Stack Technique](#-stack-technique)
- [Architecture](#️-architecture)
- [Installation et Démarrage](#-installation-et-démarrage)
  - [Démarrage Rapide](#-démarrage-rapide-un-seul-script)
  - [Installation Manuelle](#installation-manuelle)
- [Configuration](#-configuration)
- [Logs et Débogage](#-logs-et-débogage)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)
- [Fonctionnalités](#-fonctionnalités)
- [Sécurité](#-sécurité)
- [Performance](#-performance)
- [Dépannage](#-dépannage)
- [Scripts Utiles](#-scripts-utiles)
- [Déploiement](#-déploiement)

---

## 📋 Stack Technique

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM + SQLite
- Redis (cache distribué avec fallback)
- JWT (authentification)
- CoinGecko API

**Frontend:**
- React 18 + Vite
- Tailwind CSS + Radix UI
- Context API (state management)
- Axios (HTTP client)

## 🏗️ Architecture

### Backend - Architecture en Couches

```
Controllers (Routers) → Services → Database
     ↓                      ↓          ↓
  FastAPI            CoinGeckoService  SQLAlchemy
```

**Structure:**
```
backend/
├── main.py                 # Point d'entrée
├── config.py               # Configuration centralisée
├── database.py             # Setup SQLAlchemy
├── models.py               # Modèles ORM
├── schemas.py              # Schémas Pydantic
├── core/                   # Infrastructure
│   ├── cache.py           # Cache Redis avec fallback
│   ├── security.py        # JWT + Bcrypt
│   └── exceptions.py      # Exceptions personnalisées
├── services/              # Business Logic
│   └── coingecko_service.py
└── routers/               # Controllers REST
    ├── auth.py            # Authentification
    ├── user.py            # Données utilisateur
    ├── coingecko.py       # Prix cryptos
    └── holdings.py        # Portfolio
```

### Bonnes Pratiques Implémentées

✅ **Dependency Injection** : FastAPI Depends pour auth, DB, validation  
✅ **Service Layer Pattern** : Logique métier isolée et réutilisable  
✅ **Cache Redis** : Réduction 60-80% des appels API avec fallback gracieux  
✅ **Validation Pydantic** : Schémas avec validation automatique  
✅ **Sécurité** : JWT + Bcrypt + CORS configuré  
✅ **Gestion Erreurs** : Exceptions centralisées avec codes HTTP appropriés  
✅ **Tests Unitaires** : Pytest avec fixtures et mocks  
✅ **Migrations DB** : Alembic pour versioning du schéma  
✅ **Principes SOLID** : Séparation des responsabilités

## 🚀 Installation et Démarrage

### 🎯 Démarrage Rapide

**Installation**
```bash
# Windows
.\setup.bat

# Linux/macOS
chmod +x setup.sh && ./setup.sh
```

**Démarrage**
```bash
# Windows
.\start.bat

# Linux/macOS
chmod +x start.sh && ./start.sh
```

Le script démarre automatiquement :
1. 🔴 Redis (Docker, conteneur `cryptotracker-redis`)
2. 🐍 Backend (FastAPI, port 8000)
3. ⚛️ Frontend (Vite, port 5173)

Ouvrez **http://localhost:5173** dans votre navigateur.

> 💡 Les fenêtres Backend et Frontend peuvent être minimisées dans la barre des tâches.

> ⚠️ **Si les fenêtres ne s'ouvrent pas**, lancez manuellement :
> ```bash
> # Terminal 1
> cd backend && .venv\Scripts\activate && uvicorn main:app --reload
>
> # Terminal 2
> cd frontend && npm run dev
> ```

---

## 🛑 Arrêter l'Application

### Option 1 : Arrêt Simple (Backend + Frontend)
Fermez les 2 fenêtres de terminal :
- **"CryptoTracker Backend"**
- **"CryptoTracker Frontend"**

Redis continue de tourner en arrière-plan (pas de problème).

### Option 2 : Arrêt Complet (avec Redis)
```bash
# 1. Fermer les fenêtres Backend et Frontend
# 2. Arrêter Redis
docker stop cryptotracker-redis
```

### Option 3 : Arrêt Forcé (si les fenêtres sont introuvables)
```bash
# Tuer le backend (port 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Tuer le frontend (port 5173)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Arrêter Redis
docker stop cryptotracker-redis
```

---

## 📋 Logs et Débogage

### 1️⃣ Logs en Temps Réel (Fenêtres de Terminal)

Quand vous lancez `start.bat`, **2 fenêtres de terminal s'ouvrent** :

#### Fenêtre "CryptoTracker Backend"
- Logs du serveur FastAPI
- Requêtes HTTP (GET, POST, PUT, DELETE)
- Erreurs backend et stack traces
- Connexion Redis (`Redis connected successfully` ou `Redis connection failed`)
- Logs applicatifs (niveau INFO par défaut)

#### Fenêtre "CryptoTracker Frontend"
- Logs du serveur Vite
- Compilation des composants React
- Hot Module Replacement (HMR)
- Erreurs de build et warnings ESLint

**💡 Astuce** : Si vous ne voyez pas ces fenêtres, vérifiez la barre des tâches Windows. Elles peuvent être minimisées.

### 2️⃣ Logs Redis (Docker)

```bash
# Voir les logs du conteneur Redis
docker logs cryptotracker-redis

# Suivre les logs en temps réel
docker logs -f cryptotracker-redis

# Vérifier que Redis fonctionne
redis-cli ping
# Devrait retourner : PONG
```

### 3️⃣ Logs de la Console Navigateur

Ouvrez les **DevTools** (F12) :
- **Console** : Logs JavaScript, erreurs frontend, requêtes API
- **Network** : Requêtes HTTP vers le backend, codes de réponse, temps de réponse

### 4️⃣ Niveau de Logs (Configuration)

Dans `backend/.env`, ajustez le niveau de logs :

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

- **DEBUG** : Tous les détails (requêtes SQL, cache Redis, etc.)
- **INFO** : Informations importantes (démarrage, connexions, requêtes API)
- **WARNING** : Avertissements uniquement
- **ERROR** : Erreurs uniquement

### 5️⃣ Logs Persistants (Optionnel)

Pour sauvegarder les logs dans des fichiers :

```bash
# Backend
cd backend
.venv\Scripts\activate
uvicorn main:app --reload > logs_backend.txt 2>&1

# Frontend
cd frontend
npm run dev > logs_frontend.txt 2>&1
```

### 6️⃣ Vérifier les Services en Cours

```bash
# Vérifier le backend (port 8000)
netstat -ano | findstr :8000

# Vérifier le frontend (port 5173)
netstat -ano | findstr :5173

# Vérifier Redis (port 6379)
netstat -ano | findstr :6379
redis-cli ping
```

---

### 📦 Installation Initiale (setup.bat / setup.sh)

**Ces scripts effectuent automatiquement :**
1. ✅ Vérification des prérequis (Python, Node.js, PostgreSQL)
2. ✅ Création de l'environnement virtuel Python
3. ✅ Installation des dépendances backend (pip)
4. ✅ Création du fichier `.env` depuis `.env.example`
5. ✅ Création de la base de données PostgreSQL
6. ✅ Application des migrations Alembic
7. ✅ Installation des dépendances frontend (npm)
8. ✅ Configuration complète en une seule commande

**Note** : Docker Desktop doit être installé pour Redis. Si absent, téléchargez-le depuis https://www.docker.com/products/docker-desktop/

---

### Installation Manuelle

Si vous préférez installer manuellement ou si les scripts automatiques échouent :

#### Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis (optionnel mais recommandé)

#### 1. Backend

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env (copier depuis .env.example)
cp .env.example .env

# Appliquer les migrations
alembic upgrade head

# Démarrer le serveur
uvicorn main:app --reload
```

Le backend démarre sur **http://localhost:8000**

### 2. Frontend

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

Le frontend démarre sur **http://localhost:5173**

### 3. Redis (FORTEMENT RECOMMANDÉ)

⚠️ **IMPORTANT** : Sans Redis, vous risquez d'atteindre rapidement la limite de requêtes de l'API CoinGecko (429 Too Many Requests).

**Script automatique (recommandé)** :
```bash
# Windows
check-redis.bat

# Linux/macOS
chmod +x check-redis.sh
./check-redis.sh
```

Ce script vérifie si Redis est démarré et le lance automatiquement avec Docker si nécessaire.

**Démarrage manuel** :
```bash
# Avec Docker (recommandé - fonctionne sur tous les OS)
docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest

# Linux
sudo apt install redis-server
redis-server

# macOS
brew install redis
redis-server

# Windows (natif)
# Télécharger depuis https://github.com/microsoftarchive/redis/releases
```

**Vérifier que Redis fonctionne** :
```bash
redis-cli ping
# Devrait retourner : PONG
```

**Logs backend** : Au démarrage, vous devriez voir :
- ✅ `Redis connected successfully` → Cache actif, pas de problème de rate limit
- ❌ `Redis connection failed` → Mode dégradé, risque de 429 Too Many Requests

## 🔧 Configuration

### Variables d'Environnement Backend (.env)

Le fichier `backend/.env` est créé automatiquement par `setup.bat` depuis `backend/.env.example`.

```env
# ── Base de données PostgreSQL ────────────────────────────────────────
# IMPORTANT: Créer la base de données avant de lancer les migrations:
# psql -U postgres -c "CREATE DATABASE cryptotracker;"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cryptotracker

# ── Authentification JWT ──────────────────────────────────────────────
# IMPORTANT: Générer une vraie clé secrète avec: openssl rand -hex 32
SECRET_KEY=109f0634b5fabe6f89f791afa0d406e73eff4d44737f2039ca1d934e5df4b094
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 heures

# ── Redis Cache ───────────────────────────────────────────────────────
# IMPORTANT: Redis doit être installé et démarré avant de lancer l'application
# Utiliser Docker: docker run -d -p 6379:6379 redis:latest
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=  # Décommenter si Redis nécessite un mot de passe
REDIS_SOCKET_TIMEOUT=5.0
REDIS_SOCKET_CONNECT_TIMEOUT=5.0

# ── CoinGecko API ─────────────────────────────────────────────────────
COINGECKO_URL=https://api.coingecko.com/api/v3
API_TIMEOUT=10.0
DETAIL_TIMEOUT=15.0

# ── Cache TTL (Time To Live en secondes) ──────────────────────────────
# TTL augmentés pour réduire drastiquement les appels à CoinGecko
PRICES_TTL=120     # 2 minutes (au lieu de 30s)
SEARCH_TTL=600     # 10 minutes (au lieu de 5min)
HISTORY_TTL=600    # 10 minutes (au lieu de 5min)
DETAIL_TTL=300     # 5 minutes (au lieu de 2min)

# ── CORS ──────────────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:5173

# ── Logging ───────────────────────────────────────────────────────────
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Variables d'Environnement Frontend (.env)

Le fichier `frontend/.env` est optionnel. Par défaut, le frontend utilise `http://localhost:8000`.

```env
# URL de l'API backend
VITE_API_URL=http://localhost:8000
```

### Configuration Avancée

#### Backend (`backend/config.py`)
Toutes les configurations sont centralisées dans `config.py` avec Pydantic Settings :
- Validation automatique des types
- Valeurs par défaut
- Documentation intégrée

#### Frontend (`frontend/src/config.js`)
Constantes de l'application :
- `API_BASE_URL` : URL du backend
- `REFRESH_INTERVAL` : Intervalle de rafraîchissement (60s)
- `DEBOUNCE_MS` : Délai de debounce pour la recherche (400ms)
- `STALE_TIME` : Durées de cache pour TanStack Query
- `DEFAULT_COINS` : Coins affichés par défaut (`['bitcoin', 'ethereum', 'solana']`)

## 📚 API Documentation

### Swagger UI

Une fois le backend démarré :
- **Swagger UI** : http://localhost:8000/api/docs
- **ReDoc** : http://localhost:8000/api/redoc

### Endpoints Principaux

```
# Authentification
POST   /api/auth/register       # Inscription
POST   /api/auth/login          # Connexion
GET    /api/auth/me             # Utilisateur actuel

# Données Utilisateur
GET    /api/user/data           # Toutes les données (coins + alertes)
POST   /api/user/coins          # Ajouter un coin
DELETE /api/user/coins/{id}     # Supprimer un coin
PUT    /api/user/coins/reorder  # Réorganiser (drag & drop)

# Alertes
POST   /api/user/alerts         # Créer une alerte
PUT    /api/user/alerts/{id}    # Modifier une alerte
DELETE /api/user/alerts/{id}    # Supprimer une alerte

# Prix Cryptos
GET    /api/prices              # Prix de plusieurs cryptos
GET    /api/search              # Rechercher des cryptos
GET    /api/history/{coin_id}   # Historique des prix
GET    /api/detail/{coin_id}    # Détails d'une crypto

# Portfolio
GET    /api/holdings/           # Liste des holdings
POST   /api/holdings/           # Créer un holding
PUT    /api/holdings/{id}       # Modifier un holding
DELETE /api/holdings/{id}       # Supprimer un holding
GET    /api/holdings/summary    # Résumé du portfolio
```

## 🧪 Tests

Le projet dispose d'une **suite de tests complète** organisée de manière professionnelle.

### 📁 Structure des Tests

```
tests/                          # Tests de validation et intégration
├── test_corrections.py         # Tests de sécurité
├── test_middlewares.py         # Tests des middlewares
└── test_integration.py         # Tests end-to-end

backend/tests/                  # Tests unitaires pytest
├── conftest.py                 # Fixtures globales
└── unit/                       # Tests unitaires isolés
    ├── core/                   # Tests des modules core
    ├── routers/                # Tests des endpoints
    └── services/               # Tests des services

run_all_tests.py               # Script orchestrateur
```

### 🚀 Exécution Rapide

#### Script Orchestrateur (RECOMMANDÉ)

Exécute tous les tests dans l'ordre optimal :

```bash
# Tests rapides (sans intégration)
python run_all_tests.py --fast

# Tests complets (avec intégration)
python run_all_tests.py

# Tests avec couverture de code
python run_all_tests.py --fast --coverage
```

**Ce que fait le script** :
1. ✅ Tests de sécurité (requirements, rate limiting, SECRET_KEY)
2. ✅ Tests des middlewares (imports, enregistrement, simplification)
3. ✅ Tests unitaires backend (130 tests avec pytest)
4. ✅ Tests d'intégration (optionnel, nécessite l'app démarrée)

**Résultat** : Rapport final avec statistiques et code de sortie approprié.

---

### 1️⃣ Tests de Sécurité

Valide les corrections de sécurité prioritaires :

```bash
python tests/test_corrections.py
```

**Tests effectués** :
- ✅ Fichier requirements.txt (encodage UTF-8, dépendances)
- ✅ Rate limiting (SlowAPI configuré)
- ✅ SECRET_KEY (longueur sécurisée ≥32 caractères)

---

### 2️⃣ Tests des Middlewares

Valide l'implémentation des middlewares personnalisés :

```bash
python tests/test_middlewares.py
```

**Tests effectués** :
- ✅ Imports des middlewares
- ✅ Chargement de l'application
- ✅ Enregistrement des middlewares (logging, exception, security)
- ✅ Simplification des routers (pas de try/except)
- ✅ Existence des fichiers middleware

---

### 3️⃣ Tests Unitaires Backend

Tests détaillés avec pytest et couverture de code :

```bash
cd backend

# Tests simples
pytest -v

# Tests avec couverture
pytest -v --cov=. --cov-report=html

# Tests d'un module spécifique
pytest tests/unit/routers/test_auth.py -v

# Tests avec markers
pytest -m unit
```

**Modules testés** (130 tests) :
- ✅ **core/cache.py** : Redis, fallback, statistiques
- ✅ **core/security.py** : JWT, Bcrypt, authentification
- ✅ **core/exceptions.py** : Exceptions personnalisées
- ✅ **routers/auth.py** : Inscription, connexion, get_me
- ✅ **routers/user.py** : Coins, alertes, réorganisation
- ✅ **services/coingecko_service.py** : Prix, recherche, historique

**Couverture actuelle** : **86.34%** (visible dans `backend/htmlcov/index.html`)

---

### 4️⃣ Tests d'Intégration

Tests end-to-end de l'application complète :

```bash
# Prérequis : Application démarrée
.\start.bat

# Lancer les tests
python tests/test_integration.py
```

**Tests effectués** :
- ✅ Structure du projet (fichiers et dossiers)
- ✅ Configuration (.env et variables)
- ✅ Connexion Redis (port 6379)
- ✅ Backend API (health check, port 8000)
- ✅ Frontend (accessibilité, port 5173)
- ✅ Endpoints API (inscription, connexion, prix, recherche)
- ✅ Scripts de démarrage (setup.bat, start.bat, check-redis.bat)

**Résultat** : Rapport détaillé avec suggestions de correction.

---

### 📊 Rapport de Couverture de Code

Après avoir exécuté les tests unitaires avec couverture :

```bash
cd backend
pytest --cov=. --cov-report=html
```

Ouvrez `backend/htmlcov/index.html` pour voir :
- **Pourcentage de couverture** par fichier (objectif : 80%+)
- **Lignes testées** (en vert)
- **Lignes non testées** (en rouge)
- **Branches non couvertes**

**Configuration** : Voir `backend/.coveragerc` pour personnaliser la couverture.

---

### 🎯 Quand Exécuter les Tests

**Développement quotidien** :
```bash
cd backend && pytest        # Tests unitaires rapides
```

**Avant un commit** :
```bash
python run_all_tests.py --fast --coverage
```

**Avant un déploiement** :
```bash
python run_all_tests.py     # Tous les tests
```

**Après modification des middlewares** :
```bash
python tests/test_middlewares.py
```

**Après modification de la sécurité** :
```bash
python tests/test_corrections.py
```

## 🎯 Fonctionnalités

### Utilisateur
- ✅ Inscription / Connexion sécurisée (JWT)
- ✅ Gestion du profil

### Watchlist
- ✅ Recherche de cryptomonnaies
- ✅ Ajout/suppression de cryptos
- ✅ Réorganisation par drag & drop
- ✅ Affichage des prix en temps réel

### Alertes
- ✅ Alertes de prix (haute/basse)
- ✅ Notifications visuelles
- ✅ Gestion des alertes

### Portfolio
- ✅ Ajout d'investissements
- ✅ Calcul automatique des gains/pertes
- ✅ Statistiques du portfolio
- ✅ Historique des prix

### Interface
- ✅ Mode sombre/clair
- ✅ Multilingue (FR/EN)
- ✅ Design responsive
- ✅ Animations fluides

## 🔒 Sécurité

- **JWT** : Tokens stateless avec expiration (24 heures par défaut)
- **Bcrypt** : Hachage sécurisé des mots de passe (salt + 12 rounds)
- **CORS** : Configuration stricte des origines autorisées
- **Validation** : Pydantic valide toutes les entrées (types, formats, contraintes)
- **SQL Injection** : Protection via SQLAlchemy ORM (requêtes paramétrées)
- **Rate Limiting** : Gestion des erreurs 429 de CoinGecko avec cache Redis
- **Variables d'environnement** : Secrets stockés dans `.env` (non versionné)
- **HTTPS** : Recommandé en production

## 📊 Performance

### Cache Redis
- **Stratégie** : Cache-Aside + Stale-While-Revalidate
- **TTL Différenciés** (optimisés pour éviter le rate limit) :
  - Prix : 2 minutes (120s) - données volatiles
  - Recherche : 10 minutes (600s) - stable
  - Historique : 10 minutes (600s) - stable
  - Détails : 5 minutes (300s) - moyennement volatile
- **Résultat** : Réduction 60-80% des appels API CoinGecko
- **Fallback** : Mode dégradé si Redis indisponible (données périmées acceptées)

### Optimisations Backend
- ✅ Requêtes DB optimisées (eager loading, indexes)
- ✅ Pagination prête (pour grandes listes)
- ✅ Fallback gracieux (données périmées si erreur API)
- ✅ Gestion des timeouts (10s API, 15s détails)
- ✅ Connection pooling (SQLAlchemy)
- ✅ Async/await pour I/O non-bloquant

### Optimisations Frontend
- ✅ TanStack Query pour le cache client
- ✅ Debounce sur la recherche (400ms)
- ✅ Lazy loading des composants
- ✅ Optimistic updates (UI réactive)
- ✅ Code splitting avec Vite

## 🐛 Dépannage

### ⚠️ "429 Too Many Requests" (CoinGecko Rate Limit)

**Symptôme** : Message d'erreur "Too many requests" dans le frontend, même sans manipulation.

**Cause** : Redis n'est pas démarré → pas de cache → chaque requête va directement à CoinGecko → rate limit atteint rapidement.

**Solution** :

1. **Vérifier si Redis est démarré** :
   ```bash
   redis-cli ping
   # Devrait retourner : PONG
   ```

2. **Si Redis n'est pas démarré, utiliser le script automatique** :
   ```bash
   # Windows
   check-redis.bat
   
   # Linux/macOS
   ./check-redis.sh
   ```

3. **Redémarrer le backend** et vérifier les logs :
   - ✅ `Redis connected successfully` → Problème résolu
   - ❌ `Redis connection failed` → Vérifier que Redis écoute sur le port 6379

4. **Vérifier le cache fonctionne** :
   ```bash
   # Dans un autre terminal
   redis-cli
   > KEYS *
   # Devrait afficher les clés de cache après quelques requêtes
   ```

**TTL du cache** (configuré pour éviter le rate limit) :
- Prix : 2 minutes (120s)
- Recherche : 10 minutes
- Historique : 10 minutes
- Détails : 5 minutes

### "Module 'redis' not found"
```bash
cd backend
pip install redis==5.2.1
```

### "Redis connection failed"
**Sans Redis** : L'application fonctionne en mode dégradé mais vous risquez d'atteindre le rate limit CoinGecko.
**Solution** : Démarrer Redis avec `check-redis.bat` (Windows) ou `./check-redis.sh` (Linux/macOS).

### "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### "CORS error"
Vérifier que `ALLOWED_ORIGINS` dans `.env` inclut l'URL du frontend.

## 📖 Patterns de Conception

- **Singleton** : Instance unique du service CoinGecko
- **Repository** : Abstraction de l'accès aux données (SQLAlchemy)
- **Factory** : Création d'objets complexes (tokens, liens)
- **Strategy** : Différentes stratégies de cache
- **Decorator** : Décorateurs FastAPI (@router, @Depends)

## 🎓 Principes SOLID

- **S** : Single Responsibility (chaque classe = 1 responsabilité)
- **O** : Open/Closed (extension sans modification)
- **L** : Liskov Substitution (sous-types remplaçables)
- **I** : Interface Segregation (interfaces spécifiques)
- **D** : Dependency Inversion (dépendre d'abstractions)

## 📝 Scripts Utiles

### Scripts Automatiques (Recommandés)

```bash
# Installation complète (première fois)
.\setup.bat          # Windows
./setup.sh           # Linux/macOS

# Démarrage complet (Redis + Backend + Frontend)
.\start.bat          # Windows
./start.sh           # Linux/macOS

# Vérifier et démarrer Redis
.\check-redis.bat    # Windows
./check-redis.sh     # Linux/macOS
```

### Scripts Manuels

#### Backend
```bash
cd backend

# Activer l'environnement virtuel
.venv\Scripts\activate              # Windows
source .venv/bin/activate           # Linux/macOS

# Démarrer le serveur
uvicorn main:app --reload --port 8000

# Tests
pytest tests/ -v                    # Tests unitaires
pytest tests/ -v --cov=. --cov-report=html  # Avec couverture
python test_functional.py           # Tests fonctionnels (si disponible)

# Migrations de base de données
alembic revision --autogenerate -m "Description"  # Créer une migration
alembic upgrade head                              # Appliquer les migrations
alembic downgrade -1                              # Annuler la dernière migration
alembic history                                   # Voir l'historique

# Dépendances
pip install -r requirements.txt     # Installer les dépendances
pip freeze > requirements.txt       # Mettre à jour requirements.txt
```

#### Frontend
```bash
cd frontend

# Démarrer le serveur de développement
npm run dev                         # Port 5173

# Build
npm run build                       # Build de production (dossier dist/)
npm run preview                     # Prévisualiser le build

# Linting
npm run lint                        # Vérifier le code avec ESLint

# Dépendances
npm install                         # Installer les dépendances
npm update                          # Mettre à jour les dépendances
```

#### Redis
```bash
# Démarrer Redis avec Docker
docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest

# Gérer le conteneur
docker start cryptotracker-redis    # Démarrer
docker stop cryptotracker-redis     # Arrêter
docker restart cryptotracker-redis  # Redémarrer
docker rm cryptotracker-redis       # Supprimer

# Logs et monitoring
docker logs cryptotracker-redis     # Voir les logs
docker logs -f cryptotracker-redis  # Suivre les logs en temps réel
redis-cli ping                      # Vérifier la connexion
redis-cli info                      # Informations sur Redis
redis-cli KEYS *                    # Voir toutes les clés en cache
redis-cli FLUSHALL                  # Vider tout le cache (attention !)
```

#### Base de données PostgreSQL
```bash
# Créer la base de données
psql -U postgres -c "CREATE DATABASE cryptotracker;"

# Se connecter à la base
psql -U postgres -d cryptotracker

# Supprimer la base (attention !)
psql -U postgres -c "DROP DATABASE cryptotracker;"

# Backup
pg_dump -U postgres cryptotracker > backup.sql

# Restore
psql -U postgres cryptotracker < backup.sql
```

## 🚀 Déploiement

### Backend (Production)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Variables d'environnement
export SECRET_KEY="votre-clé-secrète-forte"
export DATABASE_URL="postgresql://..."  # PostgreSQL recommandé
export REDIS_HOST="votre-redis-host"

# Démarrer avec Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (Production)

```bash
# Build
npm run build

# Déployer le dossier dist/ sur votre hébergeur
# (Vercel, Netlify, etc.)
```

## 📄 Licence

Ce projet est un projet éducatif.

## 👤 Auteur

Projet CryptoTracker - Formation IBM CIC

---

**Version** : 3.0.0  
**Date** : 2026-04-24  
**Status** : ✅ Production Ready

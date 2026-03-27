# 🚀 CryptoTracker

> Application full-stack de suivi de cryptomonnaies en temps réel avec authentification, alertes de prix, drag & drop et graphiques interactifs.

![Version](https://img.shields.io/badge/version-3.0.0-6C63FF)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![MUI](https://img.shields.io/badge/MUI-7-007FFF?logo=mui)

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Stack technique](#-stack-technique)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Lancer l'application](#-lancer-lapplication)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Structure du projet](#-structure-du-projet)
- [Dépannage](#-dépannage)

---

## 🎯 Vue d'ensemble

CryptoTracker est une application full-stack moderne permettant de suivre les prix de cryptomonnaies en temps réel avec :

- **🔐 Authentification sécurisée** : Comptes utilisateurs avec JWT et bcrypt
- **💾 Persistance PostgreSQL** : Toutes vos données sauvegardées en base de données
- **📊 Dashboard personnalisable** : Ajoutez/supprimez des coins, réorganisez par drag & drop
- **🔔 Alertes de prix** : Notifications quand un seuil est franchi (haut ↑ ou bas ↓)
- **📈 Graphiques historiques** : Visualisez l'évolution sur 7/14/30/90 jours
- **📉 Métriques détaillées** : Market cap, volume, ATH, supply, sentiment communautaire
- **🔄 Synchronisation multi-appareils** : Accédez à vos données depuis n'importe où

### Pourquoi un backend ?

Le backend FastAPI sert de proxy intelligent entre le frontend et l'API CoinGecko :
1. **Normalise** les réponses (200+ champs → données utiles uniquement)
2. **Cache** les résultats (réduit les appels API, évite les rate limits)
3. **Protège** contre les erreurs réseau avec retry et fallback
4. **Authentifie** les utilisateurs et gère leurs données personnelles

---

## ✨ Fonctionnalités

### 🔐 Authentification

- **Inscription** : Création de compte avec email et mot de passe
- **Connexion** : Authentification JWT avec token valide 24h
- **Sécurité** : Mots de passe hachés avec bcrypt (12 rounds)
- **Protection** : Routes protégées nécessitant un token valide

### 📊 Dashboard principal

#### 🔄 Suivi en temps réel
- Prix en USD avec variation 24h (vert/rouge)
- Market cap formaté (T/B/M)
- Refresh automatique toutes les 60s avec barre de progression
- Refresh manuel via bouton

#### 🔍 Recherche de coins
- Barre de recherche avec debounce 400ms
- Dropdown avec 6 résultats max
- Détection des coins déjà ajoutés (badge "Déjà ajouté")
- Ajout instantané au clic

#### 🎯 Drag & drop
- Réorganisation des cartes par glisser-déposer
- Handle `⠿` dédié (les boutons restent cliquables)
- Carte fantôme stylisée (rotation + ombre violette)
- Seuil d'activation 8px (distingue clic et drag)
- **Sauvegarde automatique** de l'ordre en base de données

#### 🔔 Alertes de prix
- Configuration via icône cloche sur chaque carte
- Seuil haut ↑ et bas ↓ indépendants
- **Persistance en base de données** (synchronisé entre appareils)
- Notification toast au franchissement du seuil
- Détection intelligente : alerte uniquement au **franchissement**

#### ❌ Suppression
- Chip `✕` en haut à droite de chaque carte
- Suppression immédiate avec mise à jour optimiste
- Suppression en base de données

### 📈 Page détail

#### 📊 Graphique interactif
- Graphique en aire avec Recharts
- Sélecteur de période : 7 / 14 / 30 / 90 jours
- Tooltip au survol avec prix et date
- Gradient violet pour l'identité visuelle

#### 📉 Métriques complètes
- **Prix actuel** avec variation 24h
- **Market cap** et fully diluted valuation
- **Volume 24h** et variations (24h / 7j / 30j)
- **ATH** (All-Time High) avec % de distance
- **Supply** : circulante / totale / max
- **Sentiment communautaire** : barre haussier/baissier

---

## 🛠️ Stack technique

### Frontend

| Technologie | Version | Rôle |
|-------------|---------|------|
| **React** | 19.2 | Bibliothèque UI avec hooks |
| **Vite** | 8.0 | Build tool ultra-rapide |
| **Material UI** | 7.3 | Composants UI (Card, Dialog, Snackbar...) |
| **TanStack Query** | 5.95 | Server state management (cache, retry) |
| **React Router** | 7.13 | Navigation multi-pages |
| **dnd-kit** | 6.3 | Drag & drop accessible |
| **Recharts** | 3.8 | Graphiques React |
| **Axios** | 1.13 | Client HTTP |

### Backend

| Technologie | Version | Rôle |
|-------------|---------|------|
| **FastAPI** | 0.135 | Framework web Python async |
| **PostgreSQL** | 16+ | Base de données relationnelle |
| **SQLAlchemy** | 2.0 | ORM Python |
| **Alembic** | 1.14 | Migrations de base de données |
| **Uvicorn** | 0.42 | Serveur ASGI |
| **python-jose** | 3.3 | Génération et validation JWT |
| **passlib** | 1.7.4 | Hachage bcrypt |
| **bcrypt** | 4.0.1 | Algorithme de hachage |

### API externe

| Service | Rôle |
|---------|------|
| **CoinGecko API v3** | Prix, market cap, historique (gratuit, sans clé) |

---

## 📦 Installation

### Prérequis

- **Node.js** ≥ 18 ([télécharger](https://nodejs.org/))
- **Python** ≥ 3.10 ([télécharger](https://www.python.org/downloads/))
- **PostgreSQL** ≥ 14 ([télécharger](https://www.postgresql.org/download/))
- **npm** ≥ 9

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd cryptotracker
```

### 2. Installer PostgreSQL

#### Windows

1. Télécharger depuis https://www.postgresql.org/download/windows/
2. Lancer l'installeur (garder les paramètres par défaut)
3. **Noter le mot de passe** choisi pour l'utilisateur `postgres`
4. Port par défaut : `5432`

#### Mac

```bash
brew install postgresql@16
brew services start postgresql@16
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 3. Créer la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE cryptotracker;

# Vérifier la création
\l

# Quitter
\q
```

### 4. Installer les dépendances Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows :
.venv\Scripts\activate
# Mac/Linux :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 5. Installer les dépendances Frontend

```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

### Backend

1. **Éditer le fichier `.env`**

```env
# Base de données PostgreSQL
# Remplacer 'password' par VOTRE mot de passe PostgreSQL
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/cryptotracker

# Clé secrète JWT (générer une clé sécurisée)
SECRET_KEY=votre-cle-secrete-generee

# Configuration JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API CoinGecko
COINGECKO_URL=https://api.coingecko.com/api/v3

# CORS (origines autorisées)
ALLOWED_ORIGINS=http://localhost:5173
```

2. **Générer une clé secrète sécurisée**

```bash
# Générer une clé aléatoire de 64 caractères
python -c "import secrets; print(secrets.token_hex(32))"
```

Copier le résultat et le coller dans `SECRET_KEY` du fichier `.env`.

4. **Créer les tables de la base de données**

```bash
cd backend

# Activer l'environnement virtuel si ce n'est pas déjà fait
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Générer la migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer la migration (créer les tables)
alembic upgrade head
```

5. **Vérifier que les tables sont créées**

```bash
psql -U postgres -d cryptotracker -c "\dt"
```

Vous devriez voir :
```
             List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | user_alerts     | table | postgres
 public | user_coins      | table | postgres
 public | users           | table | postgres
```

### Frontend

1. **Le fichier `.env` devrait contenir**

```env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Lancer l'application

### Terminal 1 : Backend

```bash
cd backend

# Activer l'environnement virtuel
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Démarrer le serveur
uvicorn main:app --reload --port 8000
```

### Terminal 2 : Frontend

```bash
cd frontend

# Démarrer le serveur de développement
npm run dev
```

### Accéder à l'application

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost:5173 | Interface utilisateur |
| **API Backend** | http://localhost:8000 | API REST |
| **Documentation API** | http://localhost:8000/docs | Swagger UI interactif |
| **Cache Stats** | http://localhost:8000/api/cache/stats | Monitoring du cache |

---

## 🧪 Premier lancement

### 1. Créer un compte

1. Ouvrir http://localhost:5173
2. Vous serez redirigé vers `/login`
3. Cliquer sur **"S'inscrire"**
4. Remplir le formulaire :
   - Email : `test@example.com`
   - Mot de passe : `password123` (min 8 caractères)
   - Confirmer le mot de passe
5. Cliquer sur **"S'inscrire"**

### 2. Ajouter des cryptomonnaies

1. Utiliser la barre de recherche en haut
2. Taper "bitcoin" (attendre 400ms pour le debounce)
3. Cliquer sur **"Bitcoin"** dans les résultats
4. Une carte Bitcoin apparaît avec le prix en temps réel
5. Répéter pour d'autres coins : "ethereum", "solana", "cardano"...

### 3. Configurer des alertes

1. Cliquer sur l'icône **🔔** sur une carte
2. Configurer une alerte haute :
   - Seuil haut : `70000`
   - Cliquer sur **"Enregistrer"**
3. Configurer une alerte basse :
   - Seuil bas : `60000`
   - Cliquer sur **"Enregistrer"**

### 4. Réorganiser les cartes

1. Cliquer et maintenir sur l'icône **⠿** (handle) d'une carte
2. Glisser-déposer pour changer l'ordre
3. Relâcher

### 5. Voir les détails d'un coin

1. Cliquer sur une carte (pas sur les boutons)
2. Vous êtes redirigé vers `/coin/bitcoin`
3. Voir le graphique historique et les métriques détaillées
4. Cliquer sur **"← Retour"** pour revenir au dashboard

---

## 🏗️ Architecture

### Modèle de données

#### Table `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Table `user_coins`
```sql
CREATE TABLE user_coins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    coin_id VARCHAR(50) NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, coin_id)
);
```

#### Table `user_alerts`
```sql
CREATE TABLE user_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    coin_id VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('high', 'low')),
    threshold FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, coin_id, type)
);
```

### Flux d'authentification

```
1. Inscription (POST /api/auth/register)
   ├─ Validation email + mot de passe (min 8 caractères)
   ├─ Hash du mot de passe avec bcrypt (12 rounds)
   └─ Création de l'utilisateur en base

2. Connexion (POST /api/auth/login)
   ├─ Vérification email + mot de passe
   ├─ Génération d'un token JWT signé avec HS256
   └─ Retour du token (valide 24h par défaut)

3. Requêtes protégées
   ├─ Header: Authorization: Bearer <token>
   ├─ Décodage du token JWT
   ├─ Extraction de l'email
   ├─ Récupération de l'utilisateur en base
   └─ Injection dans la dépendance get_current_user
```

### Flux de données

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVIGATEUR                              │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   App.jsx    │───▶│ useCrypto    │───▶│  TanStack Query │  │
│  │  (Dashboard) │    │   Prices     │    │   (cache 90s)   │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
│         │                    │                      │           │
│         │                    ▼                      ▼           │
│         │            ┌──────────────┐      ┌──────────────┐    │
│         │            │ usePriceAlerts│      │   Axios      │    │
│         │            │   (backend)   │      │  HTTP Client │    │
│         │            └──────────────┘      └──────────────┘    │
│         │                    │                      │           │
│         ▼                    ▼                      ▼           │
│  ┌──────────────┐    ┌──────────────┐             │           │
│  │ CoinDetail   │    │ AlertToast   │             │           │
│  │   (page)     │    │ (Snackbar)   │             │           │
│  └──────────────┘    └──────────────┘             │           │
└────────────────────────────────────────────────────┼───────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Authentification (JWT + bcrypt)                        │   │
│  │  POST /api/auth/register                                │   │
│  │  POST /api/auth/login                                   │   │
│  │  GET  /api/auth/me                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Données utilisateur (protégées)                        │   │
│  │  GET    /api/user/data                                  │   │
│  │  POST   /api/user/coins                                 │   │
│  │  PUT    /api/user/coins/reorder                         │   │
│  │  DELETE /api/user/coins/{coin_id}                       │   │
│  │  POST   /api/user/alerts                                │   │
│  │  PUT    /api/user/alerts/{alert_id}                     │   │
│  │  DELETE /api/user/alerts/{alert_id}                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Proxy CoinGecko (cache 60s-5min)                       │   │
│  │  GET /api/prices?coins=bitcoin,ethereum                 │   │
│  │  GET /api/search?q=cardano                              │   │
│  │  GET /api/history/bitcoin?days=7                        │   │
│  │  GET /api/detail/bitcoin                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                    │   │
│  │  - users                                                │   │
│  │  - user_coins                                           │   │
│  │  - user_alerts                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┼───────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COINGECKO API (externe)                      │
│                                                                 │
│  • /simple/price        → Prix + market cap + volume           │
│  • /search              → Recherche par nom/symbole            │
│  • /coins/{id}/market_chart → Historique des prix             │
│  • /coins/{id}          → Détails complets du coin             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 API Reference

### Authentification

#### `POST /api/auth/register`
Créer un nouveau compte.

**Body :**
```json
{
  "email": "user@example.com",
  "password": "motdepasse123"
}
```

**Réponse 201 :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-03-25T10:00:00Z"
}
```

---

#### `POST /api/auth/login`
Se connecter et obtenir un token JWT.

**Body (form-data) :**
```
username: user@example.com
password: motdepasse123
```

**Réponse 200 :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### `GET /api/auth/me`
Récupérer les informations de l'utilisateur courant.

**Headers :**
```
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-03-25T10:00:00Z"
}
```

---

### Données utilisateur (protégées)

Tous ces endpoints nécessitent le header `Authorization: Bearer <token>`.

#### `GET /api/user/data`
Récupérer toutes les données utilisateur (coins + alertes).

**Réponse 200 :**
```json
{
  "user": { "id": 1, "email": "user@example.com", ... },
  "coins": [
    { "id": 1, "coin_id": "bitcoin", "position": 0, ... },
    { "id": 2, "coin_id": "ethereum", "position": 1, ... }
  ],
  "alerts": [
    { "id": 1, "coin_id": "bitcoin", "type": "high", "threshold": 70000, ... }
  ]
}
```

---

#### `POST /api/user/coins`
Ajouter un coin à suivre.

**Body :**
```json
{
  "coin_id": "cardano",
  "position": 2
}
```

---

#### `PUT /api/user/coins/reorder`
Réorganiser les coins (après drag & drop).

**Body :**
```json
{
  "coin_ids": ["ethereum", "bitcoin", "cardano"]
}
```

---

#### `DELETE /api/user/coins/{coin_id}`
Supprimer un coin.

---

#### `POST /api/user/alerts`
Créer une alerte de prix.

**Body :**
```json
{
  "coin_id": "bitcoin",
  "type": "high",
  "threshold": 75000
}
```

---

### Proxy CoinGecko

#### `GET /api/prices`
Récupère les prix et métriques pour une liste de coins.

**Query params :**
- `coins` (string) : IDs CoinGecko séparés par virgules

**Cache :** 60s

---

#### `GET /api/search`
Recherche de coins par nom ou symbole.

**Query params :**
- `q` (string) : Terme de recherche (min 2 caractères)

**Cache :** 5 minutes

---

#### `GET /api/history/{coin_id}`
Historique des prix agrégé par jour.

**Query params :**
- `days` (int) : Nombre de jours (7, 14, 30, 90)

**Cache :** 5 minutes

---

#### `GET /api/detail/{coin_id}`
Informations complètes sur un coin.

**Cache :** 2 minutes

---

## 📁 Structure du projet

```
cryptotracker/
├── backend/
│   ├── main.py                 # FastAPI app + endpoints CoinGecko
│   ├── database.py             # Configuration SQLAlchemy
│   ├── models.py               # Modèles (User, UserCoin, UserAlert)
│   ├── schemas.py              # Schémas Pydantic
│   ├── auth.py                 # Authentification JWT + bcrypt
│   ├── routers_auth.py         # Routes d'authentification
│   ├── routers_user.py         # Routes données utilisateur
│   ├── alembic/                # Migrations de base de données
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example
│   └── .venv/
│
└── frontend/
    ├── src/
    │   ├── main.jsx            # Point d'entrée + Router
    │   ├── App.jsx             # Dashboard principal
    │   ├── config.js           # Configuration centralisée
    │   │
    │   ├── pages/
    │   │   ├── Login.jsx       # Page de connexion
    │   │   ├── Register.jsx    # Page d'inscription
    │   │   └── CoinDetail.jsx  # Page détail coin
    │   │
    │   ├── components/
    │   │   ├── Header.jsx              # En-tête avec déconnexion
    │   │   ├── ProtectedRoute.jsx      # Route protégée
    │   │   ├── CryptoCard.jsx          # Carte d'affichage
    │   │   ├── SortableCard.jsx        # Wrapper drag & drop
    │   │   ├── DragOverlayCard.jsx     # Carte fantôme
    │   │   ├── CoinSearch.jsx          # Barre de recherche
    │   │   ├── RefreshBar.jsx          # Barre de progression
    │   │   ├── AlertDialog.jsx         # Dialog alertes
    │   │   ├── AlertToast.jsx          # Notifications
    │   │   └── ErrorBoundary.jsx       # Gestion erreurs
    │   │
    │   ├── contexts/
    │   │   └── AuthContext.jsx         # Contexte d'authentification
    │   │
    │   ├── api/
    │   │   ├── client.js               # Client Axios configuré
    │   │   ├── auth.js                 # API authentification
    │   │   └── user.js                 # API données utilisateur
    │   │
    │   └── hooks/
    │       ├── useCryptoPrices.js      # Fetch prix
    │       ├── useCoinSearch.js        # Recherche avec debounce
    │       ├── useCountdown.js         # Countdown refresh
    │       ├── usePriceAlerts.js       # Alertes (backend)
    │       └── useUserData.js          # Données utilisateur
    │
    ├── package.json
    ├── vite.config.js
    └── .env.example
```
---

## 🎓 Concepts clés

### 1. Authentification JWT

Les tokens JWT permettent une authentification stateless :
- Le serveur génère un token signé contenant l'email de l'utilisateur
- Le client stocke le token et l'envoie dans chaque requête
- Le serveur vérifie la signature et extrait l'email
- Pas besoin de session côté serveur

### 2. Hachage bcrypt

Les mots de passe ne sont jamais stockés en clair :
- bcrypt génère un hash unique avec un salt aléatoire
- 12 rounds de hachage (2^12 = 4096 itérations)
- Impossible de retrouver le mot de passe depuis le hash
- Résistant aux attaques par force brute

### 3. TanStack Query

Gère automatiquement le cache et les requêtes :
- Cache côté client (90s pour les prix)
- Retry automatique avec exponential backoff
- Synchronisation entre onglets
- Garbage collection des données non utilisées

### 4. Cascade DELETE

Supprimer un utilisateur supprime automatiquement :
- Tous ses coins suivis (`user_coins`)
- Toutes ses alertes (`user_alerts`)
- Garantit l'intégrité référentielle

---

## 📝 Commandes utiles

### Backend

```bash
# Démarrer le serveur
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Voir l'historique des migrations
alembic history

# Revenir en arrière
alembic downgrade -1
```

### Frontend

```bash
# Démarrer le serveur
cd frontend
npm run dev

# Build pour production
npm run build

# Prévisualiser le build
npm run preview

# Linter
npm run lint
```

### Base de données

```bash
# Se connecter à la base
psql -U postgres -d cryptotracker

# Voir les tables
\dt

# Voir la structure d'une table
\d users

# Voir tous les utilisateurs
SELECT * FROM users;

# Voir les coins d'un utilisateur
SELECT * FROM user_coins WHERE user_id = 1;

# Voir les alertes d'un utilisateur
SELECT * FROM user_alerts WHERE user_id = 1;

# Sauvegarder la base
pg_dump -U postgres cryptotracker > backup.sql

# Restaurer la base
psql -U postgres cryptotracker < backup.sql

# Réinitialiser complètement
psql -U postgres -c "DROP DATABASE cryptotracker;"
psql -U postgres -c "CREATE DATABASE cryptotracker;"
cd backend
alembic upgrade head
```

---

## 🧪 Tests Unitaires

### Vue d'ensemble

Le projet dispose d'une suite complète de tests unitaires suivant les principes **Clean Architecture** et **SOLID**. Les tests garantissent l'isolation totale, la lisibilité et une couverture exhaustive des cas limites.

### Structure des tests

```
backend/tests/
├── conftest.py                      # Fixtures globales
├── pytest.ini                       # Configuration pytest
├── .coveragerc                      # Configuration couverture
└── unit/
    ├── core/
    │   └── test_security.py         # Tests sécurité (JWT, bcrypt)
    ├── services/
    │   └── test_coingecko_service.py # Tests service CoinGecko
    └── routers/
        ├── test_auth.py             # Tests authentification
        └── test_user.py             # Tests données utilisateur
```

### Principes appliqués

- **Isolation totale** : Mocks/Stubs pour toutes les dépendances (DB, API, cache)
- **Pattern AAA** : Arrange-Act-Assert (Given-When-Then)
- **Couverture complète** : Happy path + edge cases + error handling
- **Nommage descriptif** : `test_should_return_error_when_user_id_is_invalid`

### Lancer les tests

```bash
cd backend

# Activer l'environnement virtuel
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Installer pytest (si pas déjà fait)
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov

# Tests d'un module spécifique
pytest tests/unit/core/test_security.py

# Tests avec verbosité
pytest -v

# Tests avec rapport HTML
pytest --cov --cov-report=html
# Ouvrir htmlcov/index.html
```

### Couverture des tests

| Module | Tests | Couverture |
|--------|-------|------------|
| `core/security.py` | 25+ tests | Hachage, JWT, authentification |
| `services/coingecko_service.py` | 20+ tests | API calls, cache, erreurs |
| `routers/auth.py` | 15+ tests | Register, login, validation |
| `routers/user.py` | 30+ tests | CRUD coins/alerts, permissions |

### Exemples de scénarios testés

**Sécurité :**
- ✅ Hash bcrypt génère des salts différents
- ✅ Vérification de mot de passe correct/incorrect
- ✅ Token JWT valide/expiré/invalide
- ✅ Authentification avec utilisateur inexistant

**Service CoinGecko :**
- ✅ Cache hit/miss
- ✅ Rate limit (429) avec fallback sur données périmées
- ✅ Timeout avec retry
- ✅ Normalisation des données API

**Authentification :**
- ✅ Inscription avec email déjà utilisé
- ✅ Login avec identifiants incorrects
- ✅ Validation Pydantic (email invalide, mot de passe court)

**Données utilisateur :**
- ✅ Ajout de coin déjà suivi
- ✅ Suppression de coin inexistant
- ✅ Réorganisation avec drag & drop
- ✅ Alertes avec seuils invalides (≤ 0)

### Améliorations suggérées

**Code source :**
1. **Injection de dépendances** : Extraire `CoinGeckoService` en interface pour faciliter les tests
2. **Séparation des responsabilités** : Déplacer la logique métier des routers vers des services
3. **Validation centralisée** : Créer des validators réutilisables pour les coin_ids

**Tests :**
1. Ajouter des tests d'intégration avec vraie DB (SQLite in-memory)
2. Ajouter des tests de performance pour le cache
3. Ajouter des tests de sécurité (injection SQL, XSS)


---

## 🚀 Déploiement

### Frontend (Vercel/Netlify)

1. Build : `npm run build`
2. Déployer le dossier `dist/`
3. Configurer la variable d'environnement `VITE_API_URL`

### Backend (Railway/Render)

1. Configurer les variables d'environnement
2. Installer PostgreSQL addon
3. Exécuter `alembic upgrade head` au démarrage
4. Démarrer avec `uvicorn main:app --host 0.0.0.0 --port $PORT`

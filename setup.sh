#!/bin/bash

echo "========================================"
echo "  CryptoTracker - Setup Automatique"
echo "========================================"
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Python n'est pas installé"
    echo "Installez Python depuis https://www.python.org/downloads/"
    exit 1
fi

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Node.js n'est pas installé"
    echo "Installez Node.js depuis https://nodejs.org/"
    exit 1
fi

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} PostgreSQL n'est pas installé"
    echo "Installez PostgreSQL :"
    echo "  - macOS: brew install postgresql@16"
    echo "  - Linux: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Tous les prérequis sont installés"
echo ""

# ========================================
# Configuration Backend
# ========================================
echo "========================================"
echo "  Configuration du Backend"
echo "========================================"
echo ""

cd backend

# Créer l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "[1/5] Création de l'environnement virtuel Python..."
    python3 -m venv .venv
    echo -e "${GREEN}[OK]${NC} Environnement virtuel créé"
else
    echo "[1/5] Environnement virtuel déjà existant"
fi
echo ""

# Activer l'environnement virtuel et installer les dépendances
echo "[2/5] Installation des dépendances Python..."
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERREUR]${NC} Échec de l'installation des dépendances"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Dépendances installées"
echo ""

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "[3/5] Création du fichier .env..."
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Fichier .env créé"
    echo ""
    echo -e "${YELLOW}[IMPORTANT]${NC} Éditez backend/.env et configurez :"
    echo "  - DATABASE_URL avec votre mot de passe PostgreSQL"
    echo "  - SECRET_KEY avec une clé secrète (voir SETUP.md)"
    echo ""
    read -p "Appuyez sur Entrée pour continuer..."
else
    echo "[3/5] Fichier .env déjà existant"
    echo ""
fi

# Créer la base de données
echo "[4/5] Création de la base de données..."
echo "Entrez le mot de passe PostgreSQL quand demandé :"
psql -U postgres -c "CREATE DATABASE cryptotracker;" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[INFO]${NC} La base existe peut-être déjà (erreur ignorée)"
else
    echo -e "${GREEN}[OK]${NC} Base de données créée"
fi
echo ""

# Créer les tables
echo "[5/5] Création des tables (migrations)..."
alembic revision --autogenerate -m "Initial migration" > /dev/null 2>&1
alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERREUR]${NC} Échec de la création des tables"
    echo "Vérifiez DATABASE_URL dans backend/.env"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Tables créées"
echo ""

cd ..

# ========================================
# Configuration Frontend
# ========================================
echo "========================================"
echo "  Configuration du Frontend"
echo "========================================"
echo ""

cd frontend

# Installer les dépendances
echo "[1/2] Installation des dépendances Node.js..."
npm install > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERREUR]${NC} Échec de l'installation des dépendances"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Dépendances installées"
echo ""

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "[2/2] Création du fichier .env..."
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Fichier .env créé"
else
    echo "[2/2] Fichier .env déjà existant"
fi
echo ""

cd ..

# ========================================
# Fin du setup
# ========================================
echo "========================================"
echo "  Setup terminé avec succès !"
echo "========================================"
echo ""
echo "Pour démarrer l'application :"
echo ""
echo "  Terminal 1 - Backend :"
echo "    cd backend"
echo "    source .venv/bin/activate"
echo "    uvicorn main:app --reload --port 8000"
echo ""
echo "  Terminal 2 - Frontend :"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Puis ouvrez http://localhost:5173 dans votre navigateur"
echo ""
echo "Consultez SETUP.md pour plus de détails"
echo ""

 

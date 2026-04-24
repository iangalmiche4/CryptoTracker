#!/bin/bash

echo "========================================"
echo "  CryptoTracker - Démarrage Complet"
echo "========================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ========================================
# 1. Démarrer Redis
# ========================================
echo "[1/3] Démarrage de Redis..."
echo ""

# Vérifier si Redis est déjà en cours d'exécution
if docker exec cryptotracker-redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Redis est déjà en cours d'exécution"
else
    # Vérifier si le conteneur existe
    if docker ps -a --filter "name=cryptotracker-redis" --format "{{.Names}}" | grep -q "cryptotracker-redis"; then
        echo -e "${YELLOW}[INFO]${NC} Démarrage du conteneur Redis existant..."
        if docker start cryptotracker-redis &> /dev/null; then
            echo -e "${GREEN}[OK]${NC} Redis démarré avec succès"
        else
            echo -e "${RED}[ERREUR]${NC} Échec du démarrage de Redis"
            echo "Vérifiez que Docker est lancé"
            exit 1
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} Création d'un nouveau conteneur Redis..."
        if docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest &> /dev/null; then
            echo -e "${GREEN}[OK]${NC} Redis créé et démarré avec succès"
        else
            echo -e "${RED}[ERREUR]${NC} Échec de la création de Redis"
            echo "Vérifiez que Docker est lancé"
            exit 1
        fi
    fi
fi
echo ""

# Attendre que Redis soit prêt
sleep 2

# ========================================
# 2. Démarrer le Backend
# ========================================
echo "[2/3] Démarrage du Backend..."
echo ""

# Vérifier si le backend est déjà en cours d'exécution
if lsof -Pi :8000 -sTCP:LISTEN -t &> /dev/null; then
    echo -e "${YELLOW}[AVERTISSEMENT]${NC} Le port 8000 est déjà utilisé"
    echo "Le backend est peut-être déjà en cours d'exécution"
    echo ""
else
    echo "Démarrage du serveur FastAPI sur http://localhost:8000"
    echo ""
    
    # Démarrer dans un nouveau terminal selon l'OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/backend\" && source .venv/bin/activate && uvicorn main:app --reload --port 8000"'
    else
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000" &
        else
            echo -e "${YELLOW}[INFO]${NC} Démarrage du backend en arrière-plan..."
            cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000 &
            cd ..
        fi
    fi
    
    sleep 3
    echo -e "${GREEN}[OK]${NC} Backend démarré"
    echo ""
fi

# ========================================
# 3. Démarrer le Frontend
# ========================================
echo "[3/3] Démarrage du Frontend..."
echo ""

# Vérifier si le frontend est déjà en cours d'exécution
if lsof -Pi :5173 -sTCP:LISTEN -t &> /dev/null; then
    echo -e "${YELLOW}[AVERTISSEMENT]${NC} Le port 5173 est déjà utilisé"
    echo "Le frontend est peut-être déjà en cours d'exécution"
    echo ""
else
    echo "Démarrage du serveur Vite sur http://localhost:5173"
    echo ""
    
    # Démarrer dans un nouveau terminal selon l'OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/frontend\" && npm run dev"'
    else
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd frontend && npm run dev; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd frontend && npm run dev" &
        else
            echo -e "${YELLOW}[INFO]${NC} Démarrage du frontend en arrière-plan..."
            cd frontend && npm run dev &
            cd ..
        fi
    fi
    
    sleep 3
    echo -e "${GREEN}[OK]${NC} Frontend démarré"
    echo ""
fi

# ========================================
# Fin du démarrage
# ========================================
echo "========================================"
echo "  Application démarrée avec succès !"
echo "========================================"
echo ""
echo "Services en cours d'exécution :"
echo "  - Redis      : http://localhost:6379"
echo "  - Backend    : http://localhost:8000"
echo "  - Frontend   : http://localhost:5173"
echo ""
echo "Ouvrez http://localhost:5173 dans votre navigateur"
echo ""
echo "Pour arrêter l'application :"
echo "  - Fermez les terminaux Backend et Frontend (Ctrl+C)"
echo "  - Arrêtez Redis : docker stop cryptotracker-redis"
echo ""

# Made with Bob

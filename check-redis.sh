#!/bin/bash

echo "========================================"
echo "  Redis - Vérification et Démarrage"
echo "========================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si Redis est déjà en cours d'exécution
echo "[1/3] Vérification de Redis..."
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Redis est déjà en cours d'exécution"
    echo ""
    redis-cli info server | grep redis_version
    echo ""
    exit 0
fi

echo -e "${YELLOW}[INFO]${NC} Redis n'est pas en cours d'exécution"
echo ""

# Vérifier si Docker est installé
echo "[2/3] Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Docker n'est pas installé"
    echo ""
    echo "Options d'installation de Redis :"
    echo "  1. Docker : https://docs.docker.com/get-docker/"
    echo "  2. macOS : brew install redis"
    echo "  3. Linux : sudo apt install redis-server"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Docker est installé"
echo ""

# Vérifier si un conteneur Redis existe déjà
echo "[3/3] Vérification des conteneurs Redis..."
if docker ps -a --filter "name=cryptotracker-redis" --format "{{.Names}}" | grep -q "cryptotracker-redis"; then
    echo -e "${YELLOW}[INFO]${NC} Conteneur Redis existant trouvé"
    echo ""
    
    # Vérifier si le conteneur est en cours d'exécution
    if docker ps --filter "name=cryptotracker-redis" --format "{{.Names}}" | grep -q "cryptotracker-redis"; then
        echo -e "${GREEN}[OK]${NC} Le conteneur Redis est déjà en cours d'exécution"
    else
        echo -e "${YELLOW}[INFO]${NC} Démarrage du conteneur Redis existant..."
        if docker start cryptotracker-redis; then
            echo -e "${GREEN}[OK]${NC} Conteneur Redis démarré avec succès"
        else
            echo -e "${RED}[ERREUR]${NC} Échec du démarrage du conteneur"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}[INFO]${NC} Aucun conteneur Redis trouvé"
    echo -e "${YELLOW}[INFO]${NC} Création et démarrage d'un nouveau conteneur Redis..."
    if docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest; then
        echo -e "${GREEN}[OK]${NC} Conteneur Redis créé et démarré avec succès"
    else
        echo -e "${RED}[ERREUR]${NC} Échec de la création du conteneur"
        exit 1
    fi
fi

echo ""
echo "Attente de 2 secondes pour que Redis soit prêt..."
sleep 2

# Vérifier que Redis répond
if redis-cli ping &> /dev/null; then
    echo ""
    echo "========================================"
    echo "  Redis est prêt !"
    echo "========================================"
    echo ""
    redis-cli info server | grep redis_version
    echo ""
    echo "Pour arrêter Redis :"
    echo "  docker stop cryptotracker-redis"
    echo ""
    echo "Pour voir les logs Redis :"
    echo "  docker logs cryptotracker-redis"
    echo ""
else
    echo -e "${RED}[ERREUR]${NC} Redis ne répond pas"
    echo "Vérifiez les logs : docker logs cryptotracker-redis"
    exit 1
fi

echo "Vous pouvez maintenant démarrer le backend"
echo ""

# Made with Bob

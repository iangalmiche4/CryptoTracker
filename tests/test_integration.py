"""
test_integration.py - Tests d'intégration complets pour CryptoTracker

Ce script teste l'ensemble de l'application :
- Scripts de démarrage (setup.bat, start.bat, check-redis.bat)
- Backend API (tous les endpoints)
- Base de données (connexion, migrations)
- Redis (cache)
- Configuration (.env)

Usage:
    python test_integration.py
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

# Changer vers le répertoire racine du projet (remonter d'un niveau depuis tests/)
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
REDIS_PORT = 6379
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.RESET}\n")

# ============================================================================
# Tests de structure de projet
# ============================================================================

def test_project_structure():
    """Vérifie que tous les fichiers essentiels existent"""
    print_section("Test 1: Structure du Projet")
    
    required_files = [
        "setup.bat",
        "start.bat",
        "check-redis.bat",
        "README.md",
        "backend/main.py",
        "backend/config.py",
        "backend/requirements.txt",
        "backend/.env.example",
        "backend/alembic.ini",
        "frontend/package.json",
        "frontend/src/main.jsx",
        "frontend/src/config.js",
    ]
    
    required_dirs = [
        "backend",
        "frontend",
        "backend/routers",
        "backend/services",
        "backend/core",
        "backend/tests",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/contexts",
        "frontend/src/hooks",
    ]
    
    all_ok = True
    
    # Vérifier les fichiers
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Fichier trouvé: {file_path}")
        else:
            print_error(f"Fichier manquant: {file_path}")
            all_ok = False
    
    # Vérifier les dossiers
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print_success(f"Dossier trouvé: {dir_path}")
        else:
            print_error(f"Dossier manquant: {dir_path}")
            all_ok = False
    
    return all_ok

# ============================================================================
# Tests de configuration
# ============================================================================

def test_configuration():
    """Vérifie que les fichiers de configuration sont corrects"""
    print_section("Test 2: Configuration")
    
    all_ok = True
    
    # Vérifier backend/.env
    env_path = Path("backend/.env")
    if env_path.exists():
        print_success("Fichier backend/.env existe")
        
        # Lire et vérifier les variables essentielles
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "REDIS_HOST",
            "COINGECKO_URL",
        ]
        
        for var in required_vars:
            if var in env_content:
                print_success(f"Variable {var} présente")
            else:
                print_error(f"Variable {var} manquante")
                all_ok = False
    else:
        print_error("Fichier backend/.env manquant")
        print_info("Exécutez setup.bat pour le créer")
        all_ok = False
    
    # Vérifier backend/config.py
    config_path = Path("backend/config.py")
    if config_path.exists():
        print_success("Fichier backend/config.py existe")
    else:
        print_error("Fichier backend/config.py manquant")
        all_ok = False
    
    return all_ok

# ============================================================================
# Tests des services
# ============================================================================

def test_redis_connection():
    """Vérifie que Redis est accessible"""
    print_section("Test 3: Connexion Redis")
    
    try:
        # Vérifier avec redis-cli
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print_success("Redis répond correctement")
            return True
        else:
            print_error("Redis ne répond pas")
            print_info("Exécutez check-redis.bat pour démarrer Redis")
            return False
    except FileNotFoundError:
        print_error("redis-cli non trouvé")
        print_info("Installez Redis ou utilisez Docker")
        return False
    except subprocess.TimeoutExpired:
        print_error("Timeout lors de la connexion à Redis")
        return False

def test_backend_running():
    """Vérifie que le backend est accessible"""
    print_section("Test 4: Backend API")
    
    try:
        # Test du health check
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            print_success(f"Backend accessible sur {BACKEND_URL}")
            print_success(f"Health check: {response.json()}")
            return True
        else:
            print_error(f"Backend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Impossible de se connecter au backend")
        print_info("Exécutez start.bat ou démarrez manuellement le backend")
        return False
    except requests.exceptions.Timeout:
        print_error("Timeout lors de la connexion au backend")
        return False

def test_frontend_running():
    """Vérifie que le frontend est accessible"""
    print_section("Test 5: Frontend")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        
        if response.status_code == 200:
            print_success(f"Frontend accessible sur {FRONTEND_URL}")
            return True
        else:
            print_error(f"Frontend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Impossible de se connecter au frontend")
        print_info("Exécutez start.bat ou démarrez manuellement le frontend")
        return False
    except requests.exceptions.Timeout:
        print_error("Timeout lors de la connexion au frontend")
        return False

# ============================================================================
# Tests des endpoints API
# ============================================================================

def test_api_endpoints():
    """Teste les principaux endpoints de l'API"""
    print_section("Test 6: Endpoints API")
    
    all_ok = True
    
    # Test 1: Documentation Swagger
    try:
        response = requests.get(f"{BACKEND_URL}/api/docs", timeout=5)
        if response.status_code == 200:
            print_success("Swagger UI accessible (/api/docs)")
        else:
            print_error(f"Swagger UI inaccessible: {response.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"Erreur Swagger UI: {e}")
        all_ok = False
    
    # Test 2: Inscription
    try:
        test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "username": f"testuser_{int(time.time())}",
            "password": "TestPassword123!"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 201:
            print_success("Inscription réussie")
            user_data = response.json()
            token = user_data.get("access_token")
            
            # Test 3: Connexion
            login_data = {
                "username": test_user["email"],
                "password": test_user["password"]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print_success("Connexion réussie")
                token = response.json().get("access_token")
                
                # Test 4: Récupération des données utilisateur
                headers = {"Authorization": f"Bearer {token}"}
                
                response = requests.get(
                    f"{BACKEND_URL}/api/user/data",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print_success("Récupération des données utilisateur réussie")
                else:
                    print_error(f"Erreur données utilisateur: {response.status_code}")
                    all_ok = False
            else:
                print_error(f"Erreur connexion: {response.status_code}")
                all_ok = False
        else:
            print_error(f"Erreur inscription: {response.status_code}")
            print_info(f"Réponse: {response.text}")
            all_ok = False
    except Exception as e:
        print_error(f"Erreur lors des tests d'authentification: {e}")
        all_ok = False
    
    # Test 5: Endpoints publics (prix)
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/prices?ids=bitcoin,ethereum",
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Récupération des prix réussie")
            prices = response.json()
            print_info(f"Prix récupérés: {len(prices)} cryptos")
        else:
            print_error(f"Erreur prix: {response.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"Erreur lors de la récupération des prix: {e}")
        all_ok = False
    
    # Test 6: Recherche
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/search?query=bitcoin",
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Recherche réussie")
            results = response.json()
            print_info(f"Résultats trouvés: {len(results)}")
        else:
            print_error(f"Erreur recherche: {response.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"Erreur lors de la recherche: {e}")
        all_ok = False
    
    return all_ok

# ============================================================================
# Tests des scripts
# ============================================================================

def test_scripts_exist():
    """Vérifie que les scripts de démarrage existent et sont exécutables"""
    print_section("Test 7: Scripts de Démarrage")
    
    scripts = ["setup.bat", "start.bat", "check-redis.bat"]
    all_ok = True
    
    for script in scripts:
        if Path(script).exists():
            print_success(f"Script {script} existe")
        else:
            print_error(f"Script {script} manquant")
            all_ok = False
    
    return all_ok

# ============================================================================
# Rapport final
# ============================================================================

def generate_report(results):
    """Génère un rapport final des tests"""
    print_section("Rapport Final")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total de tests: {total_tests}")
    print(f"{Colors.GREEN}Tests réussis: {passed_tests}{Colors.RESET}")
    print(f"{Colors.RED}Tests échoués: {failed_tests}{Colors.RESET}")
    print()
    
    if failed_tests == 0:
        print(f"{Colors.GREEN}{'='*60}")
        print("  ✓ TOUS LES TESTS SONT PASSÉS !")
        print(f"{'='*60}{Colors.RESET}")
        print()
        print("L'application est prête à être utilisée.")
        return True
    else:
        print(f"{Colors.RED}{'='*60}")
        print("  ✗ CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"{'='*60}{Colors.RESET}")
        print()
        print("Détails des échecs:")
        for test_name, result in results.items():
            if not result:
                print(f"  {Colors.RED}✗ {test_name}{Colors.RESET}")
        print()
        print("Consultez les messages ci-dessus pour plus de détails.")
        return False

# ============================================================================
# Main
# ============================================================================

def main():
    """Exécute tous les tests"""
    print(f"{Colors.BLUE}")
    print("="*60)
    print("  TESTS D'INTÉGRATION CRYPTOTRACKER")
    print("="*60)
    print(f"{Colors.RESET}")
    print()
    print("Ce script va tester:")
    print("  1. Structure du projet")
    print("  2. Configuration (.env)")
    print("  3. Connexion Redis")
    print("  4. Backend API")
    print("  5. Frontend")
    print("  6. Endpoints API")
    print("  7. Scripts de démarrage")
    print()
    input("Appuyez sur Entrée pour commencer...")
    
    results = {}
    
    # Exécuter les tests
    results["Structure du projet"] = test_project_structure()
    results["Configuration"] = test_configuration()
    results["Redis"] = test_redis_connection()
    results["Backend"] = test_backend_running()
    results["Frontend"] = test_frontend_running()
    results["Endpoints API"] = test_api_endpoints()
    results["Scripts"] = test_scripts_exist()
    
    # Générer le rapport
    success = generate_report(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrompus par l'utilisateur{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Erreur inattendue: {e}{Colors.RESET}")
        sys.exit(1)


"""
run_all_tests.py - Script orchestrateur pour exécuter tous les tests

Ce script exécute tous les tests dans l'ordre recommandé :
1. Tests de sécurité (test_corrections.py)
2. Tests des middlewares (test_middlewares.py)
3. Tests unitaires backend (pytest)
4. Tests d'intégration (test_integration.py)

Usage:
    python run_all_tests.py
    python run_all_tests.py --skip-integration  # Sauter les tests d'intégration
    python run_all_tests.py --fast              # Tests rapides uniquement
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# Fix encoding pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Affiche un en-tête de section"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message):
    """Affiche une information"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def run_test_script(script_path, description):
    """
    Exécute un script de test Python
    
    Args:
        script_path: Chemin vers le script
        description: Description du test
    
    Returns:
        bool: True si le test a réussi, False sinon
    """
    print_info(f"Exécution : {description}")
    print(f"  Script : {script_path}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode == 0:
            print_success(f"{description} - RÉUSSI")
            return True
        else:
            print_error(f"{description} - ÉCHOUÉ (code {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT (> 5 minutes)")
        return False
    except Exception as e:
        print_error(f"{description} - ERREUR : {e}")
        return False

def run_pytest(description, args=None):
    """
    Exécute pytest avec des arguments optionnels
    
    Args:
        description: Description du test
        args: Arguments supplémentaires pour pytest
    
    Returns:
        bool: True si les tests ont réussi, False sinon
    """
    print_info(f"Exécution : {description}")
    
    cmd = [sys.executable, "-m", "pytest"]
    if args:
        cmd.extend(args)
    
    print(f"  Commande : {' '.join(cmd)}")
    print()
    
    # Sauvegarder le dossier original
    original_dir = os.getcwd()
    
    try:
        # Changer vers le dossier backend pour pytest
        backend_dir = Path(original_dir) / "backend"
        
        if backend_dir.exists():
            os.chdir(backend_dir)
        
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            timeout=300
        )
        
        # Revenir au dossier original
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print_success(f"{description} - RÉUSSI")
            return True
        else:
            print_error(f"{description} - ÉCHOUÉ (code {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        print_error(f"{description} - TIMEOUT (> 5 minutes)")
        return False
    except Exception as e:
        os.chdir(original_dir)
        print_error(f"{description} - ERREUR : {e}")
        return False

def generate_report(results):
    """
    Génère un rapport final des tests
    
    Args:
        results: Dictionnaire {nom_test: bool}
    """
    print_header("RAPPORT FINAL")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"Total de tests : {total}")
    print(f"{Colors.GREEN}Tests réussis : {passed}{Colors.RESET}")
    print(f"{Colors.RED}Tests échoués : {failed}{Colors.RESET}")
    print()
    
    # Détails par test
    for test_name, result in results.items():
        if result:
            print(f"  {Colors.GREEN}✓{Colors.RESET} {test_name}")
        else:
            print(f"  {Colors.RED}✗{Colors.RESET} {test_name}")
    
    print()
    
    # Message final
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}")
        print("  ✓ TOUS LES TESTS SONT PASSÉS !")
        print(f"{'='*70}{Colors.RESET}")
        print()
        print("🎉 L'application est prête pour le déploiement.")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}{'='*70}")
        print("  ✗ CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"{'='*70}{Colors.RESET}")
        print()
        print("⚠️  Veuillez corriger les erreurs avant de déployer.")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Exécute tous les tests CryptoTracker"
    )
    parser.add_argument(
        "--skip-integration",
        action="store_true",
        help="Sauter les tests d'intégration (nécessitent Redis/Backend/Frontend)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Tests rapides uniquement (sécurité + middlewares + unitaires)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Générer le rapport de couverture pour les tests unitaires"
    )
    
    args = parser.parse_args()
    
    # En-tête
    print(f"{Colors.MAGENTA}{Colors.BOLD}")
    print("="*70)
    print("  🧪 CRYPTOTRACKER - SUITE DE TESTS COMPLÈTE")
    print("="*70)
    print(f"{Colors.RESET}")
    print()
    print("Ce script va exécuter tous les tests dans l'ordre recommandé.")
    print()
    
    if args.fast:
        print_info("Mode RAPIDE : Tests d'intégration désactivés")
        print()
    
    results = {}
    
    # 1. Tests de sécurité
    print_header("1/4 - Tests de Sécurité")
    results["Tests de sécurité"] = run_test_script(
        "tests/test_corrections.py",
        "Validation des corrections de sécurité"
    )
    
    # 2. Tests des middlewares
    print_header("2/4 - Tests des Middlewares")
    results["Tests des middlewares"] = run_test_script(
        "tests/test_middlewares.py",
        "Validation des middlewares personnalisés"
    )
    
    # 3. Tests unitaires (pytest)
    print_header("3/4 - Tests Unitaires Backend")
    pytest_args = ["-v", "--tb=short"]
    if args.coverage:
        pytest_args.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    results["Tests unitaires"] = run_pytest(
        "Tests unitaires avec pytest",
        pytest_args
    )
    
    # 4. Tests d'intégration (optionnel)
    if not args.skip_integration and not args.fast:
        print_header("4/4 - Tests d'Intégration")
        print_warning("Les tests d'intégration nécessitent :")
        print("  - Redis démarré")
        print("  - Backend lancé (port 8000)")
        print("  - Frontend lancé (port 5173)")
        print()
        
        response = input("Continuer avec les tests d'intégration ? (o/N) : ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            results["Tests d'intégration"] = run_test_script(
                "tests/test_integration.py",
                "Tests d'intégration end-to-end"
            )
        else:
            print_info("Tests d'intégration ignorés")
            results["Tests d'intégration"] = None
    else:
        print_info("Tests d'intégration ignorés (--skip-integration ou --fast)")
        results["Tests d'intégration"] = None
    
    # Filtrer les tests None (ignorés)
    results = {k: v for k, v in results.items() if v is not None}
    
    # Rapport final
    success = generate_report(results)
    
    # Code de sortie
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrompus par l'utilisateur{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Erreur inattendue : {e}{Colors.RESET}")
        sys.exit(1)

 
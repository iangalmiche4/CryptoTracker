"""
Script de test pour valider les middlewares implémentés
"""

import sys
import os
from pathlib import Path

# Fix encoding pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Changer vers le répertoire racine du projet (remonter d'un niveau depuis tests/)
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# Ajouter les répertoires au path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

def test_imports():
    """Test 1: Vérifier que les imports fonctionnent"""
    print("🧪 Test 1: Imports des middlewares...")
    try:
        from backend.middleware import exception_handler_middleware, request_logging_middleware
        print("   ✅ Imports OK")
        return True
    except Exception as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_main_app():
    """Test 2: Vérifier que l'application se charge"""
    print("\n🧪 Test 2: Chargement de l'application...")
    try:
        from backend.main import app
        print("   ✅ Application chargée")
        return True
    except Exception as e:
        print(f"   ❌ Erreur de chargement: {e}")
        return False

def test_middleware_registration():
    """Test 3: Vérifier que les middlewares sont enregistrés"""
    print("\n🧪 Test 3: Enregistrement des middlewares...")
    try:
        from backend.main import app
        
        # Compter les middlewares HTTP
        middleware_count = len([m for m in app.user_middleware if m.kwargs.get('dispatch')])
        print(f"   ℹ️  Nombre de middlewares HTTP: {middleware_count}")
        
        if middleware_count >= 3:  # logging, exception, security
            print("   ✅ Middlewares enregistrés")
            return True
        else:
            print("   ⚠️  Nombre de middlewares insuffisant")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_router_simplification():
    """Test 4: Vérifier que coingecko.py a été simplifié"""
    print("\n🧪 Test 4: Simplification de coingecko.py...")
    try:
        with open('backend/routers/coingecko.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier qu'il n'y a plus de try/except dans les routes
        if 'try:' not in content or content.count('try:') == 0:
            print("   ✅ Fichier simplifié (pas de try/except)")
            return True
        else:
            print(f"   ⚠️  Encore {content.count('try:')} bloc(s) try/except")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_middleware_files():
    """Test 5: Vérifier que les fichiers middleware existent"""
    print("\n🧪 Test 5: Fichiers middleware...")
    files = [
        'backend/middleware/__init__.py',
        'backend/middleware/exception_handler.py',
        'backend/middleware/request_logging.py'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} manquant")
            all_exist = False
    
    return all_exist

def main():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("🔍 TESTS DES MIDDLEWARES")
    print("=" * 60)
    
    tests = [
        test_middleware_files,
        test_imports,
        test_main_app,
        test_middleware_registration,
        test_router_simplification
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Erreur lors du test: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("✅ Tous les tests sont passés!")
        return 0
    else:
        print("⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob

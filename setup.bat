@echo off
echo ========================================
echo   CryptoTracker - Setup Automatique
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)

REM Vérifier si PostgreSQL est installé
psql --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PostgreSQL n'est pas installe ou n'est pas dans le PATH
    echo Telechargez PostgreSQL depuis https://www.postgresql.org/download/
    pause
    exit /b 1
)

REM Vérifier si Redis est installé
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo [AVERTISSEMENT] Redis n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Redis est REQUIS pour le cache de l'application.
    echo.
    echo Options d'installation :
    echo   1. Docker (recommande) : docker run -d -p 6379:6379 redis:latest
    echo   2. Windows : https://github.com/microsoftarchive/redis/releases
    echo   3. WSL : sudo apt install redis-server
    echo.
    echo L'application fonctionnera en mode degrade sans Redis.
    echo.
    pause
) else (
    echo [OK] Redis est installe
)

echo [OK] Tous les prerequis sont installes
echo.

REM ========================================
REM Configuration Backend
REM ========================================
echo ========================================
echo   Configuration du Backend
echo ========================================
echo.

cd backend

REM Créer l'environnement virtuel
if not exist .venv (
    echo [1/5] Creation de l'environnement virtuel Python...
    python -m venv .venv
    echo [OK] Environnement virtuel cree
) else (
    echo [1/5] Environnement virtuel deja existant
)
echo.

REM Activer l'environnement virtuel et installer les dépendances
echo [2/5] Installation des dependances Python...
call .venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances
    pause
    exit /b 1
)
echo [OK] Dependances installees
echo.

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo [3/5] Creation du fichier .env...
    copy .env.example .env >nul
    echo [OK] Fichier .env cree
    echo.
    echo [IMPORTANT] Editez backend\.env et configurez :
    echo   - DATABASE_URL avec votre mot de passe PostgreSQL
    echo   - SECRET_KEY avec une cle secrete (voir SETUP.md)
    echo.
    pause
) else (
    echo [3/5] Fichier .env deja existant
    echo.
)

REM Créer la base de données
echo [4/5] Creation de la base de donnees...
echo Entrez le mot de passe PostgreSQL quand demande :
psql -U postgres -c "CREATE DATABASE cryptotracker;" 2>nul
if errorlevel 1 (
    echo [INFO] La base existe peut-etre deja (erreur ignoree)
) else (
    echo [OK] Base de donnees creee
)
echo.

REM Créer les tables
echo [5/5] Creation des tables (migrations)...
alembic revision --autogenerate -m "Initial migration" >nul 2>&1
alembic upgrade head
if errorlevel 1 (
    echo [ERREUR] Echec de la creation des tables
    echo Verifiez DATABASE_URL dans backend\.env
    pause
    exit /b 1
)
echo [OK] Tables creees
echo.

cd ..

REM ========================================
REM Configuration Frontend
REM ========================================
echo ========================================
echo   Configuration du Frontend
echo ========================================
echo.

cd frontend

REM Installer les dépendances
echo [1/2] Installation des dependances Node.js...
call npm install
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances
    pause
    exit /b 1
)
echo [OK] Dependances installees
echo.

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo [2/2] Creation du fichier .env...
    copy .env.example .env >nul
    echo [OK] Fichier .env cree
) else (
    echo [2/2] Fichier .env deja existant
)
echo.

cd ..

REM ========================================
REM Fin du setup
REM ========================================
echo ========================================
echo   Setup termine avec succes !
echo ========================================
echo.
echo Pour demarrer l'application :
echo.
echo   Terminal 1 - Redis (si pas deja demarre) :
echo     redis-server
echo     OU avec Docker : docker run -d -p 6379:6379 redis:latest
echo.
echo   Terminal 2 - Backend :
echo     cd backend
echo     .venv\Scripts\activate
echo     uvicorn main:app --reload --port 8000
echo.
echo   Terminal 3 - Frontend :
echo     cd frontend
echo     npm run dev
echo.
echo Puis ouvrez http://localhost:5173 dans votre navigateur
echo.
echo Consultez SETUP.md pour plus de details
echo.
pause

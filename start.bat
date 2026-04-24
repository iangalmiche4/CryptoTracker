@echo off
echo ========================================
echo   CryptoTracker - Demarrage Complet
echo ========================================
echo.

REM ========================================
REM 1. Demarrer Redis
REM ========================================
echo [1/3] Demarrage de Redis...
echo.

REM Vérifier si Redis est déjà en cours d'exécution
docker exec cryptotracker-redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis est deja en cours d'execution
) else (
    REM Vérifier si le conteneur existe
    docker ps -a --filter "name=cryptotracker-redis" --format "{{.Names}}" | findstr "cryptotracker-redis" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Demarrage du conteneur Redis existant...
        docker start cryptotracker-redis >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Redis demarre avec succes
        ) else (
            echo [ERREUR] Echec du demarrage de Redis
            echo Verifiez que Docker Desktop est lance
            pause
            exit /b 1
        )
    ) else (
        echo [INFO] Creation d'un nouveau conteneur Redis...
        docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Redis cree et demarre avec succes
        ) else (
            echo [ERREUR] Echec de la creation de Redis
            echo Verifiez que Docker Desktop est lance
            pause
            exit /b 1
        )
    )
)
echo.

REM Attendre que Redis soit prêt
timeout /t 2 /nobreak >nul

REM ========================================
REM 2. Demarrer le Backend
REM ========================================
echo [2/3] Demarrage du Backend...
echo.

REM Vérifier si le backend est déjà en cours d'exécution (port en écoute uniquement)
netstat -ano | findstr "LISTENING" | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [AVERTISSEMENT] Le port 8000 est deja utilise
    echo Le backend est peut-etre deja en cours d'execution
    echo.
) else (
    echo Demarrage du serveur FastAPI sur http://localhost:8000
    echo.
    start "CryptoTracker Backend" /D "%CD%\backend" cmd /k ".venv\Scripts\activate && uvicorn main:app --reload --port 8000"
    timeout /t 5 /nobreak >nul
    echo [OK] Backend demarre dans une nouvelle fenetre
    echo Si la fenetre ne s'ouvre pas, verifiez la barre des taches
    echo.
)

REM ========================================
REM 3. Demarrer le Frontend
REM ========================================
echo [3/3] Demarrage du Frontend...
echo.

REM Vérifier si le frontend est déjà en cours d'exécution (port en écoute uniquement)
netstat -ano | findstr "LISTENING" | findstr ":5173" >nul 2>&1
if %errorlevel% equ 0 (
    echo [AVERTISSEMENT] Le port 5173 est deja utilise
    echo Le frontend est peut-etre deja en cours d'execution
    echo.
) else (
    echo Demarrage du serveur Vite sur http://localhost:5173
    echo.
    start "CryptoTracker Frontend" /D "%CD%\frontend" cmd /k "npm run dev"
    timeout /t 5 /nobreak >nul
    echo [OK] Frontend demarre dans une nouvelle fenetre
    echo Si la fenetre ne s'ouvre pas, verifiez la barre des taches
    echo.
)

REM ========================================
REM Fin du demarrage
REM ========================================
echo ========================================
echo   Application demarree avec succes !
echo ========================================
echo.
echo Services en cours d'execution :
echo   - Redis      : http://localhost:6379
echo   - Backend    : http://localhost:8000
echo   - Frontend   : http://localhost:5173
echo.
echo Ouvrez http://localhost:5173 dans votre navigateur
echo.
echo Pour arreter l'application :
echo   - Fermez les fenetres Backend et Frontend
echo   - Arretez Redis : docker stop cryptotracker-redis
echo.
echo IMPORTANT : Si les fenetres ne s'ouvrent pas :
echo   1. Verifiez la barre des taches Windows (elles peuvent etre minimisees)
echo   2. Ou lancez manuellement :
echo      - Backend  : cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn main:app --reload
echo      - Frontend : cd frontend ^&^& npm run dev
echo.
echo Logs disponibles dans les fenetres separees
echo.
pause

@REM Made with Bob

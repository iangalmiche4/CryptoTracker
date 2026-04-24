@echo off
echo ========================================
echo   Redis - Verification et Demarrage
echo ========================================
echo.

REM Vérifier si Redis est déjà en cours d'exécution
echo [1/3] Verification de Redis...
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis est deja en cours d'execution
    echo.
    redis-cli info server | findstr "redis_version"
    echo.
    goto :end
)

echo [INFO] Redis n'est pas en cours d'execution
echo.

REM Vérifier si Docker est installé
echo [2/3] Verification de Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker n'est pas installe
    echo.
    echo Options d'installation de Redis :
    echo   1. Docker Desktop : https://www.docker.com/products/docker-desktop/
    echo   2. Redis pour Windows : https://github.com/microsoftarchive/redis/releases
    echo   3. WSL + Redis : wsl --install puis sudo apt install redis-server
    echo.
    pause
    exit /b 1
)

echo [OK] Docker est installe
echo.

REM Vérifier si un conteneur Redis existe déjà
echo [3/3] Verification des conteneurs Redis...
docker ps -a --filter "name=cryptotracker-redis" --format "{{.Names}}" | findstr "cryptotracker-redis" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Conteneur Redis existant trouve
    echo.
    
    REM Vérifier si le conteneur est en cours d'exécution
    docker ps --filter "name=cryptotracker-redis" --format "{{.Names}}" | findstr "cryptotracker-redis" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Le conteneur Redis est deja en cours d'execution
    ) else (
        echo [INFO] Demarrage du conteneur Redis existant...
        docker start cryptotracker-redis
        if %errorlevel% equ 0 (
            echo [OK] Conteneur Redis demarre avec succes
        ) else (
            echo [ERREUR] Echec du demarrage du conteneur
            pause
            exit /b 1
        )
    )
) else (
    echo [INFO] Aucun conteneur Redis trouve
    echo [INFO] Creation et demarrage d'un nouveau conteneur Redis...
    docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest
    if %errorlevel% equ 0 (
        echo [OK] Conteneur Redis cree et demarre avec succes
    ) else (
        echo [ERREUR] Echec de la creation du conteneur
        pause
        exit /b 1
    )
)

echo.
echo Attente de 2 secondes pour que Redis soit pret...
timeout /t 2 /nobreak >nul

REM Vérifier que Redis répond
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Redis est pret !
    echo ========================================
    echo.
    redis-cli info server | findstr "redis_version"
    echo.
    echo Pour arreter Redis :
    echo   docker stop cryptotracker-redis
    echo.
    echo Pour voir les logs Redis :
    echo   docker logs cryptotracker-redis
    echo.
) else (
    echo [ERREUR] Redis ne repond pas
    echo Verifiez les logs : docker logs cryptotracker-redis
    pause
    exit /b 1
)

:end
echo Vous pouvez maintenant demarrer le backend
echo.
pause

@REM Made with Bob

# ========================================
#   CryptoTracker - Démarrage Complet
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CryptoTracker - Démarrage Complet" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# 1. Démarrer Redis
# ========================================
Write-Host "[1/3] Démarrage de Redis..." -ForegroundColor Yellow
Write-Host ""

# Vérifier si Redis est déjà en cours d'exécution
$redisRunning = docker exec cryptotracker-redis redis-cli ping 2>$null
if ($redisRunning -eq "PONG") {
    Write-Host "[OK] Redis est déjà en cours d'exécution" -ForegroundColor Green
} else {
    # Vérifier si le conteneur existe
    $containerExists = docker ps -a --filter "name=cryptotracker-redis" --format "{{.Names}}" 2>$null
    if ($containerExists -eq "cryptotracker-redis") {
        Write-Host "[INFO] Démarrage du conteneur Redis existant..." -ForegroundColor Yellow
        docker start cryptotracker-redis | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Redis démarré avec succès" -ForegroundColor Green
        } else {
            Write-Host "[ERREUR] Échec du démarrage de Redis" -ForegroundColor Red
            Write-Host "Vérifiez que Docker Desktop est lancé" -ForegroundColor Yellow
            Read-Host "Appuyez sur Entrée pour quitter"
            exit 1
        }
    } else {
        Write-Host "[INFO] Création d'un nouveau conteneur Redis..." -ForegroundColor Yellow
        docker run -d --name cryptotracker-redis -p 6379:6379 redis:latest | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Redis créé et démarré avec succès" -ForegroundColor Green
        } else {
            Write-Host "[ERREUR] Échec de la création de Redis" -ForegroundColor Red
            Write-Host "Vérifiez que Docker Desktop est lancé" -ForegroundColor Yellow
            Read-Host "Appuyez sur Entrée pour quitter"
            exit 1
        }
    }
}
Write-Host ""

# Attendre que Redis soit prêt
Start-Sleep -Seconds 2

# ========================================
# 2. Démarrer le Backend
# ========================================
Write-Host "[2/3] Démarrage du Backend..." -ForegroundColor Yellow
Write-Host ""

# Vérifier si le backend est déjà en cours d'exécution
$backendRunning = netstat -ano | Select-String "LISTENING" | Select-String ":8000"
if ($backendRunning) {
    Write-Host "[AVERTISSEMENT] Le port 8000 est déjà utilisé" -ForegroundColor Yellow
    Write-Host "Le backend est peut-être déjà en cours d'exécution" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Démarrage du serveur FastAPI sur http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    
    # Démarrer le backend dans une nouvelle fenêtre
    $backendPath = Join-Path $PSScriptRoot "backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8000" -WindowStyle Normal
    
    Start-Sleep -Seconds 5
    Write-Host "[OK] Backend démarré dans une nouvelle fenêtre" -ForegroundColor Green
    Write-Host "Si la fenêtre ne s'ouvre pas, vérifiez la barre des tâches" -ForegroundColor Yellow
    Write-Host ""
}

# ========================================
# 3. Démarrer le Frontend
# ========================================
Write-Host "[3/3] Démarrage du Frontend..." -ForegroundColor Yellow
Write-Host ""

# Vérifier si le frontend est déjà en cours d'exécution
$frontendRunning = netstat -ano | Select-String "LISTENING" | Select-String ":5173"
if ($frontendRunning) {
    Write-Host "[AVERTISSEMENT] Le port 5173 est déjà utilisé" -ForegroundColor Yellow
    Write-Host "Le frontend est peut-être déjà en cours d'exécution" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Démarrage du serveur Vite sur http://localhost:5173" -ForegroundColor Cyan
    Write-Host ""
    
    # Démarrer le frontend dans une nouvelle fenêtre
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
    
    Start-Sleep -Seconds 5
    Write-Host "[OK] Frontend démarré dans une nouvelle fenêtre" -ForegroundColor Green
    Write-Host "Si la fenêtre ne s'ouvre pas, vérifiez la barre des tâches" -ForegroundColor Yellow
    Write-Host ""
}

# ========================================
# Fin du démarrage
# ========================================
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Application démarrée avec succès !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services en cours d'exécution :" -ForegroundColor Cyan
Write-Host "  - Redis      : http://localhost:6379" -ForegroundColor White
Write-Host "  - Backend    : http://localhost:8000" -ForegroundColor White
Write-Host "  - Frontend   : http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Ouvrez http://localhost:5173 dans votre navigateur" -ForegroundColor Green
Write-Host ""
Write-Host "Pour arrêter l'application :" -ForegroundColor Yellow
Write-Host "  - Fermez les fenêtres Backend et Frontend" -ForegroundColor White
Write-Host "  - Arrêtez Redis : docker stop cryptotracker-redis" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT : Si les fenêtres ne s'ouvrent pas :" -ForegroundColor Yellow
Write-Host "  1. Vérifiez la barre des tâches Windows (elles peuvent être minimisées)" -ForegroundColor White
Write-Host "  2. Ou lancez manuellement :" -ForegroundColor White
Write-Host "     - Backend  : cd backend; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload" -ForegroundColor White
Write-Host "     - Frontend : cd frontend; npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Logs disponibles dans les fenêtres séparées" -ForegroundColor Cyan
Write-Host ""
Read-Host "Appuyez sur Entrée pour quitter"


# ========================================
#   CryptoTracker - Setup Automatique
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CryptoTracker - Setup Automatique" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python est installé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Téléchargez Python depuis https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# Vérifier si Node.js est installé
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js est installé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Node.js n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Téléchargez Node.js depuis https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host ""

# ========================================
# Configuration Backend
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration du Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Créer l'environnement virtuel
if (-not (Test-Path ".venv")) {
    Write-Host "[1/5] Création de l'environnement virtuel Python..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[OK] Environnement virtuel créé" -ForegroundColor Green
} else {
    Write-Host "[1/5] Environnement virtuel déjà existant" -ForegroundColor Green
}
Write-Host ""

# Activer l'environnement virtuel et installer les dépendances
Write-Host "[2/5] Installation des dépendances Python..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dépendances installées" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Échec de l'installation des dépendances" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}
Write-Host ""

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "[3/5] Création du fichier .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[OK] Fichier .env créé" -ForegroundColor Green
    Write-Host ""
    Write-Host "[IMPORTANT] Éditez backend\.env et configurez :" -ForegroundColor Yellow
    Write-Host "  - DATABASE_URL avec votre mot de passe PostgreSQL" -ForegroundColor Yellow
    Write-Host "  - SECRET_KEY avec une clé secrète (voir SETUP.md)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour continuer"
} else {
    Write-Host "[3/5] Fichier .env déjà existant" -ForegroundColor Green
    Write-Host ""
}

# Créer la base de données
Write-Host "[4/5] Création de la base de données..." -ForegroundColor Yellow
Write-Host "Entrez le mot de passe PostgreSQL quand demandé :" -ForegroundColor Yellow
psql -U postgres -c "CREATE DATABASE cryptotracker;" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] La base existe peut-être déjà (erreur ignorée)" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Base de données créée" -ForegroundColor Green
}
Write-Host ""

# Créer les tables
Write-Host "[5/5] Création des tables (migrations)..." -ForegroundColor Yellow
alembic revision --autogenerate -m "Initial migration" 2>$null | Out-Null
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Tables créées" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Échec de la création des tables" -ForegroundColor Red
    Write-Host "Vérifiez DATABASE_URL dans backend\.env" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}
Write-Host ""

Set-Location ..

# ========================================
# Configuration Frontend
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration du Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

# Installer les dépendances
Write-Host "[1/2] Installation des dépendances Node.js..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dépendances installées" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] Échec de l'installation des dépendances" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}
Write-Host ""

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "[2/2] Création du fichier .env..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
    }
    Write-Host "[OK] Fichier .env créé" -ForegroundColor Green
} else {
    Write-Host "[2/2] Fichier .env déjà existant" -ForegroundColor Green
}
Write-Host ""

Set-Location ..

# ========================================
# Fin du setup
# ========================================
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup terminé avec succès !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer l'application :" -ForegroundColor Cyan
Write-Host ""
Write-Host "  PowerShell :" -ForegroundColor Yellow
Write-Host "    .\start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  CMD :" -ForegroundColor Yellow
Write-Host "    start.bat" -ForegroundColor White
Write-Host ""
Write-Host "Puis ouvrez http://localhost:5173 dans votre navigateur" -ForegroundColor Cyan
Write-Host ""
Read-Host "Appuyez sur Entrée pour quitter"

# Made with Bob

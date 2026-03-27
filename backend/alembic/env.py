"""
env.py — Configuration de l'environnement Alembic

Ce fichier configure comment Alembic se connecte à la base de données
et génère les migrations. Il est exécuté à chaque commande Alembic.

Responsabilités :
  - Charger les modèles SQLAlchemy pour l'autogenerate
  - Configurer la connexion à la base de données
  - Définir les modes de migration (online/offline)
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ── Import des modèles ────────────────────────────────────────────────
# Nécessaire pour que l'autogenerate détecte les changements de schéma

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base
from models import User, UserCoin, UserAlert

# ── Configuration Alembic ─────────────────────────────────────────────

# Objet de configuration Alembic (accès aux valeurs du fichier .ini)
config = context.config

# Charger DATABASE_URL depuis le fichier .env
# Cela permet d'utiliser la même configuration que l'application
from dotenv import load_dotenv
load_dotenv()
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Configuration du logging Python depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées des modèles SQLAlchemy
# C'est ce qui permet à Alembic de détecter les changements de schéma
target_metadata = Base.metadata

# ── Fonctions de migration ────────────────────────────────────────────


def run_migrations_offline() -> None:
    """
    Exécute les migrations en mode 'offline'.
    
    Ce mode configure le contexte avec uniquement une URL de connexion,
    sans créer d'Engine SQLAlchemy. Cela permet de générer des scripts SQL
    sans avoir besoin d'une connexion active à la base de données.
    
    Les appels à context.execute() émettent les commandes SQL dans la sortie
    standard au lieu de les exécuter directement.
    
    Utilisation :
        alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Exécute les migrations en mode 'online'.
    
    Ce mode crée un Engine SQLAlchemy et établit une connexion réelle
    à la base de données. Les migrations sont exécutées directement
    sur la base de données.
    
    C'est le mode par défaut utilisé lors de l'exécution de :
        alembic upgrade head
        alembic downgrade -1
    
    Le pool de connexions est configuré avec NullPool pour éviter
    les problèmes de connexions persistantes lors des migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ── Point d'entrée ────────────────────────────────────────────────────

# Détermine automatiquement le mode à utiliser
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

#!/bin/sh

# Génère une révision automatique pour l'initialisation du schéma
alembic revision --autogenerate -m "Initial migration"

# Applique les migrations Alembic pour initialiser la base de données
alembic upgrade head

# Modifications apportées au schéma - génère une nouvelle révision
alembic revision --autogenerate -m "Modify schema"

# Applique les nouvelles modifications de schéma
alembic upgrade head

# Démarre le serveur FastAPI avec Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

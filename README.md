# Online Library Management API

FastAPI Project


```bash
# Virtual environment creation & activation
python3 -m venv venv
.\venv\Scripts\activate
# Installing libraries listed in 'requirements.txt'
pip install -r requirements.txt
pip freeze
# Creation table oracledb
python proj_sqlalch.py
# Generate secret_key
python -c 'import os; print(os.urandom(24).hex())'
```

Deactivation of the virtual environment (if necessary)
```bash
deactivate
```

## Démarrage application

Variables d'environnement à définir dans un fichier .env  (exemple):
```text
# Connect oracledb
DATABASE_USER
DATABASE_PASSWORD
DATABASE_DSN

# SQLalchemy
SQLALCHEMY_DATABASE_URL

# Key to sign the token
SECRET_KEY
```

```bash
fastapi dev main.py
````
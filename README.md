# Online Library Management API

FastAPI Project


```bash
# Virtual environment creation & activation
python3 -m venv venv
.\venv\Scripts\activate
# Installing libraries listed in 'requirements.txt'
pip install -r requirements.txt
pip freeze
```

Deactivation of the virtual environment (if necessary)
```bash
deactivate
```

## Démarrage application

Variables d'environnement à définir dans un fichier .env  (exemple):
```text
BDD_URL=sqlite://:memory:
```

```bash
fastapi dev main.py
````
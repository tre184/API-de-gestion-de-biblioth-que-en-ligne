from typing import Union, Optional

from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from dotenv import load_dotenv
import os,schema, uvicorn, crud

import models

load_dotenv()

# Instancie FastAPI
app = FastAPI()
# Traitement des fichiers statics (HTML, CSS, JS, IMAGES ...)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Traitement des templates (Jinja2)
templates = Jinja2Templates(directory="templates")

# Route pour la page d'accueil

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/index.html
    '''
    books =  crud.all_book()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

# Page de connexion
@app.get("/login", response_class=HTMLResponse, name="connexion")
def connexion_page(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/login.html
    '''
    return templates.TemplateResponse("login.html", {"request": request})

# Page d'inscription
@app.get("/inscription", response_class=HTMLResponse, name="inscription_page")
def inscription_page(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/inscription.html
    '''
    return templates.TemplateResponse("inscription.html", {"request": request})

# Page user connecté
@app.get("/users/{users_name}", response_model=schema.UserCreated)
def read_page(users_name: str, request: Request):
    '''
    Récupérer la page d'un utilisateur connecté
    :param request: L'objet Request pour Jinja2
    :param users_name: Nom de l'utilisateur à afficher
    :return: redirection vers /templates/user.html
    '''
    return templates.TemplateResponse("user.html", {"request": request, "user": users})
''''
# Route pour afficher les livres empruntés et l'historique d'un utilisateur
@app.get("/users/{user_name}/emprunts", response_model=schema.UserOut)
def read_emprunts(user_name: str, request: Request):
    # Filtrer les emprunts par utilisateur
    user_emprunts = [emprunt for emprunt in emprunts if emprunt["user"] == user_name]

    # Passer les emprunts et les informations au template HTML
    return templates.TemplateResponse("emprunts.html", {
        "request": request,
        "user_name": user_name,
        "emprunts": user_emprunts
    })

# Route pour afficher les livres empruntés récemment
@app.get("/recent-emprunts", name="recent_emprunts")
def recent_emprunts(request: Request):
    # Récupérer les emprunts récents ici
    emprunts_recents = []  # Exemple vide
    return templates.TemplateResponse("emprunts.html", {"request": request, "emprunts": emprunts_recents, "title": "Livres empruntés récemment"})

# Route pour afficher l'historique des emprunts
@app.get("/historique-emprunts", name="historique_emprunts")
def historique_emprunts(request: Request):
    # Récupérer l'historique des emprunts ici
    historique = []  # Exemple vide
    return templates.TemplateResponse("emprunts.html", {"request": request, "emprunts": historique, "title": "Historique des emprunts"})'''

@app.post("/submit_signup", response_class=HTMLResponse, name="submit_signup")
def submit_signup(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        phone: Optional[str] = Form(None),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    # Vérification que les mots de passe correspondent
    if password != confirm_password:
        return templates.TemplateResponse("inscription.html", {"request": request, "error": "Les mots de passe ne correspondent pas"})

    # Utilisation du schéma Pydantic pour valider et créer l'utilisateur
    try:
        user_data = UserCreated.create_user(name=name, email=email, phone=phone, password=password)
    except ValidationError as e:
        # Gestion des erreurs de validation
        return templates.TemplateResponse("inscription.html", {"request": request, "error": e.errors()})

    # Vérifier si l'utilisateur existe déjà
    user_in_db = db.query(User).filter(User.email == email).first()
    if user_in_db:
        return templates.TemplateResponse("inscription.html", {"request": request, "error": "L'utilisateur existe déjà"})

    # Création de l'utilisateur avec le mot de passe haché
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password=user_data.password  # Mot de passe déjà haché par Pydantic
    )

    # Ajout de l'utilisateur dans la base de données
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redirection vers la page de confirmation après succès
    return templates.TemplateResponse("login.html", {"request": request})
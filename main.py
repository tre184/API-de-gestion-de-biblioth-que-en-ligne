from typing import Union, Optional, List
from datetime import datetime, date, timedelta
from fastapi import FastAPI, Request, Form, Depends,HTTPException, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from passlib.context import CryptContext
from dotenv import load_dotenv
from schema import UserLogin
import os,schema, uvicorn, crud

# Chargement des variables d'environnement
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Clé secrète utilisée pour signer les tokens
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cryptage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utilisation du token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Instancie FastAPI
app = FastAPI()
# Traitement des fichiers statics (HTML, CSS, JS, IMAGES ...)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Traitement des templates (Jinja2)
templates = Jinja2Templates(directory="templates")

# Vérification et hachage des mots de passe
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Création du token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Récupération de l'utilisateur dans la base de données
def get_user(username: str):
    return crud.connexion(username)

# Authentification de l'utilisateur
def authenticate_user(username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur et mot de passe requis.")
    user = get_user(username)
    if not user or not verify_password(password, user.password):
        return False
    return user

# Obtenir l'utilisateur actuel
def get_current_user(access_token: str = Cookie(None)) -> schema.UserCreated:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token is missing")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing username")
        user = crud.connexion(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token: user not found")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token decoding error: {str(e)}")
    return schema.UserCreated.model_validate(user, from_attributes=True)


# Route pour la page d'accueil

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/index.html
    '''
    books =  crud.all_books()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

# Route pour la page de connexion
@app.get("/login", response_class=HTMLResponse, name="connexion")
def connexion_page(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/login.html
    '''
    return templates.TemplateResponse("login.html", {"request": request})

# Route pour la page d'inscription
@app.get("/inscription", response_class=HTMLResponse, name="inscription_page")
def inscription_page(request: Request):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/registration.html
    '''
    return templates.TemplateResponse("registration.html", {"request": request})

# Route de la page user connecté
@app.get("/user/{username}", response_model=schema.UserCreated)
def user_page(
        request: Request,
        current_user: schema.UserCreated = Depends(get_current_user)
):

    '''
    Affiche la page d'accueil pour un utilisateur connecté avec la liste de livres
    :param request: L'objet Request pour Jinja2
    :param current_user: L'utilisateur actuellement connecté
    :return: redirection vers /templates/user.html
    '''

    books = crud.all_books()
    if books is None:
        books = []

    # Retourner le template avec la liste des livres
    return templates.TemplateResponse("user.html", {"request": request, "user": current_user, "books": books})

# Route pour afficher les livres empruntés et l'historique d'un utilisateur
@app.get("/users/{username}/emprunts", name="gestion_emprunts")
def read_emprunts(
        request: Request,
        username: str
):
    '''

    :param request:
    :param username: name de l'utilisateur
    :return:
    '''

    # Récupérer l'utilisateur par son nom
    user = crud.connexion(username)

    # Récupérer les emprunts de l'utilisateur depuis la base de données
    user_emprunts = crud.get_loan_by_user(user.id)

    # Passer les emprunts et les informations au template HTML
    return templates.TemplateResponse("management_loans.html", {
        "request": request,
        "user": user,
        "emprunts": user_emprunts
    })

# Route formulaire d'inscription
@app.post("/submit_signup", response_class=HTMLResponse, name="submit_signup")
def submit_signup(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        phone: Optional[str] = Form(None),
        password: str = Form(...),
        confirm_password: str = Form(...)
):
    # Vérification que les mots de passe correspondent
    if password != confirm_password:
        return templates.TemplateResponse("registration.html", {"request": request, "error": "Les mots de passe ne correspondent pas"})

    # Utilisation du schéma Pydantic pour valider et créer l'utilisateur
    try:
        user = schema.UserCreate.create_user(name=name, email=email, phone=phone, password=password)
    except ValidationError as e:
        # Gestion des erreurs de validation
        return templates.TemplateResponse("registration.html", {"request": request, "error": "Erreur de validation des données : " + str(e.errors())})

    new_user = crud.create_user(user)

    if new_user is None:
        return templates.TemplateResponse("registration.html", {"request": request, "error": "L'utilisateur existe déjà"})

    # Redirection vers la page de confirmation après succès
    return RedirectResponse(url="/login", status_code=303)

# Route pour la connexion
@app.post("/login", response_class=HTMLResponse, name="connecte")
def login(
        request: Request,
        user_data: UserLogin =  Depends(UserLogin.as_form)
):
    '''
    Route qui gère le processus de connexion d'un utilisateur
    :param request: L'objet Request pour Jinja2
    :param user_data: Schéma UserLogin avec les données de connexion (username et password)
    :param password: Le mot de passe envoyé par le formulaire
    :return: Redirection vers la page user.html en cas de succès, ou renvoi sur la page de connexion avec erreur
    '''

    user = crud.connexion(user_data.username)
    if not user or not pwd_context.verify(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Génération du token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)

    # Stockage du token dans un cookie
    response = RedirectResponse(url=f"/user/{user.name}", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)  # secure=True pour HTTPS
    return response

# Route de déconnexion
@app.post("/logout", response_class=HTMLResponse, name="logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)  # Rediriger vers la page de connexion
    response.delete_cookie("access_token")  # Supprimez le cookie contenant le token
    return response

#Route pour la gestion des livres
@app.get("/gestion_des_livres", response_class=HTMLResponse, name="gestion_livres")
def gestion_livres(request: Request, current_user: schema.UserCreated = Depends(get_current_user)):
    '''
    Traitement du GET /
    :param request: L'objet Request pour Jinja2
    :return: redirection vers /templates/management_books.html
    '''
    books =  crud.all_books()
    return templates.TemplateResponse("management_books.html", {"request": request, "books": books, "user": current_user})

# Route pour afficher le formulaire d'ajout du book
@app.get("/ajouter livre", response_class=HTMLResponse, name="ajoute livre")
def add_book_page(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})

# Route création du book
@app.post("/submit_add_book", response_class=HTMLResponse, name="submit_add_book")
def create_book(
        request: Request,
        title: str = Form(...),
        author: str = Form(...),
        kind: str = Form(...),
        publication_date: str = Form(...)
):
    # Vérification de la validité de la date
    if not publication_date:
        return {"error": "La date de publication est obligatoire."}

    try:
        pub_date = datetime.strptime(publication_date, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Format de date invalide. Utilisez le format YYYY-MM-DD."}

    # Validation des autres champs
    if not title or not author or not kind:
        return {"error": "Tous les champs (titre, auteur, genre) sont obligatoires."}

    # Vous pouvez ensuite utiliser 'pub_date' comme un objet date
    new_book = schema.BookCreate(title=title, author=author, kind=kind, publication_date=pub_date)


    # Logique pour insérer le livre dans la base de données (par exemple, via CRUD)
    created_book = crud.create_book(new_book)

    if created_book is None:
        return templates.TemplateResponse("add_book.html", {"request": request, "error": "Le livre existe déjà"})

    return RedirectResponse(url="/gestion_des_livres", status_code=303)

# Route pour afficher le formulaire de modification du book
@app.get("/modifier_livre/{book_id}", response_class=HTMLResponse)
def modifier_livre(request: Request, book_id: int):
    '''
    Affiche la page de modification d'un livre
    :param request: L'objet Request pour Jinja2
    :param book_id: ID du livre à modifier
    :return: redirection vers /templates/update_book.html
    '''
    # Récupérer le livre depuis la base de données
    book = crud.get_book_by_id(book_id)

    # Afficher la page avec les données actuelles du livre
    return templates.TemplateResponse("update_book.html", {"request": request, "book": book})

# Route modifiaction book
@app.put("/update_book/{book_id}", response_class=HTMLResponse)
async def update_book(
        request: Request,
        book_id: int
):
    # Récupérer le livre existant
    book = crud.get_book_by_id(book_id)

    # Récupérer les données JSON depuis la requête
    data = await request.json()

    # Extraire les champs envoyés dans le JSON
    title = data.get('title')
    author = data.get('author')
    kind = data.get('kind')
    publication_date = data.get('publication_date')

    # Mise à jour des informations du livre
    try:
        pub_date = datetime.strptime(publication_date, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Format de date invalide. Utilisez le format YYYY-MM-DD."}

    # Logique pour mettre à jour le livre dans la base de données
    updated_book = crud.update_book(book_id, title, author, kind, pub_date)

    # Redirection vers la page de gestion des livres après modification
    return RedirectResponse(url="/gestion_des_livres", status_code=303)

# Route suppression book
@app.delete("/delete_book/{book_id}", response_class=HTMLResponse)
def delete_book(request: Request, book_id: int):
    '''
    Route pour supprimer un livre
    :param request: L'objet Request pour Jinja2
    :param book_id: L'ID du livre à supprimer
    :return: Redirection vers la page de gestion des livres
    '''
    # Supprimer le livre
    deleted_book = crud.delete_book(book_id)

    # Redirection vers la page de gestion des livres après la suppression
    return RedirectResponse(url="/gestion_des_livres", status_code=303)

# Route recherche book
@app.get("/search_books", response_model=List[schema.BookCreated])
def search_book(
        request: Request,
        title: Optional[str] = None,
        author: Optional[str] = None,
        kind: Optional[str] = None
):
    '''
    Route pour rechercher des livres par titre, auteur ou genre
    :param request: L'objet Request pour Jinja2
    :param title: Titre du livre (optionnel)
    :param author: Auteur du livre (optionnel)
    :param kind: Genre du livre (optionnel)
    :return: Liste de livres correspondant aux critères
    '''
    # Rechercher les livres
    books = crud.search_book(title=title, author=author, kind=kind)

    # Retourner le template avec la liste des livres trouvés
    return templates.TemplateResponse("search_result.html", {"request": request, "books": books})

# Route emprunt book
@app.get("/user/{username}/loan_book/{book_title}", response_class=HTMLResponse, name="loan_book")
def loan_book_page(
        request: Request,
        username: str,
        book_title: str
):
    '''

    :param request:
    :param username: Nom de l'utilisateur
    :param book_title: Titre du livre
    :return: Template avec les détails du livre et formulaire d'emprunt
    '''

    # Récupérer l'utilisateur par son nom
    user = crud.connexion(username)

    # Récupérer le livre par son titre
    book = crud.get_book_by_title(book_title)

    # Vérifier combien de livres l'utilisateur a déjà empruntés
    user_emprunts = crud.get_emprunts_by_user(user.id)
    if len(user_emprunts) >= 6:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas emprunter plus de 6 livres")
    # Retourner la page avec les détails du livre et un formulaire pour l'emprunt
    return templates.TemplateResponse("loan_book.html", {"request": request, "user": user, "book": book, "max_days": 30})


# route confirmer emprunt book
@app.post("/user/{username}/loan_book/{book_title}", response_class=HTMLResponse)
def emprunter_book(
        request: Request,
        username: str,
        book_title: str,
        return_date: str = Form(...)
):
    '''
    Route pour qu'un utilisateur emprunte un livre
    :param request: Objet Request pour Jinja2
    :param user_id: ID du user qui emprunte
    :param book_id: ID du livre à emprunter
    :return:
    '''

    # Convertir la chaîne de date en un objet date
    try:
        return_date = datetime.strptime(return_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide")

    # Récupérer l'utilisateur et le livre comme dans la fonction précédente
    user = crud.connexion(username)
    book = crud.get_book_by_title(book_title)

    # Vérifier si la date de retour est valide
    max_return_date = date.today() + timedelta(days=30)
    if return_date > max_return_date:
        raise HTTPException(status_code=400, detail="La date de retour dépasse la limite de 30 jours")

    # Emprunter le livre
    emprunt = crud.borrow_book(user.id, book.id, return_date)

    return RedirectResponse(url=f"/user/{username}", status_code=303)

# Route rendu book emprunté
@app.post("/user/{username}/return_book/{book_title}", response_class=HTMLResponse, name="return_book")
def return_book(
        request: Request,
        username: str,
        book_title: str
):
    '''
    Route pour retourner un livre emprunté par un utilisateur
    :param request: Objet Request pour Jinja2
    :param username: Nom d'utilisateur
    :param book_title: Titre du livre
    :return: Template de confirmation du retour
    '''
    # Récupérer l'utilisateur et le livre
    user = crud.connexion(username)
    book = crud.get_book_by_title(book_title)

    # Appeler la fonction pour retourner le livre
    result = crud.return_book(user.id, book.id)

    return RedirectResponse(url=f"/user/{username}", status_code=303)

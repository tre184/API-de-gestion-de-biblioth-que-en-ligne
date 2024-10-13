import os, models, schema
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, select, func
from sqlalchemy.orm import declarative_base, sessionmaker, joinedload
from dotenv import load_dotenv
from datetime import date
from passlib.context import CryptContext

load_dotenv()

SQLALCHEMY_DATABASE_URL=os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cryptage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gestion des sessions
Session = sessionmaker(bind=engine)

# Ajout d'un nouvel utilisateur avec hashage de mot de passe
def create_user(user: schema.UserCreate) -> schema.UserCreated:
    '''
    Crée un nouvel user
    :param user: schema UserCreate
    :return: schema UserCreate
    '''
    with Session() as session:
        # Vérification si l'utilisateur existe déjà dans la base de données par son email
        user_in_db = session.query(models.User).filter(models.User.email == user.email).first()
        if user_in_db:
            return None

        # Hachage du mot de passe de l'utilisateur
        hashed_password = pwd_context.hash(user.password)

        # Création du nouvel utilisateur avec les données fournies
        new_user = models.User(**user.model_dump())
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return schema.UserCreated.model_validate(new_user, from_attributes=True)

def create_book(book: schema.BookCreate) -> schema.BookCreated:
    '''
    Crée un nouveau book
    :param book: schema BookCreate
    :return: schema BookCreated
    '''
    with Session() as session:
        # Vérifier si le livre existe déjà
        existing_book = session.query(models.Book).filter(models.Book.title == book.title).first()
        if existing_book:
            return None
        new_book = models.Book(**book.model_dump())
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return schema.BookCreated.model_validate(new_book, from_attributes=True)

def all_books() -> List[schema.BookCreated]:
    '''
    retourne tous les books
    :param book: schema BookCreate
    :return: schema BookCreated
    '''
    with Session() as session:
        books = session.query(models.Book).all()
        return [schema.BookCreated.model_validate(book, from_attributes=True) for book in books]

def get_book_by_id(book_id) -> schema.BookCreated:
    '''
    retourne book de la base de données
    :param book_id: ID du book à modifier
    :return: book
    '''

    with Session() as session:
        book = session.query(models.Book).get(book_id)
        return schema.BookCreated.model_validate(book, from_attributes=True)

def get_book_by_title(book_title: str) ->schema.BookCreated:
    '''
    retouren book de la base de données
    :param book_title:  Title du book
    :return: book
    '''

    with Session() as session:
        book = session.query(models.Book).filter(models.Book.title == book_title).first()
        return schema.BookCreated.model_validate(book, from_attributes=True)

def get_book_by_author(book_author: str) ->schema.BookCreated:
    '''
    retouren book de la base de données
    :param book_title:  Title du book
    :return: book
    '''

    with Session() as session:
        book = session.query(models.Book).filter(models.Book.author == book_author).first()
        return schema.BookCreated.model_validate(book, from_attributes=True)

def get_book_by_kind(book_kind: str) ->schema.BookCreated:
    '''
    retouren book de la base de données
    :param book_title:  Title du book
    :return: book
    '''

    with Session() as session:
        book = session.query(models.Book).filter(models.Book.kind == book_kind).first()
        if book:
            return schema.BookCreated.model_validate(book, from_attributes=True)
        else:
            print(f"Aucun livre trouvé pour le genre : {book_kind}")
            return None

def get_emprunts_by_user(user_id: int) -> List[schema.EmpruntCreated]:
    '''
    Récupère tous les emprunts d'un utilisateur
    '''
    with Session() as session:
        emprunts = session.query(models.Emprunt).filter(models.Emprunt.user_id == user_id).all()
        return [schema.EmpruntCreated.model_validate(emprunt, from_attributes=True) for emprunt in emprunts]

def search_book(title: Optional[str] = None, author: Optional[str] = None, kind: Optional[str] = None) -> List[schema.BookCreated]:
    with Session() as session:
        query = session.query(models.Book)

        if title and title.strip():
            query = query.filter(func.lower(func.trim(models.Book.title)).like(f'%{title.strip().lower()}%'))

        if author and author.strip():
            query = query.filter(func.lower(func.trim(models.Book.author)).like(f'%{author.strip().lower()}%'))

        if kind and kind.strip():
            query = query.filter(func.lower(func.trim(models.Book.kind)).like(f'%{kind.strip().lower()}%'))

        # Exécuter la requête
        books = query.all()

        if not books:
            print("Aucun livre trouvé avec les critères donnés.")
            return []

        return [schema.BookCreated.model_validate(book, from_attributes=True) for book in books]

def borrow_book(user_id: int, book_id: int, return_date: date):
    '''
    Fonction pour qu'un utilisateur emprunte un livre
    :param user_id: ID de l'utilisateur qui emprunte
    :param book_id: ID du livre à emprunter
    :return: l'emprunt créé ou un message d'erreur
    '''
    with Session() as session:
        # Vérifier si le livre existe et est disponible
        book = session.query(models.Book).filter(models.Book.id == book_id).first()

        # Créer l'emprunt avec la date d'emprunt actuelle
        emprunt = models.Emprunt(user_id=user_id, book_id=book_id, borrow_date=date.today(), return_date=return_date)
        session.add(emprunt)

        # Marquer le livre comme indisponible
        book.availability = False

        session.commit()
        session.refresh(emprunt)

        return emprunt



def get_users() -> [schema.UserCreated]:
    '''
    Récupère tous les Users de la base de données
    :return: Users
    '''
    with Session() as session:
        users = session.query(models.User).all()
        return [schema.UserCreated.model_validate(user, from_attributes=True) for user in users]

# Connexion de l'utilisateur
def connexion(username: str) -> models.User:
    '''
    Récupère l'utilisateur de la base de données avec le nom d'utilisateur donné
    :return: User
    '''
    with Session() as session:
        user = session.query(models.User).filter(models.User.name == username).first()
        return user

# Vérification du mot de passe
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Récupération de l'utilisateur
def get_user(username: str):
    with Session() as session:
        return session.query(models.User).filter(models.User.name == username).first()

def update_book(book_id: int, title: str, author: str, kind: str, publication_date: date) -> schema.BookCreated:
    '''
    Met à jour un livre
    :param book_id: ID du book à modifier
    :param title: Nouveau titre
    :param author: Nouvel auteur
    :param kind: Nouveau genre
    :param publication_date: Nouvelle date de publication
    :return: Book mis à jour
    '''
    with Session() as session:
        book = session.query(models.Book).filter(models.Book.id == book_id).first()

        # Mise à jour des attributs
        book.title = title
        book.author = author
        book.kind = kind
        book.publication_date = publication_date

        # Enregistrement des modifications
        session.commit()
        session.refresh(book)

        return schema.BookCreated.model_validate(book, from_attributes=True)

def delete_book(book_id: int) -> schema.BookCreated:
    '''
    Supprime un book
    :param book_id: ID du book à supprimer
    :return: book supprimé
    '''
    with Session() as session:
        book = session.query(models.Book).filter(models.Book.id == book_id).first()


        # Enregistrement des modifications
        session.delete(book)
        session.commit()

        return schema.BookCreated.model_validate(book, from_attributes=True)

def get_loan_by_user(user_id: int):
    '''

    :param user_id:
    :return:
    '''
    with Session() as session:
        emprunts = session.query(models.Emprunt).options(joinedload(models.Emprunt.book)).filter(models.Emprunt.user_id == user_id).all()
        return emprunts

def return_book(user_id: int, book_id: int):
    '''
    Fonction pour retourner un livre emprunté.
    :param user_id: ID de l'utilisateur qui retourne le livre
    :param book_id: ID du livre à retourner
    :return: Dictionnaire avec le statut de l'opération
    '''
    with Session() as session:
        # Trouver l'emprunt correspondant (non retourné)
        emprunt = session.query(models.Emprunt).filter(
            models.Emprunt.user_id == user_id,
            models.Emprunt.book_id == book_id,
            models.Emprunt.returned == False
        ).first()

        # Mettre à jour l'état de l'emprunt pour indiquer qu'il est retourné
        emprunt.returned = True

        # Rendre le livre disponible à nouveau
        book = session.query(models.Book).filter(models.Book.id == book_id).first()
        if book:
            book.availability = True

        # Sauvegarder les modifications
        session.commit()
        return {"message": "Livre retourné avec succès."}
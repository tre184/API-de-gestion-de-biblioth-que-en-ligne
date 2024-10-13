from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, User, Book, Emprunt
import os



load_dotenv()  # take environment variables from .env (do not overver already defined vars)

# Connexion à la base de données
SQLALCHEMY_DATABASE_URL=os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Création de la table
#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Gestion des sessions
Session = sessionmaker(bind=engine)
session = Session()

session.commit()
import os, models, schema
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL=os.getenv('SQLALCHEMY_DATABASE_URL')
print('SQLALCHEMY_DATABASE_URL', SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Gestion des sessions
Session = sessionmaker(bind=engine)

def create_user(user: schema.UserCreate) -> schema.UserCreated:
    '''
    Crée un nouvel user
    :param user: schema UserCreate
    :return: schema UserCreate
    '''
    with Session() as session:
        new_user = models.User(**user.model_dump())
        session.add(new_user)
        session.commit()
        return schema.UserCreated.model_validate(new_user, from_attributes=True)
    return None

def create_book(book: schema.BookCreate) -> schema.BookCreated:
    '''
    Crée un nouveau book
    :param book: schema BookCreate
    :return: schema BookCreated
    '''
    with Session() as session:
        new_user = models.User(**book.model_dump())
        session.add(new_book)
        session.commit()
        return schema.BookCreated.model_validate(new_book, from_attributes=True)
    return None

def all_book() -> List[schema.BookCreated]:
    '''
    retourne tous les books
    :param book: schema BookCreate
    :return: schema BookCreated
    '''
    with Session() as session:
        books = session.query(models.Book).all()
        return [schema.BookOut.model_validate(book, from_attributes=True) for book in books]

'''def get_user_by_id(user_id: int) -> schema.UserCreated:
    '''
    #get_user_by_id : récupère un User à partir de son id
    #:param user_id: l'ID du user
    #:return: User

    #with Session() as session:
        #user = session.query(models.User).get(user_id)
        #return schema.UserCreated.model_validate(user, from_attributes=True)

#def get_users() -> [schema.UserCreated]:
    #'''
    #get_user_by_id : récupère un User à partir de son id
    #:param user_id: l'ID du user
    #:return: User
    #'''
    #with Session() as session:
        #users = session.query(models.User).all()
        #return [schema.UserCreated.model_validate(user, from_attributes=True) for user in users]'''
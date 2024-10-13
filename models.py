from sqlalchemy import create_engine, Column, Integer, String, select, Date, Boolean, ForeignKey, Sequence, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import date

# Definition of the basis
Base = declarative_base()

# Definition de la table users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('users_seq'), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=True)
    password = Column(String(255), nullable=False)
    # Relation avec les emprunts
    emprunts = relationship("Emprunt", back_populates="user")

    def __repr__(self) -> str:
        return f"User[{self.id}] : {self.name}"

# Definition dela table books
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, Sequence('books_seq'), primary_key=True)
    title = Column(String(50))
    author = Column(String(50))
    kind = Column(String(50))
    publication_date = Column(Date)
    availability = Column(Numeric(1), default=1)
    # Relation avec les emprunts
    emprunts = relationship("Emprunt", back_populates="book")

    def __repr__(self) -> str:
        return f"Book[{self.id}] : {self.title}"

# Definition de la table emprunts
class Emprunt(Base):
    __tablename__ = 'emprunts'
    id = Column(Integer, Sequence('emprunts_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", backref="emprunts")
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    book = relationship("Book", backref="emprunts")
    borrow_date = Column(Date, default=date.today)
    return_date = Column(Date, nullable=False)
    returned = Column(Numeric(1), default=0)
    # Relations pour les utilisateurs et les livres
    user = relationship("User", back_populates="emprunts")
    book = relationship("Book", back_populates="emprunts")

    def __repr__(self) -> str:
        return f"Emprunt[{self.id}] - User: {self.user_id}, Book: {self.book_id}, Returned: {self.returned}"
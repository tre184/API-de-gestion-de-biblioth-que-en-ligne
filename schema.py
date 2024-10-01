from pydantic import BaseModel, PositiveInt, EmailStr, constr, ValidationError
from datetime import date
from typing import Optional, List


from passlib.context import CryptContext

# Configuration pour le hachage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fonction pour hacher le mot de passe
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Schéma de base pour les utilisateurs
class User(BaseModel):
    name: str
    email: str
    phone: Optional[str] | None

# Schéma pour créer un utilisateur (incluant le mot de passe)
class UserCreate(User):
    password: constr(min_length=6)
    @classmethod
    def create_user(cls, name: str, email: str, phone: Optional[str], password: str) -> 'UserCreate':
        hashed_password = hash_password(password)  # Hachage du mot de passe avant de le stocker
        return cls(name=name, email=email, phone=phone, password=hashed_password)
# Schéma pour retourner un utilisateur (incluant l'ID)
class UserCreated(User):
    id: int

    class Config:
        from_attributes = True

# Schéma de base pour les livres
class Book(BaseModel):
    title: str
    author: str
    publication_date: date
    availability: Optional[bool] = True

# Schéma pour créer un livre
class BookCreate(Book):
    pass

# Schéma pour retourner un livre (incluant l'ID)
class BookCreated(Book):
    id: int

    class Config:
        from_attributes = True

# Schéma de base pour les emprunts
class Emprunt(BaseModel):
    borrow_date: date
    return_date: date
    returned: Optional[bool] = False

# Schéma pour créer un emprunt
class EmpruntCreate(Emprunt):
    user_id: int
    book_id: int

# Schéma pour retourner un emprunt (incluant l'ID et les relations)
class EmpruntCreated(Emprunt):
    id: int
    user: UserCreated
    book: BookCreated

    class Config:
        from_attributes = True

# Simuler des utilisateurs en dur
#users = [
    #UserOut(id=1, name="Alice Dupont", email="alice@example.com", phone="123456789"),
    #UserOut(id=2, name="Bob Martin", email="bob@example.com", phone="987654321"),
    #UserOut(id=3, name="Charlie Dubois", email="charlie@example.com", phone="564738291"),
#]

# Simuler des livres en dur
#books = [
    #BookOut(id=1, title="L'Art de la Guerre", author="Sun Tzu", publication_date=datetime(2005, 1, 1), availability=True),
    #BookOut(id=2, title="1984", author="George Orwell", publication_date=datetime(1949, 6, 8), availability=True),
    #BookOut(id=3, title="Le Petit Prince", author="Antoine de Saint-Exupéry", publication_date=datetime(1943, 4, 6), availability=True),
    #BookOut(id=4, title="Harry Potter à l'école des sorciers", author="J.K. Rowling", publication_date=datetime(1997, 6, 26), availability=True),
    #BookOut(id=5, title="Les Misérables", author="Victor Hugo", publication_date=datetime(1862, 1, 1), availability=True),
    #BookOut(id=6, title="Le Comte de Monte-Cristo", author="Alexandre Dumas", publication_date=datetime(1845, 8, 28), availability=True),
    #BookOut(id=7, title="Germinal", author="Émile Zola", publication_date=datetime(1885, 3, 12), availability=True),
    #BookOut(id=8, title="L'Étranger", author="Albert Camus", publication_date=datetime(1942, 5, 1), availability=True),
    #BookOut(id=9, title="Madame Bovary", author="Gustave Flaubert", publication_date=datetime(1857, 12, 1), availability=True),
    #BookOut(id=10, title="La Peste", author="Albert Camus", publication_date=datetime(1947, 6, 1), availability=True),
#]

# Simuler des emprunts en dur (chaque utilisateur a emprunté deux livres)
#emprunts = [
    #EmpruntOut(id=1, user=users[0], book=books[0], borrow_date=datetime.now() - timedelta(days=5), return_date=datetime.now() + timedelta(days=10), returned=False),
    #EmpruntOut(id=2, user=users[0], book=books[1], borrow_date=datetime.now() - timedelta(days=8), return_date=datetime.now() + timedelta(days=5), returned=False),
    #EmpruntOut(id=3, user=users[1], book=books[2], borrow_date=datetime.now() - timedelta(days=3), return_date=datetime.now() + timedelta(days=7), returned=False),
    #EmpruntOut(id=4, user=users[1], book=books[3], borrow_date=datetime.now() - timedelta(days=10), return_date=datetime.now() + timedelta(days=3), returned=False),
    #EmpruntOut(id=5, user=users[2], book=books[4], borrow_date=datetime.now() - timedelta(days=2), return_date=datetime.now() + timedelta(days=12), returned=False),
    #EmpruntOut(id=6, user=users[2], book=books[5], borrow_date=datetime.now() - timedelta(days=6), return_date=datetime.now() + timedelta(days=8), returned=False),
#]

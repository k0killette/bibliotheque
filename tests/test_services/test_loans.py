import pytest
from sqlalchemy.orm import Session
# Imports des modèles
from src.models.loans import Loan
from src.models.books import Book
from src.models.users import User
# Imports des repositories
from src.repositories.loans import LoanRepository
from src.repositories.books import BookRepository
from src.repositories.users import UserRepository
# Imports des services métier
from src.services.loans import LoanService
from src.services.books import BookService
from src.services.users import UserService
# Imports des schémas (DTOs)
from src.api.schemas.loans import LoanCreate
from src.api.schemas.books import BookCreate
from src.api.schemas.users import UserCreate

def setup_test_data(db_session: Session):
    book_repo = BookRepository(Book, db_session)
    user_repo = UserRepository(User, db_session)
    book_service = BookService(book_repo)
    user_service = UserService(user_repo)

    # Création d’un livre (quantité = 2)
    book = book_repo.create(BookCreate(
        title="Loan Book",
        author="Author L",
        isbn="3333333333333",
        quantity=2,
        publication_year=2024
    ))

    # Création d’un utilisateur via un dictionnaire brut
    user = user_repo.create(UserCreate(
        email="loan@example.com",
        password="password",
        full_name="Loan User"
    ))

    return user, book

def test_create_loan(db_session: Session):
    user, book = setup_test_data(db_session)

    loan_repo = LoanRepository(Loan, db_session)
    book_repo = BookRepository(Book, db_session)

    service = LoanService(loan_repo, BookService(book_repo))

    loan_in = LoanCreate(user_id=user.id, book_id=book.id)

    loan = service.create(obj_in=loan_in)

    assert loan.user_id == user.id
    assert loan.book_id == book.id
    assert loan.return_date is None

    book_after = book_repo.get(id=book.id)
    assert book_after.quantity == 1 # /!\ un exemplaire a été emprunté


def test_create_loan_book_unavailable(db_session: Session):
    user, book = setup_test_data(db_session)

    book_repo = BookRepository(Book, db_session)

    # Quantité = 0 - le livre est indisponible 
    book.quantity = 0
    db_session.commit()

    loan_repo = LoanRepository(Loan, db_session)
    service = LoanService(loan_repo, BookService(book_repo))

    loan_in = LoanCreate(user_id=user.id, book_id=book.id)

    with pytest.raises(ValueError, match="Livre non disponible"):
        service.create(obj_in=loan_in)


def test_return_loan(db_session: Session):
    user, book = setup_test_data(db_session)

    loan_repo = LoanRepository(Loan, db_session)
    book_repo = BookRepository(Book, db_session)
    service = LoanService(loan_repo, BookService(book_repo))

    # Création d’un emprunt
    loan = service.create(obj_in=LoanCreate(
        user_id=user.id, 
        book_id=book.id
    ))

    # Retour du livre
    returned_loan = service.return_loan(loan_id=loan.id)

    # Le retour est bien enregistré
    assert returned_loan.return_date is not None

    book_after = book_repo.get(id=book.id)
    # Le stock est rétabli
    assert book_after.quantity == 2


def test_return_loan_invalid_id(db_session: Session):
    loan_repo = LoanRepository(Loan, db_session)
    book_repo = BookRepository(Book, db_session)
    service = LoanService(loan_repo, BookService(book_repo))

    with pytest.raises(ValueError, match="Emprunt non trouvé"):
        service.return_loan(loan_id=999)

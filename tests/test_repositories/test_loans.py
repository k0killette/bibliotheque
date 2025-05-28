import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.models.loans import Loan
from src.models.users import User
from src.models.books import Book
from src.repositories.loans import LoanRepository

@pytest.fixture
def sample_user(db: Session) -> User:
    user = User(
        email="loanuser@example.com",
        hashed_password="fakehashedpassword",
        full_name="Loan User",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def sample_book(db: Session) -> Book:
    book = Book(
        title="Loan Test Book",
        author="Loan Author",
        isbn="1234567890123",
        publication_year=2020,
        quantity=3
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@pytest.fixture
def sample_loan(db: Session, sample_user: User, sample_book: Book) -> Loan:
    loan_data = {
        "user_id": sample_user.id,
        "book_id": sample_book.id,
        "loan_date": datetime.utcnow() - timedelta(days=2),
        "due_date": datetime.utcnow() + timedelta(days=5),
        "return_date": None,
        "extended": False
    }
    loan = Loan(**loan_data)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

def test_create_loan(db: Session, sample_user: User, sample_book: Book):
    repo = LoanRepository(db)
    loan_date = datetime.utcnow()
    due_date = loan_date + timedelta(days=14)
    new_loan = repo.create({
        "user_id": sample_user.id,
        "book_id": sample_book.id,
        "loan_date": loan_date,
        "due_date": due_date,
        "return_date": None,
        "extended": False
    })
    assert new_loan.id is not None
    assert new_loan.user_id == sample_user.id
    assert new_loan.book_id == sample_book.id
    assert new_loan.due_date == due_date
    assert new_loan.return_date is None

def test_get_loan_by_id(db: Session, sample_loan: Loan):
    repo = LoanRepository(db)
    fetched = repo.get_by_id(sample_loan.id)
    assert fetched is not None
    assert fetched.id == sample_loan.id

def test_update_loan(db: Session, sample_loan: Loan):
    repo = LoanRepository(db)
    return_date = datetime.utcnow()
    updated = repo.update(sample_loan, {"return_date": return_date, "extended": True})
    assert updated.return_date == return_date
    assert updated.extended is True

def test_delete_loan(db: Session, sample_loan: Loan):
    repo = LoanRepository(db)
    repo.delete(sample_loan)
    deleted = repo.get_by_id(sample_loan.id)
    assert deleted is None

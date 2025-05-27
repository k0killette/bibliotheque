import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.repositories.books import BookRepository
from src.services.books import BookService
from src.api.schemas.books import BookCreate


def test_create_book(db_session: Session):
    """
    Teste la création d'un livre.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    # Schéma de création de livre
    book_in = BookCreate(
        title="Test Book",
        author="John Doe",
        isbn="1234567890123",
        quantity=5,
        publication_year=2024
    )

    # Appel au service pour créer le livre
    book = service.create(obj_in=book_in)

    # Assertions pour vérifier que le livre a bien été enregistré avec les bonnes données
    assert book.title == "Test Book"
    assert book.author == "John Doe"
    assert book.isbn == "1234567890123"
    assert book.quantity == 5
    assert book.publication_year == 2024

def test_create_book_isbn_already_used(db_session: Session):
    """
    Teste la création d'un livre avec un isbn déjà utilisé.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="First Book",
        author="Jane Smith",
        isbn="1111111111111",
        quantity=3,
        publication_year=2025
    )

    # Création d'un premier livre
    service.create(obj_in=book_in)

    # Tentative de création avec un ISBN déjà utilisé
    with pytest.raises(ValueError):
        service.create(obj_in=book_in)


def test_get_by_title(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    # Création d'un livre avec un titre unique
    service.create(obj_in=BookCreate(
        title="Unique Title", 
        author="Author A", 
        isbn="0000000000001", 
        quantity=1,
        publication_year=2024
    ))

    # Recherche d’un livre par mot-clé dans le titre
    results = service.get_by_title(title="Unique")

    # On vérifie que le bon livre est retourné
    assert len(results) == 1
    assert results[0].title == "Unique Title"


def test_update_quantity(db_session: Session):
    """
    Teste la mise à jour de la quantité d'un livre.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    # Création d’un livre avec une quantité initiale
    book_in = BookCreate(
        title="Quant Book", 
        author="Author Q", 
        isbn="9999999999999", 
        quantity=10,
        publication_year=2024
    )

    book = service.create(obj_in=book_in)
    
    # On diminue la quantité de 3 : 10 - 3 = 7
    book_quantity_update = service.update_quantity(book_id=book.id, quantity_change=-3)
    assert book_quantity_update.quantity == 7

    # On augmente de 5 : 7 + 5 = 12
    book_quantity_update = service.update_quantity(book_id=book.id, quantity_change=5)
    assert book_quantity_update.quantity == 12

    # On essaie de retirer trop : 12 - 20 = -8 → erreur attendue
    with pytest.raises(ValueError, match="La quantité ne peut pas être négative"):
        service.update_quantity(book_id=book.id, quantity_change=-20)

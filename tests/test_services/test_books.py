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
        author="Test Author",
        isbn="0123456789",
        publication_year=2023,
        quantity=5
    )

    # Appel au service pour créer le livre
    book = service.create(obj_in=book_in)

    # Assertions pour vérifier que le livre a bien été enregistré avec les bonnes données
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "0123456789"
    assert book.publication_year == 2023
    assert book.quantity == 5

def test_create_book_isbn_already_used(db_session: Session):
    """
    Teste la création d'un livre avec un isbn déjà utilisé.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="First Book",
        author="John Doe",
        isbn="0123456789",
        publication_year=2023,
        quantity=3
    )

    # Création d'un premier livre
    service.create(obj_in=book_in)

    # Tentative de création avec un ISBN déjà utilisé
    book_in_duplicate = BookCreate(
        title="Second Book",
        author="Jane Doe",
        isbn="0123456789",
        publication_year=2024,
        quantity=2
    )
    with pytest.raises(ValueError, match="L'ISBN est déjà utilisé"):
        service.create(obj_in=book_in_duplicate)

def test_get_by_isbn(db_session: Session):
    """
    Teste la récupération d'un livre par ISBN.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)
    
    book_in = BookCreate(
        title="ISBN Test Book",
        author="ISBN Author",
        isbn="0123456789",
        publication_year=2023,
        quantity=4
    )
    
    created_book = service.create(obj_in=book_in)
    
    # Récupération réussie
    retrieved_book = service.get_by_isbn(isbn="0123456789")
    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "ISBN Test Book"
    
    # Récupération échouée - ISBN inexistant
    retrieved_book = service.get_by_isbn(isbn="9876543210")
    assert retrieved_book is None

def test_get_by_title(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    # Création de plusieurs livres avec des titres similaires
    book1_in = BookCreate(
        title="Python Programming",
        author="John Doe",
        isbn="11111111111",
        publication_year=2023,
        quantity=3
    )
    book2_in = BookCreate(
        title="Advanced Python",
        author="Jane Smith",
        isbn="22222222222",
        publication_year=2024,
        quantity=2
    )
    book3_in = BookCreate(
        title="Java Programming",
        author="Bob Johnson",
        isbn="33333333333",
        publication_year=2023,
        quantity=1
    )

    service.create(obj_in=book1_in)
    service.create(obj_in=book2_in)
    service.create(obj_in=book3_in)

    # Recherche d’un livre par mot-clé dans le titre
    python_books = service.get_by_title(title="Python")
    programming_books = service.get_by_title(title="Programming")

    # On vérifie que le bon livre est retourné
    assert len(python_books) == 2
    assert len(programming_books) == 2

def test_get_by_author(db_session: Session):
    """
    Teste la recherche de livres par auteur.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)
    
    book1_in = BookCreate(
        title="Book One",
        author="Famous Author",
        isbn="44444444444",
        publication_year=2022,
        quantity=2
    )
    book2_in = BookCreate(
        title="Book Two",
        author="Famous Author",
        isbn="55555555555",
        publication_year=2023,
        quantity=3
    )
    book3_in = BookCreate(
        title="Different Book",
        author="Another Author",
        isbn="66666666666",
        publication_year=2023,
        quantity=1
    )
    
    service.create(obj_in=book1_in)
    service.create(obj_in=book2_in)
    service.create(obj_in=book3_in)
    
    # Recherche par auteur
    famous_author_books = service.get_by_author(author="Famous Author")
    assert len(famous_author_books) == 2
    
    another_author_books = service.get_by_author(author="Another")
    assert len(another_author_books) == 1

def test_update_quantity(db_session: Session):
    """
    Teste la mise à jour de la quantité d'un livre.
    """
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    # Création d’un livre avec une quantité initiale
    book_in = BookCreate(
        title="Quantity Test Book", 
        author="Test Author", 
        isbn="99999999999", 
        publication_year=2024,
        quantity=10
    )

    book = service.create(obj_in=book_in)
    original_quantity = book.quantity
    
    # Augmenter la quantité
    updated_book = service.update_quantity(book_id=book.id, quantity_change=5)
    assert updated_book.quantity == original_quantity + 5
    
    # Diminuer la quantité
    updated_book = service.update_quantity(book_id=book.id, quantity_change=-3)
    assert updated_book.quantity == original_quantity + 5 - 3
    
    # Tenter de mettre une quantité négative
    with pytest.raises(ValueError, match="La quantité ne peut pas être négative"):
        service.update_quantity(book_id=book.id, quantity_change=-20)

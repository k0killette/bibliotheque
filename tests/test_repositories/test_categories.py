import pytest
from sqlalchemy.orm import Session

from src.models.categories import Category
from src.repositories.categories import CategoryRepository

@pytest.fixture
def sample_category(db: Session) -> Category:
    category = Category(name="Test Catégorie", description="Une description de test")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def test_create_category(db: Session):
    repo = CategoryRepository(db)
    new_category = repo.create({
        "name": "Science-Fiction",
        "description": "Livres de SF futuristes"
    })
    assert new_category.id is not None
    assert new_category.name == "Science-Fiction"
    assert new_category.description == "Livres de SF futuristes"

def test_get_category_by_id(db: Session, sample_category: Category):
    repo = CategoryRepository(db)
    fetched = repo.get_by_id(sample_category.id)
    assert fetched is not None
    assert fetched.id == sample_category.id
    assert fetched.name == "Test Catégorie"

def test_update_category(db: Session, sample_category: Category):
    repo = CategoryRepository(db)
    updated = repo.update(sample_category, {"description": "Nouvelle description"})
    assert updated.description == "Nouvelle description"

def test_delete_category(db: Session, sample_category: Category):
    repo = CategoryRepository(db)
    repo.delete(sample_category)
    deleted = repo.get_by_id(sample_category.id)
    assert deleted is None

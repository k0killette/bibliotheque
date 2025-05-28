import pytest
from sqlalchemy.orm import Session
from src.repositories.users import UserRepository
from src.api.schemas.users import UserCreate, UserUpdate
from src.models.users import User
from src.utils.security import verify_password


def test_create_user(db_session: Session):
    """
    Teste la création d'un utilisateur.
    """
    user_in = UserCreate(
        email="newuser@example.com",
        full_name="New User",
        password="strongpassword"
    )
    user = UserRepository.create(db_session, obj_in=user_in)
    
    assert user.email == user_in.email
    assert user.full_name == user_in.full_name
    assert user.is_active is True
    assert verify_password("strongpassword", user.hashed_password)


def test_get_user_by_id(db_session: Session):
    user_in = UserCreate(
        email="getbyid@example.com",
        full_name="Get By Id",
        password="password"
    )
    created_user = UserRepository.create(db_session, obj_in=user_in)
    user = UserRepository.get(db_session, created_user.id)
    
    assert user is not None
    assert user.id == created_user.id


def test_get_user_by_email(db_session: Session):
    email = "getbyemail@example.com"
    user_in = UserCreate(
        email=email,
        full_name="Get By Email",
        password="password"
    )
    UserRepository.create(db_session, obj_in=user_in)
    user = UserRepository.get_by_email(db_session, email=email)

    assert user is not None
    assert user.email == email


def test_update_user(db_session: Session):
    user_in = UserCreate(
        email="updateuser@example.com",
        full_name="Update User",
        password="initialpassword"
    )
    created_user = UserRepository.create(db_session, obj_in=user_in)

    update_data = UserUpdate(
        full_name="Updated User",
        is_active=False
    )
    updated_user = UserRepository.update(db_session, db_obj=created_user, obj_in=update_data)

    assert updated_user.full_name == "Updated User"
    assert updated_user.is_active is False


def test_delete_user(db_session: Session):
    user_in = UserCreate(
        email="deleteuser@example.com",
        full_name="Delete User",
        password="tobedeleted"
    )
    created_user = UserRepository.create(db_session, obj_in=user_in)
    user_id = created_user.id

    UserRepository.remove(db_session, id=user_id)
    deleted_user = UserRepository.get(db_session, id=user_id)

    assert deleted_user is None

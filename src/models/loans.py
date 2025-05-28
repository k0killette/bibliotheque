from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Loan(Base):
    """
    Modèle SQLAlchemy pour les emprunts de livres.
    """
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    is_returned = Column(Boolean, default=False, nullable=False, index=True)
    renewal_count = Column(Integer, default=0, nullable=False) # Permet de limiter le nombre de prolongations 
    fine_amount = Column(Integer, default=0, nullable=False)  # En centimes

    # Contraintes
    __table_args__ = (
        CheckConstraint('due_date > loan_date', name='check_due_date_after_loan'),
        CheckConstraint('return_date IS NULL OR return_date >= loan_date', name='check_return_date_after_loan'),
        CheckConstraint('renewal_count >= 0', name='check_renewal_count'),
        CheckConstraint('renewal_count <= 3', name='check_max_renewals'),
        CheckConstraint('fine_amount >= 0', name='check_fine_amount'),
        # Index composite pour les requêtes fréquentes
        Index('idx_loan_user_returned', 'user_id', 'is_returned'),
        Index('idx_loan_book_returned', 'book_id', 'is_returned'),
        Index('idx_loan_due_date_returned', 'due_date', 'is_returned'),
    )

    # Relations
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
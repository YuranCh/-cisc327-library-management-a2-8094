import pytest
from library_service import (
    borrow_book_by_patron
)

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_patron_id_too_long():
    """Test borrowing a book with patron ID too long."""
    success, message = borrow_book_by_patron("1234567", 1)
    
    assert success == False
    assert "6 digits" in message.lower()

def test_borrow_book_patron_id_too_short():
    """Test borrowing a book with patron ID too short."""
    success, message = borrow_book_by_patron("12345", 1)
    
    assert success == False
    assert "6 digits" in message.lower()

def test_borrow_book_patron_id_not_digits():
    """Test borrowing a book with patron ID not digits."""
    success, message = borrow_book_by_patron("abcdef", 1)

    assert success == False
    assert "6 digits" in message.lower()

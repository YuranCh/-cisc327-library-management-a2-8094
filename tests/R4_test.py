import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from library_service import (
    return_book_by_patron
)

def test_return_book_by_patron_valid_input():
    """Test returning a book with valid input."""
    # 123456 has borrowed books with IDs 2, 3, and 11
    success, message = return_book_by_patron("123456", 1)  
    
    assert success == True
    assert "successfully returned" in message.lower()

def test_return_book_by_patron_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    assert "6 digits" in message

def test_return_book_by_patron_invalid_book_id():
    """Test returning a book with invalid book ID."""
    success, message = return_book_by_patron("123456", 0)
    
    assert success == False
    assert "positive integer" in message

def test_return_book_by_patron_nonexistent_patron():
    """Test returning a book with non-existent patron."""
    success, message = return_book_by_patron("999999", 1)
    
    assert success == False
    assert "not found" in message.lower()

def test_return_book_by_patron_nonexistent_book():
    """Test returning a book with non-existent book."""
    success, message = return_book_by_patron("123456", 999)
    
    assert success == False
    assert "not found" in message.lower()

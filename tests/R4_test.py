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
    success, message = return_book_by_patron("123456", 2)  # Use book ID 2 which user has borrowed
    
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

# AI-Generated Test Cases for R4

def test_return_book_not_borrowed_by_patron():
    """AI-Generated: Test returning a book that was not borrowed by the specified patron."""
    # Try to return a book that exists but wasn't borrowed by this patron
    success, message = return_book_by_patron("123456", 1)  # Assuming book 1 exists but not borrowed by 123456
    
    assert success == False
    assert ("not borrowed" in message.lower() or 
            "not found" in message.lower() or 
            "not currently borrowed" in message.lower())

def test_return_book_already_returned():
    """AI-Generated: Test returning a book that has already been returned."""
    # First, successfully return a book
    return_success, return_msg = return_book_by_patron("123456", 2)
    
    # Then try to return the same book again
    success, message = return_book_by_patron("123456", 2)
    
    assert success == False
    assert ("already returned" in message.lower() or 
            "not currently borrowed" in message.lower() or
            "not found" in message.lower())

import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
     
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_empty_title():
    """Test adding a book with empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title" in message.lower()

def test_add_book_negative_copies():
    """Test adding a book with negative number of copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)
    
    assert success == False
    assert "positive" in message.lower()

def test_add_book_zero_copies():
    """Test adding a book with zero copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "positive" in message.lower()

# AI-Generated Test Cases for R1

def test_add_book_title_max_length():
    """AI-Generated: Test adding a book with title at maximum allowed length (200 chars)."""
    long_title = "A" * 200  # Exactly 200 characters
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_title_exceeds_max_length():
    """AI-Generated: Test adding a book with title exceeding maximum length (201 chars)."""
    too_long_title = "A" * 201  # 201 characters - exceeds limit
    success, message = add_book_to_catalog(too_long_title, "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "200 characters" in message
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from library_service import (
    search_books_in_catalog
)

def test_search_books_by_title():
    """Test searching books by title."""
    result = search_books_in_catalog("Test Book", "title")
    
    assert isinstance(result, list)
    # Should return books with matching titles

def test_search_books_by_author():
    """Test searching books by author."""
    result = search_books_in_catalog("Test Author", "author")
    
    assert isinstance(result, list)
    # Should return books with matching authors

def test_search_books_by_isbn():
    """Test searching books by ISBN."""
    result = search_books_in_catalog("1234567890123", "isbn")
    
    assert isinstance(result, list)
    # Should return books with exact ISBN match

def test_search_books_empty_search_term():
    """Test searching books with empty search term."""
    result = search_books_in_catalog("", "title")
    
    assert isinstance(result, list)
    assert len(result) == 0  # Empty search should return no results

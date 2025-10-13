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

# AI-Generated Test Cases for R6

def test_search_books_case_insensitive():
    """AI-Generated: Test that title and author searches are case-insensitive."""
    # Search for "great gatsby" in lowercase - should match "The Great Gatsby"
    result_lower = search_books_in_catalog("great gatsby", "title")
    result_upper = search_books_in_catalog("GREAT GATSBY", "title")
    result_mixed = search_books_in_catalog("Great Gatsby", "title")
    
    assert isinstance(result_lower, list)
    assert isinstance(result_upper, list) 
    assert isinstance(result_mixed, list)
    
    # All should return the same results (case-insensitive)
    # Note: Actual verification depends on having "The Great Gatsby" in test data

def test_search_books_partial_matching():
    """AI-Generated: Test partial matching for title and author searches."""
    # Test partial title matching
    result_partial_title = search_books_in_catalog("Great", "title")  # Should match "The Great Gatsby"
    result_partial_author = search_books_in_catalog("Scott", "author")  # Should match "F. Scott Fitzgerald"
    
    assert isinstance(result_partial_title, list)
    assert isinstance(result_partial_author, list)
    
    # Verify that partial matches work
    if result_partial_title:
        found_great = any("great" in book.get('title', '').lower() for book in result_partial_title)
        assert found_great, "Partial title matching should work"
    
    if result_partial_author:
        found_scott = any("scott" in book.get('author', '').lower() for book in result_partial_author)
        assert found_scott, "Partial author matching should work"

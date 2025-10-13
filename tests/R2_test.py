import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_all_books, insert_book, get_db_connection

def test_get_all_books_returns_list():
    """Test that get_all_books returns a list."""
    books = get_all_books()
    assert isinstance(books, list)

def test_get_all_books_contains_sample_data():
    """Test that get_all_books returns the sample data."""
    books = get_all_books()
    
    # Check if sample books are present
    titles = [book['title'] for book in books]
    assert 'The Great Gatsby' in titles
    assert 'To Kill a Mockingbird' in titles
    assert '1984' in titles

def test_get_all_books_structure():
    """Test that each book in the list has the required fields."""
    books = get_all_books()
    
    # Skip if no books are returned
    if not books:
        pytest.skip("No books in database")
    
    # Check the first book has all required fields
    book = books[0]
    assert 'id' in book
    assert 'title' in book
    assert 'author' in book
    assert 'isbn' in book
    assert 'total_copies' in book
    assert 'available_copies' in book

def test_get_all_books_sorted_by_title():
    """Test that books are returned sorted by title."""
    # Add books with titles that should be sorted
    insert_book("A Test Book", "Luke Skywalker", "1111111111111", 1, 1)
    insert_book("Z Test Book", "Peter Parker", "2222222222222", 1, 1)
    insert_book("M Test Book", "Alice Jana", "3333333333333", 1, 1)
    
    books = get_all_books()
    
    # Extract titles
    titles = [book['title'] for book in books]
    
    # Check if titles are in alphabetical order
    sorted_titles = sorted(titles)
    assert titles == sorted_titles

def test_get_all_books_after_adding_new_book():
    """Test that get_all_books returns newly added books."""
    # Add a unique book
    unique_title = "Unique Test Book"
    unique_isbn = "9999999999999"
    insert_book(unique_title, "Test Author", unique_isbn, 3, 3)
    
    # Get all books
    books = get_all_books()
    
    # Check if the new book is in the results
    found = False
    for book in books:
        if book['title'] == unique_title and book['isbn'] == unique_isbn:
            found = True
            assert book['total_copies'] == 3
            assert book['available_copies'] == 3
            break
    
    assert found, "Newly added book not found in get_all_books results"

def test_get_all_books_empty_database():
    """Test get_all_books with an empty database."""
    # Clear the books table
    conn = get_db_connection()
    conn.execute("DELETE FROM books")
    conn.commit()
    conn.close()
    
    books = get_all_books()
    assert isinstance(books, list)
    assert len(books) == 0

# AI-Generated Test Cases for R2

def test_get_all_books_with_zero_available_copies():
    """AI-Generated: Test that books with zero available copies are still returned in catalog."""
    # Add a book with zero available copies
    insert_book("Unavailable Book", "Test Author", "5555555555555", 5, 0)
    
    books = get_all_books()
    unavailable_books = [book for book in books if book['available_copies'] == 0]
    
    assert len(unavailable_books) > 0
    # Verify the book is in the results even with 0 available copies
    found = any(book['title'] == "Unavailable Book" for book in books)
    assert found, "Books with zero available copies should still appear in catalog"

def test_get_all_books_data_integrity():
    """AI-Generated: Test that available_copies never exceeds total_copies in catalog display."""
    books = get_all_books()
    
    for book in books:
        assert book['available_copies'] <= book['total_copies'], \
            f"Available copies ({book['available_copies']}) exceeds total copies ({book['total_copies']}) for book: {book['title']}"
        assert book['available_copies'] >= 0, \
            f"Available copies cannot be negative for book: {book['title']}"
        assert book['total_copies'] > 0, \
            f"Total copies must be positive for book: {book['title']}"
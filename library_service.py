"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_all_books, get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_db_connection
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.

    TODO: Implement R4 as per requirements
    """
    # Use R5 API to calculate late fees and validate the borrow relationship
    late_fee_result = calculate_late_fee_for_book(patron_id, book_id)
    
    # Check if there was an error in the late fee calculation
    if late_fee_result['status'] not in ['Success', 'Overdue by 0 days'] and 'Overdue by' not in late_fee_result['status']:
        # If it's an error message, return it as failure
        return False, late_fee_result['status']
    
    # Get book information for success message
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Update book availability (+1)
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Record return date
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "Database error occurred while recording return date."
    
    # Prepare success message using R5 results
    message = f'Successfully returned "{book["title"]}".'
    if late_fee_result['fee_amount'] > 0:
        message += f' Late fee: ${late_fee_result["fee_amount"]:.2f} ({late_fee_result["days_overdue"]} days overdue).'
    else:
        message += ' No late fees.'
    
    return True, message

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID. Must be exactly 6 digits.'
        }
    
    # Validate book ID
    if not isinstance(book_id, int) or book_id <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid book ID. Must be a positive integer.'
        }
        
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found.'
        }

    # Check if the book is currently borrowed by the patron
    conn = get_db_connection()
    borrow_record = conn.execute('''
        SELECT * FROM borrow_records 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (patron_id, book_id)).fetchone()
    conn.close()

    if not borrow_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book is not currently borrowed by the patron.'
        }

    # Calculate late fees based on R5 requirements
    due_date = datetime.fromisoformat(borrow_record['due_date'])
    current_date = datetime.now()
    days_overdue = max(0, (current_date - due_date).days)
    
    late_fee = 0.0
    if days_overdue > 0:
        if days_overdue <= 7:
            # $0.50/day for first 7 days overdue
            late_fee = days_overdue * 0.50
        else:
            # $0.50/day for first 7 days + $1.00/day for additional days
            late_fee = 7 * 0.50 + (days_overdue - 7) * 1.00
        # Maximum $15.00 per book
        late_fee = min(late_fee, 15.00)

    return {
        'fee_amount': late_fee,
        'days_overdue': days_overdue,
        'status': 'Success' if days_overdue == 0 else f'Overdue by {days_overdue} days'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    return {}

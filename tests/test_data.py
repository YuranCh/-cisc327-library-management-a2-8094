"""
Test data management module.
Provides functions to initialize and reset the test database.
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_db_connection

def initialize_test_data():
    """
    Initialize test database with data that meets R1-R7 test requirements.
    This function clears existing data and adds new test data.
    """
    conn = get_db_connection()
    
    # Clear existing data and reset auto-increment
    conn.execute("DELETE FROM borrow_records")
    conn.execute("DELETE FROM books")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='books'")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='borrow_records'")
    conn.commit()
    
    # Add test books
    books = [
        # Basic books - for general testing
        ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 3, 3),  # id=1, all available
        ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2, 1),      # id=2, partially available
        ('1984', 'George Orwell', '9780451524935', 1, 0),                    # id=3, all borrowed
        
        # Books for sorting tests
        ('A Test Book', 'Test Author A', '9780000000001', 1, 1),             # id=4
        ('Z Test Book', 'Test Author Z', '9780000000002', 1, 1),             # id=5
        ('M Test Book', 'Test Author M', '9780000000003', 1, 1),             # id=6
        
        # Books for borrowing and returning tests
        ('Available Book 1', 'Borrow Author', '9780000000004', 2, 2),        # id=7, available
        ('Available Book 2', 'Borrow Author', '9780000000005', 1, 1),        # id=8, available
        ('Borrowed Book 1', 'Return Author', '9780000000006', 1, 0),         # id=9, borrowed
        ('Borrowed Book 2', 'Return Author', '9780000000007', 1, 0),         # id=10, borrowed
        
        # Books for late fee tests
        ('Overdue Book', 'Fee Author', '9780000000008', 1, 0),               # id=11, overdue
    ]
    
    for title, author, isbn, total, available in books:
        conn.execute('''
            INSERT INTO books (title, author, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, author, isbn, total, available))
    
    # Add borrowing records
    now = datetime.now()
    borrow_records = [
        # Regular borrowing record - for book id=2, partially borrowed
        ('123456', 2, (now - timedelta(days=3)).isoformat(), (now + timedelta(days=11)).isoformat(), None),
        
        # Fully borrowed book - for id=3
        ('123456', 3, (now - timedelta(days=5)).isoformat(), (now + timedelta(days=9)).isoformat(), None),
        
        # Books for return testing - id=9, id=10
        # Note: We leave book id=7 available for borrowing tests
        ('654321', 9, (now - timedelta(days=2)).isoformat(), (now + timedelta(days=12)).isoformat(), None),
        ('654321', 10, (now - timedelta(days=4)).isoformat(), (now + timedelta(days=10)).isoformat(), None),
        
        # Book for late fee testing - id=11, overdue
        ('123456', 11, (now - timedelta(days=20)).isoformat(), (now - timedelta(days=6)).isoformat(), None),
    ]
    
    for patron_id, book_id, borrow_date, due_date, return_date in borrow_records:
        conn.execute('''
            INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date, return_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (patron_id, book_id, borrow_date, due_date, return_date))
    
    conn.commit()
    conn.close()

def reset_test_data():
    """
    Reset the test database to its initial state.
    This function clears existing data and re-adds the test data.
    """
    initialize_test_data()

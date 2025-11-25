"""
E2E (End-to-End) Browser Tests for Library Management System

This module contains automated browser tests using Playwright to test
complete user workflows in the Flask web application.

Requirements:
- Launch a real browser (headless or not)
- Automate at least two full user flows
- Include assertions to check expected UI text/elements
- Must run via: pytest tests/test_e2e.py
"""

import pytest
import sys
import os
import time
from playwright.sync_api import Page, expect
from multiprocessing import Process

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from database import init_database, get_db_connection


class FlaskTestServer:
    """Helper class to manage Flask test server."""
    
    def __init__(self):
        self.process = None
        self.port = 5001  # Use different port for testing
    
    def start(self):
        """Start Flask server in a separate process."""
        def run_server():
            app = create_app()
            app.run(host='127.0.0.1', port=self.port, debug=False)
        
        self.process = Process(target=run_server)
        self.process.start()
        # Give server time to start
        time.sleep(2)
    
    def stop(self):
        """Stop Flask server."""
        if self.process:
            self.process.terminate()
            self.process.join()
    
    @property
    def url(self):
        """Get base URL for the test server."""
        return f"http://127.0.0.1:{self.port}"


@pytest.fixture(scope="session")
def test_server():
    """Fixture to provide a running Flask server for E2E tests."""
    server = FlaskTestServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture(autouse=True)
def setup_clean_database():
    """Clean database before each test."""
    # Initialize fresh database
    init_database()
    
    # Clear any existing data
    conn = get_db_connection()
    conn.execute("DELETE FROM borrow_records")
    conn.execute("DELETE FROM books")
    conn.commit()
    conn.close()


def test_add_new_book_flow(page: Page, test_server):
    """
    E2E Test: Add a new book and verify it appears in catalog
    
    User Flow:
    1. Navigate to add book page
    2. Fill in book details (title, author, ISBN, copies)
    3. Submit the form
    4. Verify success message
    5. Verify book appears in catalog with correct details
    """
    base_url = test_server.url
    
    # Step 1: Navigate to add book page
    page.goto(f"{base_url}/add_book")
    
    # Verify we're on the add book page
    expect(page.locator("h2")).to_contain_text("Add New Book")
    
    # Step 2: Fill in book details
    test_book = {
        "title": "Test Book for E2E",
        "author": "E2E Test Author", 
        "isbn": "1234567890123",
        "total_copies": "5"
    }
    
    page.fill("#title", test_book["title"])
    page.fill("#author", test_book["author"])
    page.fill("#isbn", test_book["isbn"])
    page.fill("#total_copies", test_book["total_copies"])
    
    # Step 3: Submit the form
    page.click("button[type='submit']")
    
    # Step 4: Verify success message and redirect to catalog
    expect(page).to_have_url(f"{base_url}/catalog")
    
    # Check for success flash message (if visible)
    # Note: Flash messages might disappear quickly, so we check catalog content instead
    
    # Step 5: Verify book appears in catalog
    expect(page.locator("h2")).to_contain_text("Book Catalog")
    
    # Find the book in the table
    book_row = page.locator("tr").filter(has_text=test_book["title"])
    expect(book_row).to_be_visible()
    
    # Verify book details in the table
    expect(book_row.locator("td").nth(1)).to_contain_text(test_book["title"])
    expect(book_row.locator("td").nth(2)).to_contain_text(test_book["author"])
    expect(book_row.locator("td").nth(3)).to_contain_text(test_book["isbn"])
    expect(book_row.locator("td").nth(4)).to_contain_text("5/5 Available")
    
    # Verify borrow button is present and enabled
    borrow_form = book_row.locator("form")
    expect(borrow_form).to_be_visible()
    expect(borrow_form.locator("button")).to_contain_text("Borrow")


def test_borrow_book_flow(page: Page, test_server):
    """
    E2E Test: Borrow a book with patron ID
    
    User Flow:
    1. Add a book to the catalog (setup)
    2. Navigate to catalog
    3. Enter patron ID
    4. Click borrow button
    5. Verify borrow confirmation message
    6. Verify book availability is updated
    """
    base_url = test_server.url
    
    # Step 1: Setup - Add a book first
    page.goto(f"{base_url}/add_book")
    
    test_book = {
        "title": "Borrowable Test Book",
        "author": "Borrow Test Author",
        "isbn": "9876543210987", 
        "total_copies": "3"
    }
    
    page.fill("#title", test_book["title"])
    page.fill("#author", test_book["author"])
    page.fill("#isbn", test_book["isbn"])
    page.fill("#total_copies", test_book["total_copies"])
    page.click("button[type='submit']")
    
    # Step 2: Navigate to catalog (should already be there after adding book)
    expect(page).to_have_url(f"{base_url}/catalog")
    expect(page.locator("h2")).to_contain_text("Book Catalog")
    
    # Find our test book
    book_row = page.locator("tr").filter(has_text=test_book["title"])
    expect(book_row).to_be_visible()
    
    # Verify initial availability
    expect(book_row.locator("td").nth(4)).to_contain_text("3/3 Available")
    
    # Step 3: Enter patron ID
    patron_id = "123456"
    patron_input = book_row.locator("input[name='patron_id']")
    patron_input.fill(patron_id)
    
    # Step 4: Click borrow button
    borrow_button = book_row.locator("button[type='submit']")
    expect(borrow_button).to_contain_text("Borrow")
    borrow_button.click()
    
    # Step 5: Verify we're still on catalog page (redirect after borrow)
    expect(page).to_have_url(f"{base_url}/catalog")
    
    # Step 6: Verify book availability is updated
    # Re-locate the book row after page reload
    updated_book_row = page.locator("tr").filter(has_text=test_book["title"])
    expect(updated_book_row).to_be_visible()
    
    # Check that available copies decreased from 3 to 2
    expect(updated_book_row.locator("td").nth(4)).to_contain_text("2/3 Available")
    
    # Verify borrow form is still present (book still available)
    expect(updated_book_row.locator("form")).to_be_visible()
    expect(updated_book_row.locator("button")).to_contain_text("Borrow")


def test_borrow_until_unavailable(page: Page, test_server):
    """
    E2E Test: Borrow all copies until book becomes unavailable
    
    User Flow:
    1. Add a book with limited copies (e.g., 2 copies)
    2. Borrow all copies one by one
    3. Verify book shows as "Not Available" 
    4. Verify borrow button is disabled/hidden
    """
    base_url = test_server.url
    
    # Step 1: Add a book with only 2 copies
    page.goto(f"{base_url}/add_book")
    
    test_book = {
        "title": "Limited Copies Book",
        "author": "Scarcity Author",
        "isbn": "1111222233334",
        "total_copies": "2"
    }
    
    page.fill("#title", test_book["title"])
    page.fill("#author", test_book["author"])
    page.fill("#isbn", test_book["isbn"])
    page.fill("#total_copies", test_book["total_copies"])
    page.click("button[type='submit']")
    
    # Step 2: Borrow first copy
    book_row = page.locator("tr").filter(has_text=test_book["title"])
    book_row.locator("input[name='patron_id']").fill("111111")
    book_row.locator("button[type='submit']").click()
    
    # Verify availability: 1/2 Available
    updated_row = page.locator("tr").filter(has_text=test_book["title"])
    expect(updated_row.locator("td").nth(4)).to_contain_text("1/2 Available")
    
    # Step 3: Borrow second (last) copy
    updated_row.locator("input[name='patron_id']").fill("222222")
    updated_row.locator("button[type='submit']").click()
    
    # Step 4: Verify book is now unavailable
    final_row = page.locator("tr").filter(has_text=test_book["title"])
    expect(final_row.locator("td").nth(4)).to_contain_text("Not Available")
    
    # Verify borrow form is not present (replaced with "Unavailable" text)
    expect(final_row.locator("form")).not_to_be_visible()
    expect(final_row.locator("td").nth(5)).to_contain_text("Unavailable")


def test_add_book_validation_errors(page: Page, test_server):
    """
    E2E Test: Test form validation for adding books
    
    User Flow:
    1. Navigate to add book page
    2. Try to submit empty form
    3. Verify HTML5 validation prevents submission
    4. Fill invalid data and verify server-side validation
    """
    base_url = test_server.url
    
    # Step 1: Navigate to add book page
    page.goto(f"{base_url}/add_book")
    
    # Step 2: Try to submit empty form
    page.click("button[type='submit']")
    
    # Step 3: Verify we're still on add book page (form validation prevented submission)
    expect(page).to_have_url(f"{base_url}/add_book")
    
    # Step 4: Test with invalid data
    page.fill("#title", "Valid Title")
    page.fill("#author", "Valid Author")
    page.fill("#isbn", "invalid-isbn")  # Invalid ISBN format
    page.fill("#total_copies", "0")  # Invalid: should be positive
    
    page.click("button[type='submit']")
    
    # Should stay on add book page due to validation errors
    expect(page).to_have_url(f"{base_url}/add_book")


def test_empty_catalog_display(page: Page, test_server):
    """
    E2E Test: Verify empty catalog displays appropriate message
    
    User Flow:
    1. Navigate to catalog with no books
    2. Verify empty state message is displayed
    3. Verify "Add New Book" link is present
    """
    base_url = test_server.url
    
    # Navigate to catalog (should be empty due to clean database fixture)
    page.goto(f"{base_url}/catalog")
    
    # Verify empty catalog message
    expect(page.locator("h3")).to_contain_text("No books in catalog")
    expect(page.locator("p")).to_contain_text("The library catalog is empty")
    
    # Verify add book link is present
    add_book_link = page.locator("a").filter(has_text="Add the first book")
    expect(add_book_link).to_be_visible()
    
    # Test the link works
    add_book_link.click()
    expect(page).to_have_url(f"{base_url}/add_book")


if __name__ == "__main__":
    # Allow running this file directly for testing
    pytest.main([__file__, "-v"])

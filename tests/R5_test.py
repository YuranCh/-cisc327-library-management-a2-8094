import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from library_service import (
    calculate_late_fee_for_book
)

def test_calculate_late_fee_valid_input():
    """Test calculating late fee with valid input."""
    # 123456 has borrowed books with IDs 2, 3, and 11
    result = calculate_late_fee_for_book("123456", 11)  # Use book 11 which is overdue
    
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result
    assert isinstance(result['fee_amount'], float)
    assert isinstance(result['days_overdue'], int)
    assert isinstance(result['status'], str)

def test_calculate_late_fee_invalid_patron_id():
    """Test calculating late fee with invalid patron ID."""
    result = calculate_late_fee_for_book("12345", 1)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "6 digits" in result['status']

def test_calculate_late_fee_invalid_book_id():
    """Test calculating late fee with invalid book ID."""
    result = calculate_late_fee_for_book("123456", 0)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "positive integer" in result['status']

def test_calculate_late_fee_nonexistent_patron():
    """Test calculating late fee with non-existent patron."""
    result = calculate_late_fee_for_book("999999", 1)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "not found" in result['status'].lower()

def test_calculate_late_fee_nonexistent_book():
    """Test calculating late fee with non-existent book."""
    result = calculate_late_fee_for_book("123456", 999)
    
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert "not found" in result['status'].lower()


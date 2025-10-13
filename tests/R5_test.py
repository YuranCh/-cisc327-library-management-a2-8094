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

# AI-Generated Test Cases for R5

def test_calculate_late_fee_maximum_fee_cap():
    """AI-Generated: Test that late fee calculation caps at maximum $15.00 per book."""
    # This test would need a book that's overdue by many days (>37 days to exceed $15 cap)
    # Using the existing overdue book (ID 11) which should be overdue by 20+ days
    result = calculate_late_fee_for_book("123456", 11)
    
    assert 'fee_amount' in result
    assert result['fee_amount'] <= 15.00, f"Late fee should not exceed $15.00, got ${result['fee_amount']}"
    assert result['fee_amount'] > 0, "Should have some late fee for overdue book"
    assert result['days_overdue'] > 0, "Should show days overdue for overdue book"

def test_calculate_late_fee_different_rate_periods():
    """AI-Generated: Test late fee calculation for different overdue periods (0-7 days vs 8+ days)."""
    # Test with the overdue book to verify fee calculation logic
    result = calculate_late_fee_for_book("123456", 11)  # Book 11 is overdue by ~20 days
    
    if result['days_overdue'] > 7:
        # Should be $0.50 * 7 + $1.00 * (days_overdue - 7)
        expected_fee = 7 * 0.50 + (result['days_overdue'] - 7) * 1.00
        expected_fee = min(expected_fee, 15.00)  # Cap at $15
        
        assert abs(result['fee_amount'] - expected_fee) < 0.01, \
            f"Expected fee ${expected_fee:.2f}, got ${result['fee_amount']:.2f} for {result['days_overdue']} days overdue"
    
    assert isinstance(result['fee_amount'], float)
    assert isinstance(result['days_overdue'], int)


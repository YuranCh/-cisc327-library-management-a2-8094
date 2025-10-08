import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from library_service import (
    get_patron_status_report
)

def test_get_patron_status_valid_patron():
    """Test getting patron status with valid patron ID."""
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    # Should contain patron status information
    assert 'currently_borrowed' in result or 'borrowed_books' in result
    assert 'total_late_fees' in result or 'late_fees' in result
    assert 'books_borrowed_count' in result or 'borrowed_count' in result
    assert 'borrowing_history' in result or 'history' in result

def test_get_patron_status_invalid_patron_id():
    """Test getting patron status with invalid patron ID."""
    result = get_patron_status_report("12345")
    
    assert isinstance(result, dict)
    assert 'error' in result or 'message' in result
    assert "6 digits" in str(result.get('error', result.get('message', '')))

def test_get_patron_status_nonexistent_patron():
    """Test getting patron status with non-existent patron."""
    result = get_patron_status_report("999999")
    
    assert isinstance(result, dict)
    assert 'error' in result or 'message' in result
    assert "not found" in str(result.get('error', result.get('message', ''))).lower()

def test_get_patron_status_empty_patron_id():
    """Test getting patron status with empty patron ID."""
    result = get_patron_status_report("")
    
    assert isinstance(result, dict)
    assert 'error' in result or 'message' in result
    assert "6 digits" in str(result.get('error', result.get('message', '')))

def test_get_patron_status_none_patron_id():
    """Test getting patron status with None patron ID."""
    result = get_patron_status_report(None)
    
    assert isinstance(result, dict)
    assert 'error' in result or 'message' in result
    assert "6 digits" in str(result.get('error', result.get('message', '')))

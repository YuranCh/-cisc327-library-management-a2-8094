"""
Test file for payment service mocking and stubbing.
This file tests the pay_late_fees and refund_late_fee_payment functions
using mocking and stubbing techniques.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.payment_service import PaymentGateway
from services.library_service import (
    pay_late_fees, refund_late_fee_payment,
    add_book_to_catalog, borrow_book_by_patron, return_book_by_patron,
    search_books_in_catalog, get_patron_status_report
)

# ========== Tests for pay_late_fees using mocking and stubbing ==========

@pytest.mark.parametrize("fee_amount, expected_success", [
    (10.0, True),   # Successful payment
    (0.0, False),   # No fees to pay
])
def test_pay_late_fees_success_cases(mocker, fee_amount, expected_success):
    """Test pay_late_fees with successful payment and no fees cases."""
    # Stub the calculate_late_fee_for_book function to return a predetermined fee
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': fee_amount, 'days_overdue': 5, 'status': 'Overdue by 5 days'}
    )
    
    # Stub the get_book_by_id function to return a test book
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'}
    )
    
    # Mock the PaymentGateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123456", "Success")
    
    # Call the function
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    
    # Assertions
    assert success == expected_success
    if expected_success:
        assert transaction_id == "txn_123456"
        assert "Payment successful" in message
        # Verify the mock was called with correct parameters
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=fee_amount,
            description="Late fees for 'Test Book'"
        )
    else:
        assert transaction_id is None
        assert "No late fees to pay" in message
        # Verify the mock was NOT called
        mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_declined_payment(mocker):
    """Test pay_late_fees when payment is declined by the gateway."""
    # Stub the calculate_late_fee_for_book function
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 10.0, 'days_overdue': 5, 'status': 'Overdue by 5 days'}
    )
    
    # Stub the get_book_by_id function
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'}
    )
    
    # Mock the PaymentGateway with declined payment
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Payment declined")
    
    # Call the function
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    
    # Assertions
    assert success is False
    assert transaction_id is None
    assert "Payment failed" in message
    # Verify the mock was called
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron_id():
    """Test pay_late_fees with invalid patron ID."""
    # No need to mock anything as validation happens before external calls
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Call with invalid patron ID
    success, message, transaction_id = pay_late_fees("12345", 1, mock_gateway)  # 5 digits instead of 6
    
    # Assertions
    assert success is False
    assert "Invalid patron ID" in message
    assert transaction_id is None
    # Verify the mock was NOT called
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    """Test pay_late_fees handling network/exception errors."""
    # Stub the calculate_late_fee_for_book function
    mocker.patch(
        'services.library_service.calculate_late_fee_for_book',
        return_value={'fee_amount': 10.0, 'days_overdue': 5, 'status': 'Overdue by 5 days'}
    )
    
    # Stub the get_book_by_id function
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'}
    )
    
    # Mock the PaymentGateway to raise an exception
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network error")
    
    # Call the function
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    
    # Assertions
    assert success is False
    assert "error" in message.lower()
    assert transaction_id is None
    # Verify the mock was called
    mock_gateway.process_payment.assert_called_once()


# ========== Tests for refund_late_fee_payment using mocking ==========

def test_refund_late_fee_payment_success():
    """Test successful refund of late fee payment."""
    # Mock the PaymentGateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund processed successfully")
    
    # Call the function
    success, message = refund_late_fee_payment("txn_123456", 10.0, mock_gateway)
    
    # Assertions
    assert success is True
    assert "successfully" in message.lower()
    # Verify the mock was called with correct parameters
    mock_gateway.refund_payment.assert_called_once_with("txn_123456", 10.0)


def test_refund_late_fee_payment_invalid_transaction_id():
    """Test refund with invalid transaction ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Call with invalid transaction ID
    success, message = refund_late_fee_payment("invalid_id", 10.0, mock_gateway)
    
    # Assertions
    assert success is False
    assert "Invalid transaction ID" in message
    # Verify the mock was NOT called
    mock_gateway.refund_payment.assert_not_called()


@pytest.mark.parametrize("amount, expected_message", [
    (0.0, "Refund amount must be greater than 0"),
    (-5.0, "Refund amount must be greater than 0"),
    (20.0, "Refund amount exceeds maximum late fee")
])
def test_refund_late_fee_payment_invalid_amounts(amount, expected_message):
    """Test refund with invalid amounts (negative, zero, exceeds maximum)."""
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Call with invalid amount
    success, message = refund_late_fee_payment("txn_123456", amount, mock_gateway)
    
    # Assertions
    assert success is False
    assert expected_message in message
    # Verify the mock was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_gateway_error():
    """Test refund handling gateway errors."""
    # Mock the PaymentGateway to raise an exception
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = Exception("Gateway error")
    
    # Call the function
    success, message = refund_late_fee_payment("txn_123456", 10.0, mock_gateway)
    
    # Assertions
    assert success is False
    assert "error" in message.lower()
    # Verify the mock was called
    mock_gateway.refund_payment.assert_called_once()


# ========== Additional tests for PaymentGateway class ==========

def test_payment_gateway_initialization():
    """Test PaymentGateway initialization with default and custom API key."""
    # Default API key
    gateway = PaymentGateway()
    assert gateway.api_key == "test_key_12345"
    assert gateway.base_url == "https://api.payment-gateway.example.com"
    
    # Custom API key
    custom_gateway = PaymentGateway(api_key="custom_key")
    assert custom_gateway.api_key == "custom_key"
    assert custom_gateway.base_url == "https://api.payment-gateway.example.com"


def test_payment_gateway_process_payment_directly():
    """Test PaymentGateway.process_payment method directly."""
    gateway = PaymentGateway()
    
    # Test valid payment
    success, txn_id, message = gateway.process_payment("123456", 10.0, "Test payment")
    assert success is True
    assert txn_id.startswith("txn_")
    assert "processed successfully" in message
    
    # Test invalid amount (zero)
    success, txn_id, message = gateway.process_payment("123456", 0.0, "Test payment")
    assert success is False
    assert txn_id == ""
    assert "Invalid amount" in message
    
    # Test invalid amount (too large)
    success, txn_id, message = gateway.process_payment("123456", 1500.0, "Test payment")
    assert success is False
    assert txn_id == ""
    assert "declined" in message
    
    # Test invalid patron ID
    success, txn_id, message = gateway.process_payment("12345", 10.0, "Test payment")
    assert success is False
    assert txn_id == ""
    assert "Invalid patron ID" in message


def test_payment_gateway_refund_payment_directly():
    """Test PaymentGateway.refund_payment method directly."""
    gateway = PaymentGateway()
    
    # Test valid refund
    success, message = gateway.refund_payment("txn_123456", 10.0)
    assert success is True
    assert "processed successfully" in message
    assert "Refund ID" in message
    
    # Test invalid transaction ID
    success, message = gateway.refund_payment("invalid_id", 10.0)
    assert success is False
    assert "Invalid transaction ID" in message
    
    # Test invalid refund amount
    success, message = gateway.refund_payment("txn_123456", 0.0)
    assert success is False
    assert "Invalid refund amount" in message


def test_payment_gateway_verify_payment_status():
    """Test PaymentGateway.verify_payment_status method."""
    gateway = PaymentGateway()
    
    # Test valid transaction ID
    result = gateway.verify_payment_status("txn_123456")
    assert isinstance(result, dict)
    assert result["status"] == "completed"
    assert result["transaction_id"] == "txn_123456"
    assert "amount" in result
    assert "timestamp" in result
    
    # Test invalid transaction ID
    result = gateway.verify_payment_status("invalid_id")
    assert isinstance(result, dict)
    assert result["status"] == "not_found"
    assert "message" in result


# Tests for add_book_to_catalog function
def test_add_book_author_too_long():
    """Test adding a book with author name too long."""
    long_author = "A" * 101  # 101 characters - exceeds limit
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)
    
    assert success is False
    assert "Author must be less than 100 characters" in message

def test_add_book_duplicate_isbn_error():
    """Test adding a book with duplicate ISBN."""
    # First add a book
    add_book_to_catalog("Original Book", "Original Author", "9999999999999", 1)
    
    # Try to add another book with the same ISBN
    success, message = add_book_to_catalog("Duplicate Book", "Another Author", "9999999999999", 1)
    
    assert success is False
    assert "already exists" in message.lower()

def test_add_book_database_error(mocker):
    """Test database error when adding a book."""
    # Mock the insert_book function to return False (database error)
    mocker.patch('services.library_service.insert_book', return_value=False)
    
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success is False
    assert "database error" in message.lower()

# Tests for borrow_book_by_patron function
def test_borrow_book_database_error_borrow_record(mocker):
    """Test database error when creating borrow record."""
    # Mock the get_book_by_id function
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book', 'available_copies': 1})
    
    # Mock the get_patron_borrow_count function
    mocker.patch('services.library_service.get_patron_borrow_count', return_value=3)
    
    # Mock the insert_borrow_record function to return False (database error)
    mocker.patch('services.library_service.insert_borrow_record', return_value=False)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is False
    assert "database error" in message.lower()
    assert "borrow record" in message.lower()

def test_borrow_book_database_error_availability(mocker):
    """Test database error when updating book availability."""
    # Mock the get_book_by_id function
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book', 'available_copies': 1})
    
    # Mock the get_patron_borrow_count function
    mocker.patch('services.library_service.get_patron_borrow_count', return_value=3)
    
    # Mock the insert_borrow_record function to return True
    mocker.patch('services.library_service.insert_borrow_record', return_value=True)
    
    # Mock the update_book_availability function to return False (database error)
    mocker.patch('services.library_service.update_book_availability', return_value=False)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is False
    assert "database error" in message.lower()
    assert "availability" in message.lower()

def test_borrow_book_over_limit(mocker):
    """Test borrowing when patron has reached limit."""
    # Mock the get_book_by_id function to return a valid book
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 20, 'title': 'Test Book', 'available_copies': 5})
    
    # Mock get_patron_borrow_count to return 6 (over the limit of 5)
    mocker.patch('services.library_service.get_patron_borrow_count', return_value=6)
    
    # Try to borrow a book
    success, message = borrow_book_by_patron("123456", 20)
    
    assert success is False
    assert "limit" in message.lower() or "maximum" in message.lower()

# Tests for return_book_by_patron function
def test_return_book_database_error_availability(mocker):
    """Test database error when updating book availability during return."""
    # Mock the calculate_late_fee_for_book function
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                return_value={'status': 'Success', 'fee_amount': 0, 'days_overdue': 0})
    
    # Mock the get_book_by_id function
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book'})
    
    # Mock the update_book_availability function to return False (database error)
    mocker.patch('services.library_service.update_book_availability', return_value=False)
    
    success, message = return_book_by_patron("123456", 1)
    
    assert success is False
    assert "database error" in message.lower()
    assert "availability" in message.lower()

def test_return_book_database_error_return_date(mocker):
    """Test database error when recording return date."""
    # Mock the calculate_late_fee_for_book function
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                return_value={'status': 'Success', 'fee_amount': 0, 'days_overdue': 0})
    
    # Mock the get_book_by_id function
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book'})
    
    # Mock the update_book_availability function to return True
    mocker.patch('services.library_service.update_book_availability', return_value=True)
    
    # Mock the update_borrow_record_return_date function to return False (database error)
    mocker.patch('services.library_service.update_borrow_record_return_date', return_value=False)
    
    success, message = return_book_by_patron("123456", 1)
    
    assert success is False
    assert "database error" in message.lower()
    assert "return date" in message.lower()

def test_return_book_with_late_fee(mocker):
    """Test returning a book with late fee."""
    # Mock the calculate_late_fee_for_book function to return a late fee
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                return_value={'status': 'Overdue by 5 days', 'fee_amount': 2.5, 'days_overdue': 5})
    
    # Mock the get_book_by_id function
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book'})
    
    # Mock the update functions to return True
    mocker.patch('services.library_service.update_book_availability', return_value=True)
    mocker.patch('services.library_service.update_borrow_record_return_date', return_value=True)
    
    success, message = return_book_by_patron("123456", 1)
    
    assert success is True
    assert "late fee: $2.50" in message.lower()
    assert "5 days overdue" in message.lower()

# Tests for search_books_in_catalog function
def test_search_books_invalid_search_type():
    """Test searching books with invalid search type."""
    result = search_books_in_catalog("Test", "invalid_type")
    
    assert isinstance(result, list)
    assert len(result) == 0

# Tests for get_patron_status_report function
def test_patron_status_with_return_date(mocker):
    """Test patron status report with return dates in history."""
    # Mock the get_patron_borrowed_books function
    mocker.patch('services.library_service.get_patron_borrowed_books', return_value=[])
    
    # Mock database connection and execute
    mock_conn = MagicMock()
    mock_fetchone = MagicMock()
    mock_fetchone.__getitem__.return_value = 1  # Return 1 for the count
    mock_conn.execute.return_value.fetchone.return_value = mock_fetchone
    
    mock_records = [
        {
            'book_id': 1, 
            'title': 'Test Book', 
            'author': 'Test Author',
            'borrow_date': '2023-01-01T10:00:00', 
            'due_date': '2023-01-15T10:00:00',
            'return_date': '2023-01-10T10:00:00'  # Has return date
        }
    ]
    mock_conn.execute.return_value.fetchall.return_value = mock_records
    mocker.patch('services.library_service.get_db_connection', return_value=mock_conn)
    
    # Mock the calculate_late_fee_for_book function
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                return_value={'fee_amount': 0})
    
    result = get_patron_status_report("123456")
    
    # Check that the result has borrowing history
    assert 'borrowing_history' in result
    # We can't check the exact content because our mocking is incomplete,
    # but we can verify the function ran without errors
    
    assert 'borrowing_history' in result
    assert len(result['borrowing_history']) == 1
    assert 'return_date' in result['borrowing_history'][0]

# Tests for pay_late_fees function
def test_pay_late_fees_create_gateway(mocker):
    """Test pay_late_fees creates a new gateway if none provided."""
    # We need to mock get_book_by_id first to avoid early return
    mocker.patch('services.library_service.get_book_by_id', 
                return_value={'id': 1, 'title': 'Test Book'})
    
    # Mock calculate_late_fee_for_book to return a positive fee
    mocker.patch('services.library_service.calculate_late_fee_for_book', 
                return_value={'fee_amount': 5.0, 'status': 'Overdue by 5 days'})
    
    # Create a real gateway instance to verify code path
    from services.payment_service import PaymentGateway
    
    # Use patch.object to spy on the constructor
    with patch('services.library_service.PaymentGateway', wraps=PaymentGateway) as spy:
        # Call the function without providing a gateway
        pay_late_fees("123456", 1)
        
        # Verify the constructor was called
        assert spy.call_count > 0, "PaymentGateway constructor should be called"
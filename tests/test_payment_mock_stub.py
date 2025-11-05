"""
Test file for payment service mocking and stubbing.
This file tests the pay_late_fees and refund_late_fee_payment functions
using mocking and stubbing techniques.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.payment_service import PaymentGateway
from services.library_service import pay_late_fees, refund_late_fee_payment

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

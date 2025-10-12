"""
Test configuration for pytest.
"""

import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import use_temp_database, reset_temp_database, cleanup_temp_database
from tests.test_data import initialize_test_data, reset_test_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment with temporary database."""
    # Create and initialize temporary database
    use_temp_database()
    
    # Initialize with specialized test data
    initialize_test_data()
    
    yield
    
    # Clean up temporary database
    cleanup_temp_database()

@pytest.fixture(autouse=True)
def reset_database_after_test():
    """Reset the database after each test."""
    # Test runs here
    yield
    
    # Reset database to initial test data state
    reset_test_data()

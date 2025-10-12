# Test Database Isolation and Specialized Test Dataset

This project uses thread-local storage and temporary databases to implement test isolation, ensuring tests don't pollute the main database. It also provides a specialized test dataset that meets all test requirements.

## How It Works

1. **Temporary Database**:
   - Each test process/thread uses its own temporary database file
   - Uses Python's `threading.local()` to ensure each process/thread has its own test state
   - Temporary database files are deleted after the test session ends

2. **Specialized Test Dataset**:
   - Test data is defined in `test_data.py`
   - Contains books and borrowing records that meet all R1-R7 test requirements
   - Database is reset to its initial test data state after each test

## Parallel Testing Support

The current implementation supports parallel testing on GitHub Actions or other CI platforms:

1. Each test process uses its own temporary database
2. Thread-local storage ensures different processes don't interfere with each other
3. Temporary files use unique names to avoid conflicts
4. Automatic cleanup ensures no temporary files remain after testing

## Test Dataset Design

The test dataset includes:

1. **Basic Books**:
   - Fully available books
   - Partially borrowed books
   - Fully borrowed books

2. **Sorting Tests**:
   - Books arranged in alphabetical order (A, M, Z)

3. **Borrowing and Returning Tests**:
   - Books available for borrowing
   - Books that are already borrowed
   - Books borrowed by different users

4. **Late Fee Tests**:
   - Overdue borrowing records

## Usage

No additional configuration is needed, just run the tests normally:

```bash
# Run all tests
pytest

# Run a specific test
pytest tests/R1_test.py

# Run tests in parallel
pytest -xvs -n auto  # requires pytest-xdist
```

## Implementation Details

- `database.py` uses `threading.local()` to store test state
- `test_data.py` defines the specialized test dataset
- `conftest.py` configures the test environment and data reset
- These features are automatically applied through pytest's fixture mechanism

## Advantages

- Tests don't pollute the main database
- Each test runs in a clean, consistent data environment
- Supports parallel test execution for faster testing
- No need for manual database cleanup
- Test data is specially designed to meet all test requirements
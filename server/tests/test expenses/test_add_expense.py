# test_add_expense.py


from requests import patch
from db import users_collection, expenses_collection, db
import pytest
import logicexpenses as le
from app import app
import logicconnection as lc
from datetime import timedelta
from unittest.mock import patch


# Clean the users collection before each test
@pytest.fixture(autouse=True)
def clean_collections():
    # Check if the database is FINBRAIN or FINBRAINTEST to make sure we are using the correct database for the test
    if db.name == 'FinBrainTest':
        users_collection.delete_many({})
        expenses_collection.delete_many({})


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def insert_test_user():
    """
    Insert a test user into the database
    """
    email = "user@login.com"
    # Insert a test user into the database
    users_collection.insert_one({
        "firstName": "User",
        "lastName": "Login",
        "email": email,
        "password": "Secret123",
    })

    # Create session ID and email and store it in Redis
    session_id = "s1"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)
    return session_id


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function adds an expense to the database
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense added'

    # Check if the expense was added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is not None
    assert expense['title'] == "Bought pizza"
    assert expense['date'] == "2025-01-01"
    assert expense['amount_usd'] == 100
    assert expense['amount_ils'] == 370
    assert expense['category'] == "Food & Drinks"
    assert expense['serial_number'] == 1


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_invalid_date(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the date is invalid
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "invalid-date",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid date format'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_invalid_currency(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the currency is invalid
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "invalid-currency",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid currency'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_invalid_amount(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the amount is invalid
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": "invalid-amount",
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Amount must be a number'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_invalid_title(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the title is invalid
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Invalid@Title#",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid title'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


def test_add_expense_without_session_id():
    """
    Test that the add_expense function returns an error if the session ID is not provided
    """
    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


def test_add_expense_with_invalid_session_id():
    """
    Test that the add_expense function returns an error if the session ID is invalid
    """
    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': 'invalid-session-id'}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 401
    assert response.json['message'] == 'Unauthorized'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_negative_amount(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the amount is negative
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": -100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Amount must be greater than 0'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_api_failure(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the API fails
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = None  
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 500
    assert response.json['message'] == 'Failed to get exchange rate'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_expense_serial_number_increment(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function increments the serial number correctly
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create 3 datas for the test
    for i in range(3):
        data = {
            "title": f"Bought pizza {i}",
            "date": "2025-01-01",
            "amount": 100,
            "currency": "USD",
        }

        # Send a POST request to the add_expense route and get the response
        response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

        # Check if the response is successful
        assert response.status_code == 200
        assert response.json['message'] == 'Expense added'

        # Check if the expense was added to the database
        expense = expenses_collection.find_one({"title": f"Bought pizza {i}"})
        assert expense is not None
        assert expense['title'] == f"Bought pizza {i}"
        assert expense['date'] == "2025-01-01"
        assert expense['amount_usd'] == 100
        assert expense['amount_ils'] == 370
        assert expense['category'] == "Food & Drinks"
        assert expense['serial_number'] == i + 1


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_title_too_long(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the title is too long
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test - title longer than 60 characters
    data = {
        "title": "This is a very long title that exceeds the maximum allowed length of sixty characters",
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Title must be less than 60 characters'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": data["title"]})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_amount_too_many_digits(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the amount has too many digits
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test - amount with more than 10 digits
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 12345678901,  
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Amount must be less than 10 digits'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_date_in_future(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the date is in the future
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test - future date
    data = {
        "title": "Bought pizza",
        "date": "2030-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Date cannot be in the future or before 2015'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_date_before_2015(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if the date is before 2015
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test - date before 2015
    data = {
        "title": "Bought pizza",
        "date": "2014-12-31", 
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Date cannot be in the future or before 2015'

    # Check if the expense was not added to the database
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is None


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_ils_currency(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function works correctly with ILS currency
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Create data for the test with ILS currency
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 370, 
        "currency": "ILS",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense added'

    # Check if the expense was added to the database with correct conversions
    expense = expenses_collection.find_one({"title": "Bought pizza"})
    assert expense is not None
    assert expense['title'] == "Bought pizza"
    assert expense['date'] == "2025-01-01"
    assert expense['amount_usd'] == 100  
    assert expense['amount_ils'] == 370  
    assert expense['category'] == "Food & Drinks"
    assert expense['serial_number'] == 1


@patch('logicexpenses.get_usd_to_ils_rate')
@patch('logicexpenses.classify_expense')
def test_add_expense_missing_required_fields(mock_classify_expense, mock_get_usd_to_ils_rate):
    """
    Test that the add_expense function returns an error if required fields are missing
    """
    # Mock the get_usd_to_ils_rate and classify_expense functions
    mock_get_usd_to_ils_rate.return_value = 3.7
    mock_classify_expense.return_value = "Food & Drinks"

    # Insert a test user
    session_id = insert_test_user()

    # Create client
    client = app.test_client()

    # Test missing title
    data = {
        "date": "2025-01-01",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'

    # Test missing date
    data = {
        "title": "Bought pizza",
        "amount": 100,
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'

    # Test missing amount
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "currency": "USD",
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'

    # Test missing currency
    data = {
        "title": "Bought pizza",
        "date": "2025-01-01",
        "amount": 100,
    }

    # Send a POST request to the add_expense route and get the response
    response = client.post('/add_expense', headers={'Session-ID': session_id}, json=data)

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True

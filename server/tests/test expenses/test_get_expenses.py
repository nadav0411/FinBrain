# FinBrain Project - test_get_expenses.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
from db import users_collection, expenses_collection, db
import pytest
from app import app
import logicconnection as lc
from datetime import timedelta
import time
from unittest.mock import patch
import cache
from password_hashing import hash_password


# Clean the users collection before each test
@pytest.fixture(autouse=True)
def clean_collections():
    """
    Clean the users and expenses collections before each test
    Ensures test isolation by using FinBrainTest database
    """
    # Check if the database is FINBRAIN or FINBRAINTEST to make sure we are using the correct database for the test
    if db.name == 'FinBrainTest':
        users_collection.delete_many({})
        expenses_collection.delete_many({})


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    """
    Clean Redis sessions before each test
    Ensures test isolation by removing any existing test sessions
    """
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)
    # Also clear any test cache keys to avoid cross-test contamination
    cache.clear_test_cache()


def insert_test_user():
    """
    Insert a test user into the database and create a valid session
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


def insert_demo_user_and_session():
    """
    Insert a demo user into the database and create a valid session
    """
    # Insert a demo user into the database
    email = "demo"
    users_collection.insert_one({
        "firstName": "Guest",
        "lastName": "Demo",
        "email": email,
        "password": hash_password("")
    })
    
    # Create session ID and email and store it in Redis
    session_id = "demo-session"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)
    return session_id


def get_user_id_from_email(email):
    """
    Get user ID from email address
    """
    user = users_collection.find_one({'email': email})
    return user['_id'] if user else None


def insert_test_expense(user_id, title, category="Food & Drinks", date="2025-01-01T00:00:00", amount_usd=100, amount_ils=370, serial_number=1):
    """
    Insert a test expense into the database
    """
    expenses_collection.insert_one({
        "user_id": user_id,
        "title": title,
        "date": date,
        "amount_usd": amount_usd,
        "amount_ils": amount_ils,
        "category": category,
        "serial_number": serial_number
    })


def test_get_expenses():
    """
    Test that the get_expenses function returns expenses for a user
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza")
    insert_test_expense(user_id, "Coffee")
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the get_expenses route with required parameters
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 2

    # Check if the expenses are in the database
    expenses = list(expenses_collection.find({}))
    assert len(expenses) == 2
    assert expenses[0]['title'] == "Pizza"
    assert expenses[1]['title'] == "Coffee"

    # Check if the expenses are in the response
    assert response.json['expenses'][0]['title'] == "Pizza"
    assert response.json['expenses'][1]['title'] == "Coffee"


def test_get_expenses_demo_user_basic():
    """
    Demo user can fetch expenses list successfully.
    """
    # Insert a demo user and create a valid session
    session_id = insert_demo_user_and_session()

    # Create client
    client = app.test_client()

    # Send a GET request to the get_expenses route with required parameters
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})

    # Check if the response is successful
    assert response.status_code == 200
    body = response.get_json()
    assert 'expenses' in body

    # Check if the expenses are in the response
    assert isinstance(body['expenses'], list)


def test_get_expenses_missing_month():
    """
    Test that the get_expenses function returns an error if month is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without month parameter
    response = client.get('/get_expenses?year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'


def test_get_expenses_missing_year():
    """
    Test that the get_expenses function returns an error if year is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without year parameter
    response = client.get('/get_expenses?month=1', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'


def test_get_expenses_invalid_month():
    """
    Test that the get_expenses function returns an error if month is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Test month too low
    response = client.get('/get_expenses?month=0&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'
    
    # Test month too high
    response = client.get('/get_expenses?month=13&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_invalid_year():
    """
    Test that the get_expenses function returns an error if year is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Test year too low
    response = client.get('/get_expenses?month=1&year=2014', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'
    
    # Test year too high
    response = client.get('/get_expenses?month=1&year=2035', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_without_session_id():
    """
    Test that the get_expenses function returns an error if session ID is not provided
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request without session ID
    response = client.get('/get_expenses?month=1&year=2025')
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_get_expenses_with_invalid_session_id():
    """
    Test that the get_expenses function returns an error if session ID is invalid
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid session ID
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': 'invalid-session-id'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_get_expenses_no_expenses():
    """
    Test that the get_expenses function returns empty list when user has no expenses
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the get_expenses route
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['expenses'] == []


def test_get_expenses_different_month():
    """
    Test that the get_expenses function returns only expenses for the specified month
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months
    insert_test_expense(user_id, "January Pizza")
    insert_test_expense(user_id, "February Coffee")
    
    # Update the February expense to have a different date
    expenses_collection.update_one(
        {"title": "February Coffee"},
        {"$set": {"date": "2025-02-01T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for January only
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "January Pizza"


def test_get_expenses_different_year():
    """
    Test that the get_expenses function returns only expenses for the specified year
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different years
    insert_test_expense(user_id, "2025 Pizza")
    insert_test_expense(user_id, "2024 Coffee")
    
    # Update the 2024 expense to have a different year
    expenses_collection.update_one(
        {"title": "2024 Coffee"},
        {"$set": {"date": "2024-01-01T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for 2025 only
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "2025 Pizza"


def test_get_expenses_multiple_expenses_same_month():
    """
    Test that the get_expenses function returns all expenses for the same month
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert multiple test expenses for the same month
    insert_test_expense(user_id, "Pizza")
    insert_test_expense(user_id, "Coffee")
    insert_test_expense(user_id, "Lunch")
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the get_expenses route
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 3
    
    # Check if all expenses are in the response
    expense_titles = [expense['title'] for expense in response.json['expenses']]
    assert "Pizza" in expense_titles
    assert "Coffee" in expense_titles
    assert "Lunch" in expense_titles


def test_get_expenses_edge_case_december():
    """
    Test that the get_expenses function works correctly for December (month 12)
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense for December
    insert_test_expense(user_id, "December Pizza")
    
    # Update the expense to have December date
    expenses_collection.update_one(
        {"title": "December Pizza"},
        {"$set": {"date": "2025-12-15T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for December
    response = client.get('/get_expenses?month=12&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "December Pizza"


def test_get_expenses_edge_case_january():
    """
    Test that the get_expenses function works correctly for January (month 1)
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense for January
    insert_test_expense(user_id, "January Coffee")
    
    # Update the expense to have January date
    expenses_collection.update_one(
        {"title": "January Coffee"},
        {"$set": {"date": "2025-01-15T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for January
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "January Coffee"


def test_get_expenses_non_numeric_parameters():
    """
    Test that the get_expenses function returns an error for non-numeric parameters
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with non-numeric month
    response = client.get('/get_expenses?month=abc&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'
    
    # Send a GET request with non-numeric year
    response = client.get('/get_expenses?month=1&year=abc', headers={'Session-ID': session_id})
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'


def test_get_expenses_session_id_null():
    """
    Test that the get_expenses function returns an error if session ID is null
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with null session ID
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': 'null'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_get_expenses_session_id_undefined():
    """
    Test that the get_expenses function returns an error if session ID is undefined
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with undefined session ID
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': 'undefined'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_get_expenses_session_id_empty():
    """
    Test that the get_expenses function returns an error if session ID is empty
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with empty session ID
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': ''})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_get_expenses_session_id_none():
    """
    Test that the get_expenses function returns an error if session ID is none
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with none session ID
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': 'none'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_get_expenses_boundary_year_2015():
    """
    Test that the get_expenses function works correctly for boundary year 2015
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense for 2015
    insert_test_expense(user_id, "2015 Pizza")
    
    # Update the expense to have 2015 date
    expenses_collection.update_one(
        {"title": "2015 Pizza"},
        {"$set": {"date": "2015-01-15T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for 2015
    response = client.get('/get_expenses?month=1&year=2015', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "2015 Pizza"


def test_get_expenses_boundary_year():
    """
    Test that the get_expenses function works correctly for boundary year 2027
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense for 2027
    insert_test_expense(user_id, "2027 Pizza")
    
    # Update the expense to have 2027 date
    expenses_collection.update_one(
        {"title": "2027 Pizza"},
        {"$set": {"date": "2027-12-15T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for 2027
    response = client.get('/get_expenses?month=12&year=2027', headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "2027 Pizza"


def test_get_expenses_year_before_2015():
    """
    Test that the get_expenses function returns an error for year before 2015
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for year before 2015
    response = client.get('/get_expenses?month=1&year=2014', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_year_after_2027():
    """
    Test that the get_expenses function returns an error for year after 2027
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request for year after 2027
    response = client.get('/get_expenses?month=1&year=2028', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_expired_session():
    """
    Test that the get_expenses function returns an error for expired session
    """
    # Insert a test user
    user = insert_test_user()
    
    # Create a session that will expire quickly
    email = "user@login.com"
    session_id = "expired-session"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", 1)  # Set TTL to 1 second
    
    # Wait for session to expire
    time.sleep(2)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with expired session
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_get_expenses_user_not_found():
    """
    Test that the get_expenses function returns an error when user is not found
    """
    # Create a session for a non-existent user
    email = "nonexistent@login.com"
    session_id = "invalid-user-session"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid user session
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_get_expenses_float_parameters():
    """
    Test that the get_expenses function handles float parameters correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with float month
    response = client.get('/get_expenses?month=1.5&year=2025', headers={'Session-ID': session_id})

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'
    
    # Send a GET request with float year
    response = client.get('/get_expenses?month=1&year=2025.5', headers={'Session-ID': session_id})

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Missing month or year'


def test_get_expenses_negative_parameters():
    """
    Test that the get_expenses function returns an error for negative parameters
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with negative month
    response = client.get('/get_expenses?month=-1&year=2025', headers={'Session-ID': session_id})

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'
    
    # Send a GET request with negative year
    response = client.get('/get_expenses?month=1&year=-2025', headers={'Session-ID': session_id})

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_zero_parameters():
    """
    Test that the get_expenses function returns an error for zero parameters
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with zero month
    response = client.get('/get_expenses?month=0&year=2025', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'
    
    # Send a GET request with zero year
    response = client.get('/get_expenses?month=1&year=0', headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month or year'


def test_get_expenses_multiple_months_years():
    """
    Test that the get_expenses function successfully returns expenses from multiple months and years
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months and years
    insert_test_expense(user_id, "January 2025 Pizza")
    insert_test_expense(user_id, "January 2025 Coffee")
    insert_test_expense(user_id, "February 2025 Lunch")
    insert_test_expense(user_id, "March 2025 Dinner")
    insert_test_expense(user_id, "December 2024 Holiday")
    insert_test_expense(user_id, "June 2025 Summer")
    
    # Update expenses to have different dates
    expenses_collection.update_one(
        {"title": "January 2025 Pizza"},
        {"$set": {"date": "2025-01-15T00:00:00"}}
    )
    expenses_collection.update_one(
        {"title": "January 2025 Coffee"},
        {"$set": {"date": "2025-01-20T00:00:00"}}
    )
    expenses_collection.update_one(
        {"title": "February 2025 Lunch"},
        {"$set": {"date": "2025-02-10T00:00:00"}}
    )
    expenses_collection.update_one(
        {"title": "March 2025 Dinner"},
        {"$set": {"date": "2025-03-05T00:00:00"}}
    )
    expenses_collection.update_one(
        {"title": "December 2024 Holiday"},
        {"$set": {"date": "2024-12-25T00:00:00"}}
    )
    expenses_collection.update_one(
        {"title": "June 2025 Summer"},
        {"$set": {"date": "2025-06-15T00:00:00"}}
    )
    
    # Create client
    client = app.test_client()
    
    # Test January 2025 - should return 2 expenses
    response = client.get('/get_expenses?month=1&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert len(response.json['expenses']) == 2
    january_titles = [expense['title'] for expense in response.json['expenses']]
    assert "January 2025 Pizza" in january_titles
    assert "January 2025 Coffee" in january_titles
    
    # Test February 2025 - should return 1 expense
    response = client.get('/get_expenses?month=2&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "February 2025 Lunch"
    
    # Test March 2025 - should return 1 expense
    response = client.get('/get_expenses?month=3&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "March 2025 Dinner"
    
    # Test June 2025 - should return 1 expense
    response = client.get('/get_expenses?month=6&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "June 2025 Summer"
    
    # Test December 2024 - should return 1 expense
    response = client.get('/get_expenses?month=12&year=2024', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert len(response.json['expenses']) == 1
    assert response.json['expenses'][0]['title'] == "December 2024 Holiday"
    
    # Test a month with no expenses - should return empty list
    response = client.get('/get_expenses?month=4&year=2025', headers={'Session-ID': session_id})
    assert response.status_code == 200
    assert response.json['expenses'] == []
    
    # Verify all expenses are in the database
    all_expenses = list(expenses_collection.find({"user_id": user_id}))
    assert len(all_expenses) == 6
    
    # Check that expenses are properly filtered by month/year
    january_expenses = list(expenses_collection.find({
        "user_id": user_id,
        "date": {
            "$gte": "2025-01-01T00:00:00",
            "$lt": "2025-02-01T00:00:00"
        }
    }))
    assert len(january_expenses) == 2


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
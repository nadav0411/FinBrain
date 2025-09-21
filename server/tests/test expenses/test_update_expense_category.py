# test_update_expense_category.py


# type: ignore
from db import users_collection, expenses_collection, db
import pytest
from app import app
import logicconnection as lc
from datetime import timedelta
import time
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


def get_user_id_from_email(email):
    """
    Get user ID from email
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


def test_update_expense_category_success():
    """
    Test that the update_expense_category function successfully updates an expense category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to update the expense category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Category updated'
    assert response.json['new_category'] == 'Housing & Bills'
    
    # Check if the expense was updated in the database
    updated_expense = expenses_collection.find_one({
        'user_id': user_id,
        'serial_number': 1
    })
    assert updated_expense is not None
    assert updated_expense['category'] == 'Housing & Bills'


def test_update_expense_category_missing_session_id():
    """
    Test that the update_expense_category function returns an error if session ID is not provided
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request without session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          })
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_update_expense_category_invalid_session_id():
    """
    Test that the update_expense_category function returns an error if session ID is invalid
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with invalid session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': 'invalid-session-id'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_update_expense_category_missing_serial_number():
    """
    Test that the update_expense_category function returns an error if serial number is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without serial number
    response = client.post('/update_expense_category', 
                          json={
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_update_expense_category_missing_current_category():
    """
    Test that the update_expense_category function returns an error if current category is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without current category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Current category is required'


def test_update_expense_category_missing_new_category():
    """
    Test that the update_expense_category function returns an error if new category is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'New category is required'


def test_update_expense_category_expense_not_found():
    """
    Test that the update_expense_category function returns an error if expense is not found
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request for non-existent expense
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 999,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_invalid_new_category():
    """
    Test that the update_expense_category function returns an error if new category is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with invalid new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Invalid Category'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid category'


def test_update_expense_category_category_already_updated():
    """
    Test that the update_expense_category function returns an error if category is already updated
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with wrong current category (simulating already updated)
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Housing & Bills', 
                              'new_category': 'Transportation'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Category is already updated'


def test_update_expense_category_same_category():
    """
    Test that the update_expense_category function returns an error if new category is same as current
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with same category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Food & Drinks' 
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid category'


def test_update_expense_category_session_id_null():
    """
    Test that the update_expense_category function returns an error if session ID is null
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with null session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': 'null'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_update_expense_category_session_id_undefined():
    """
    Test that the update_expense_category function returns an error if session ID is undefined
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with undefined session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': 'undefined'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_update_expense_category_session_id_empty():
    """
    Test that the update_expense_category function returns an error if session ID is empty
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with empty session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': ''})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_update_expense_category_session_id_none():
    """
    Test that the update_expense_category function returns an error if session ID is none
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with none session ID
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': 'none'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_update_expense_category_expired_session():
    """
    Test that the update_expense_category function returns an error for expired session
    """
    # Insert a test user
    user = insert_test_user()
    
    # Create a session that will expire quickly
    email = "user@login.com"
    session_id = "expired-session"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", 1)
    
    # Wait for session to expire
    time.sleep(2)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with expired session
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_update_expense_category_user_not_found():
    """
    Test that the update_expense_category function returns an error when user is not found
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
    
    # Send a POST request with invalid user session
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_update_expense_category_all_valid_categories():
    """
    Test that the update_expense_category function works with all valid categories
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # List of all valid categories
    valid_categories = [
        'Food & Drinks',
        'Housing & Bills',
        'Transportation',
        'Education & Personal Growth',
        'Health & Essentials',
        'Leisure & Gifts',
        'Other'
    ]
    
    # Test updating from Food & Drinks to each valid category
    for i, new_category in enumerate(valid_categories[1:], 1): 
        # Insert test expense
        insert_test_expense(user_id, f"Test Expense {i}", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, i)
        
        # Create client
        client = app.test_client()
        
        # Send a POST request to update the expense category
        response = client.post('/update_expense_category', 
                              json={
                                  'serial_number': i,
                                  'current_category': 'Food & Drinks',
                                  'new_category': new_category
                              },
                              headers={'Session-ID': session_id})
        
        # Check if the response is successful
        assert response.status_code == 200
        assert response.json['message'] == 'Category updated'
        assert response.json['new_category'] == new_category
        
        # Check if the expense was updated in the database
        updated_expense = expenses_collection.find_one({
            'user_id': user_id,
            'serial_number': i
        })
        assert updated_expense is not None
        assert updated_expense['category'] == new_category


def test_update_expense_category_non_numeric_serial_number():
    """
    Test that the update_expense_category function handles non-numeric serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with non-numeric serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 'abc',
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_negative_serial_number():
    """
    Test that the update_expense_category function handles negative serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with negative serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': -1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_zero_serial_number():
    """
    Test that the update_expense_category function handles zero serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with zero serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 0,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_large_serial_number():
    """
    Test that the update_expense_category function handles very large serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with very large serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 999999999,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_float_serial_number():
    """
    Test that the update_expense_category function handles float serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with float serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1.5,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_update_expense_category_empty_string_serial_number():
    """
    Test that the update_expense_category function handles empty string serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with empty string serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': '',
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_update_expense_category_none_serial_number():
    """
    Test that the update_expense_category function handles None serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with None serial number
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': None,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_update_expense_category_empty_string_current_category():
    """
    Test that the update_expense_category function handles empty string current category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with empty string current category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': '',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Current category is required'


def test_update_expense_category_none_current_category():
    """
    Test that the update_expense_category function handles None current category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with None current category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': None,
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Current category is required'


def test_update_expense_category_empty_string_new_category():
    """
    Test that the update_expense_category function handles empty string new category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with empty string new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': ''
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'New category is required'


def test_update_expense_category_none_new_category():
    """
    Test that the update_expense_category function handles None new category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with None new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': None
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'New category is required'


def test_update_expense_category_multiple_expenses_same_user():
    """
    Test that the update_expense_category function works correctly with multiple expenses for the same user
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert multiple test expenses
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740, 2)
    insert_test_expense(user_id, "Gas", "Transportation", "2025-01-03T00:00:00", 50, 185, 3)
    
    # Create client
    client = app.test_client()
    
    # Update first expense
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Leisure & Gifts'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Category updated'
    assert response.json['new_category'] == 'Leisure & Gifts'
    
    # Update second expense
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 2,
                              'current_category': 'Housing & Bills',
                              'new_category': 'Health & Essentials'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Category updated'
    assert response.json['new_category'] == 'Health & Essentials'
    
    # Update third expense
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 3,
                              'current_category': 'Transportation',
                              'new_category': 'Education & Personal Growth'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Category updated'
    assert response.json['new_category'] == 'Education & Personal Growth'
    
    # Verify all expenses were updated in the database
    expenses = list(expenses_collection.find({'user_id': user_id}))
    assert len(expenses) == 3
    
    # Check specific categories
    expense_1 = next((exp for exp in expenses if exp['serial_number'] == 1), None)
    expense_2 = next((exp for exp in expenses if exp['serial_number'] == 2), None)
    expense_3 = next((exp for exp in expenses if exp['serial_number'] == 3), None)
    
    assert expense_1 is not None
    assert expense_1['category'] == 'Leisure & Gifts'
    assert expense_2 is not None
    assert expense_2['category'] == 'Health & Essentials'
    assert expense_3 is not None
    assert expense_3['category'] == 'Education & Personal Growth'


def test_update_expense_category_case_sensitivity():
    """
    Test that the update_expense_category function handles case sensitivity correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with different case for current category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'food & drinks',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful (case sensitive)
    assert response.status_code == 400
    assert response.json['message'] == 'Category is already updated'


def test_update_expense_category_whitespace_handling():
    """
    Test that the update_expense_category function handles whitespace correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with extra whitespace
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': '  Food & Drinks  ',
                              'new_category': 'Housing & Bills'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful (whitespace sensitive)
    assert response.status_code == 400
    assert response.json['message'] == 'Category is already updated'


def test_update_expense_category_special_characters_in_category():
    """
    Test that the update_expense_category function handles special characters in category names
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with special characters in new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Food & Drinks@#$%'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid category'


def test_update_expense_category_unicode_characters():
    """
    Test that the update_expense_category function handles unicode characters
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370, 1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with unicode characters in new category
    response = client.post('/update_expense_category', 
                          json={
                              'serial_number': 1,
                              'current_category': 'Food & Drinks',
                              'new_category': 'Food & Drinks™©®'
                          },
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid category'


def test_update_expense_category_missing_json():
    """
    Test that the update_expense_category function handles missing JSON body
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without JSON body
    response = client.post('/update_expense_category', 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid JSON format'


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True

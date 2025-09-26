# FinBrain Project - test_delete_expense.py - MIT License (c) 2025 Nadav Eshed


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


def test_delete_expense_success():
    """
    Test that the delete_expense function successfully deletes an expense
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=2)
    
    # Verify expenses exist before deletion
    expenses_before = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_before) == 2
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete the first expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense deleted'
    assert response.json['serial_number'] == 1
    
    # Verify the expense was deleted from the database
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 1
    assert expenses_after[0]['title'] == "Coffee"


def test_delete_expense_missing_session_id():
    """
    Test that the delete_expense function returns an error if session ID is not provided
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request without session ID
    response = client.post('/delete_expense', json={'serial_number': 1})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_delete_expense_invalid_session_id():
    """
    Test that the delete_expense function returns an error if session ID is invalid
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with invalid session ID
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': 'invalid-session-id'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_delete_expense_missing_serial_number():
    """
    Test that the delete_expense function returns an error if serial number is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without serial number
    response = client.post('/delete_expense', 
                          json={}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_delete_expense_nonexistent_expense():
    """
    Test that the delete_expense function returns an error if expense does not exist
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", serial_number=1)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete non-existent expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 999}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'
    
    # Verify the original expense still exists
    expenses = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses) == 1
    assert expenses[0]['title'] == "Pizza"


def test_delete_expense_user_not_found():
    """
    Test that the delete_expense function returns an error when user is not found
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
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_delete_expense_expired_session():
    """
    Test that the delete_expense function returns an error for expired session
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
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_delete_expense_invalid_serial_number_format():
    """
    Test that the delete_expense function handles invalid serial number formats
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with string serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': 'abc'}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful 
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'
    
    # Send a POST request with float serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': 1.5}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_different_user():
    """
    Test that the delete_expense function cannot delete expenses from different users
    """
    # Insert two test users
    session_id1 = insert_test_user()
    
    # Create second user
    email2 = "user2@login.com"
    users_collection.insert_one({
        "firstName": "User2",
        "lastName": "Login2",
        "email": email2,
        "password": "Secret123",
    })
    
    # Create session for second user
    session_id2 = "s2"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id2}", "email", email2)
    lc.r.hset(f"session:{session_id2}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id2}", lc.SESSION_TTL_SECONDS)
    
    # Get user IDs
    user_id1 = get_user_id_from_email("user@login.com")
    user_id2 = get_user_id_from_email("user2@login.com")
    
    # Insert expenses for both users
    insert_test_expense(user_id1, "User1 Pizza", serial_number=1)
    insert_test_expense(user_id2, "User2 Coffee", serial_number=2)
    
    # Create client
    client = app.test_client()
    
    # Try to delete user2's expense using user1's session
    response = client.post('/delete_expense', 
                          json={'serial_number': 2}, 
                          headers={'Session-ID': session_id1})
    
    # Check if the response is unsuccessful (expense not found for user1)
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'
    
    # Verify both expenses still exist
    user1_expenses = list(expenses_collection.find({"user_id": user_id1}))
    user2_expenses = list(expenses_collection.find({"user_id": user_id2}))
    assert len(user1_expenses) == 1
    assert len(user2_expenses) == 1
    assert user1_expenses[0]['title'] == "User1 Pizza"
    assert user2_expenses[0]['title'] == "User2 Coffee"


def test_delete_expense_database_error():
    """
    Test that the delete_expense function handles database errors
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", serial_number=1)
    
    # Create client
    client = app.test_client()
    
    # Mock the database to raise an exception
    with patch('db.expenses_collection.delete_one') as mock_delete:
        mock_delete.side_effect = Exception("Database connection error")
        
        # Send a POST request to delete expense
        response = client.post('/delete_expense', 
                              json={'serial_number': 1}, 
                              headers={'Session-ID': session_id})
        
        # Check if the response is unsuccessful
        assert response.status_code == 500
        assert response.json['message'] == 'Failed to delete expense'


def test_delete_expense_session_id_null():
    """
    Test that the delete_expense function returns an error if session ID is null
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with null session ID
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': 'null'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_delete_expense_session_id_undefined():
    """
    Test that the delete_expense function returns an error if session ID is undefined
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with undefined session ID
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': 'undefined'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_delete_expense_session_id_empty():
    """
    Test that the delete_expense function returns an error if session ID is empty
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with empty session ID
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': ''})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_delete_expense_session_id_none():
    """
    Test that the delete_expense function returns an error if session ID is none
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with none session ID
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': 'none'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_delete_expense_negative_serial_number():
    """
    Test that the delete_expense function handles negative serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with negative serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': -1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful (expense not found)
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_zero_serial_number():
    """
    Test that the delete_expense function handles zero serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with zero serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': 0}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful (expense not found)
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_large_serial_number():
    """
    Test that the delete_expense function handles very large serial numbers
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with very large serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': 999999999}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful (expense not found)
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_missing_json_data():
    """
    Test that the delete_expense function handles missing JSON data
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request without JSON data
    response = client.post('/delete_expense', 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid JSON format'


def test_delete_expense_invalid_json_format():
    """
    Test that the delete_expense function handles invalid JSON format
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with invalid JSON
    response = client.post('/delete_expense', 
                          data='invalid json', 
                          headers={'Session-ID': session_id, 'Content-Type': 'application/json'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid JSON format'


def test_delete_expense_multiple_expenses_same_serial():
    """
    Test that the delete_expense function handles multiple expenses with same serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert multiple expenses with same serial number
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=1) 
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete expense with serial number 1
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense deleted'
    assert response.json['serial_number'] == 1
    
    # Verify only one expense was deleted
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 1


def test_delete_expense_last_expense():
    """
    Test that the delete_expense function successfully deletes the last expense
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=2)
    insert_test_expense(user_id, "Lunch", serial_number=3)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete the last expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 3}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense deleted'
    assert response.json['serial_number'] == 3
    
    # Verify the last expense was deleted
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 2
    expense_titles = [expense['title'] for expense in expenses_after]
    assert "Pizza" in expense_titles
    assert "Coffee" in expense_titles
    assert "Lunch" not in expense_titles


def test_delete_expense_first_expense():
    """
    Test that the delete_expense function successfully deletes the first expense
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=2)
    insert_test_expense(user_id, "Lunch", serial_number=3)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete the first expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense deleted'
    assert response.json['serial_number'] == 1
    
    # Verify the first expense was deleted
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 2
    expense_titles = [expense['title'] for expense in expenses_after]
    assert "Pizza" not in expense_titles
    assert "Coffee" in expense_titles
    assert "Lunch" in expense_titles


def test_delete_expense_middle_expense():
    """
    Test that the delete_expense function successfully deletes a middle expense
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=2)
    insert_test_expense(user_id, "Lunch", serial_number=3)
    insert_test_expense(user_id, "Dinner", serial_number=4)
    
    # Create client
    client = app.test_client()
    
    # Send a POST request to delete the middle expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 2}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['message'] == 'Expense deleted'
    assert response.json['serial_number'] == 2
    
    # Verify the middle expense was deleted
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 3
    expense_titles = [expense['title'] for expense in expenses_after]
    assert "Pizza" in expense_titles
    assert "Coffee" not in expense_titles
    assert "Lunch" in expense_titles
    assert "Dinner" in expense_titles


def test_delete_expense_session_id_special_characters():
    """
    Test that the delete_expense function handles session ID with special characters
    """
    # Create client
    client = app.test_client()
    
    # Send a POST request with session ID containing special characters
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': 'session@#$%^&*()'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_delete_expense_serial_number_whitespace():
    """
    Test that the delete_expense function handles serial number with whitespace
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with serial number containing whitespace
    response = client.post('/delete_expense', 
                          json={'serial_number': ' 1 '}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_serial_number_boolean():
    """
    Test that the delete_expense function handles boolean serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with boolean serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': True}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_serial_number_array():
    """
    Test that the delete_expense function handles array serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with array serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': [1, 2, 3]}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_serial_number_null():
    """
    Test that the delete_expense function handles null serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with null serial number
    response = client.post('/delete_expense', 
                          json={'serial_number': None}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_delete_expense_serial_number_undefined():
    """
    Test that the delete_expense function handles undefined serial number
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a POST request with undefined serial number (missing key)
    response = client.post('/delete_expense', 
                          json={'other_field': 'value'}, 
                          headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Serial number is required'


def test_delete_expense_multiple_deletions():
    """
    Test that the delete_expense function can handle multiple deletions
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", serial_number=1)
    insert_test_expense(user_id, "Coffee", serial_number=2)
    insert_test_expense(user_id, "Lunch", serial_number=3)
    
    # Create client
    client = app.test_client()
    
    # Delete first expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 200
    
    # Delete second expense
    response = client.post('/delete_expense', 
                          json={'serial_number': 2}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 200
    
    # Verify only one expense remains
    expenses_after = list(expenses_collection.find({"user_id": user_id}))
    assert len(expenses_after) == 1
    assert expenses_after[0]['title'] == "Lunch"


def test_delete_expense_duplicate_deletion():
    """
    Test that the delete_expense function handles duplicate deletion attempts
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expense
    insert_test_expense(user_id, "Pizza", serial_number=1)
    
    # Create client
    client = app.test_client()
    
    # Delete expense first time
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 200
    
    # Try to delete same expense again
    response = client.post('/delete_expense', 
                          json={'serial_number': 1}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_delete_expense_serial_number_edge_values():
    """
    Test that the delete_expense function handles edge case serial number values
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Test with very small positive number
    response = client.post('/delete_expense', 
                          json={'serial_number': 0.1}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'
    
    # Test with very large number
    response = client.post('/delete_expense', 
                          json={'serial_number': 1e10}, 
                          headers={'Session-ID': session_id})
    assert response.status_code == 404
    assert response.json['message'] == 'Expense not found'


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
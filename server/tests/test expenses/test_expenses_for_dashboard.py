# test_expenses_for_dashboard.py


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


def insert_test_expense(user_id, title, category="Food & Drinks", date="2025-01-01T00:00:00", amount_usd=100, amount_ils=370):
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
        "serial_number": 1
    })


def test_expenses_for_dashboard_category_breakdown():
    """
    Test that the expenses_for_dashboard function returns category breakdown data correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with different categories
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    insert_test_expense(user_id, "Gas", "Transportation", "2025-01-03T00:00:00", 50, 185)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'category_breakdown'
    assert response.json['currency'] == 'USD'
    assert response.json['months'] == ['2025-01']
    
    # Check if the data contains the expected categories
    data = response.json['data']
    assert len(data) == 7  # All 7 categories should be present
    
    # Find specific categories in the data
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    housing_data = next((item for item in data if item['category'] == 'Housing & Bills'), None)
    transport_data = next((item for item in data if item['category'] == 'Transportation'), None)
    
    assert food_data is not None
    assert food_data['amount'] == 100.0
    assert housing_data is not None
    assert housing_data['amount'] == 200.0
    assert transport_data is not None
    assert transport_data['amount'] == 50.0


def test_expenses_for_dashboard_monthly_comparison():
    """
    Test that the expenses_for_dashboard function returns monthly comparison data correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months
    insert_test_expense(user_id, "January Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "February Pizza", "Food & Drinks", "2025-02-01T00:00:00", 150, 555)
    insert_test_expense(user_id, "March Pizza", "Food & Drinks", "2025-03-01T00:00:00", 200, 740)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&months=2025-02&months=2025-03&categories=Food%20%26%20Drinks', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'monthly_comparison'
    assert response.json['currency'] == 'USD'
    assert len(response.json['months']) == 3
    
    # Check if the data contains the expected months
    data = response.json['data']
    assert len(data) == 3
    
    # Find specific months in the data
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)
    feb_data = next((item for item in data if item['month'] == '2025-02'), None)
    mar_data = next((item for item in data if item['month'] == '2025-03'), None)
    
    assert jan_data is not None
    assert jan_data['amount'] == 100.0
    assert feb_data is not None
    assert feb_data['amount'] == 150.0
    assert mar_data is not None
    assert mar_data['amount'] == 200.0


def test_expenses_for_dashboard_missing_chart():
    """
    Test that the expenses_for_dashboard function returns an error if chart is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without chart parameter
    response = client.get('/expenses_for_dashboard?currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid chart'


def test_expenses_for_dashboard_missing_currency():
    """
    Test that the expenses_for_dashboard function returns an error if currency is missing
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without currency parameter
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid currency'


def test_expenses_for_dashboard_missing_months():
    """
    Test that the expenses_for_dashboard function handles missing months gracefully
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without months parameter
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful with empty data
    assert response.status_code == 200
    assert response.json['chart'] == 'category_breakdown'
    assert response.json['currency'] == 'USD'
    assert response.json['months'] == []
    
    # Check if all categories have zero amounts
    data = response.json['data']
    for item in data:
        assert item['amount'] == 0.0
        assert item['percentage'] == 0.0


def test_expenses_for_dashboard_missing_categories():
    """
    Test that the expenses_for_dashboard function handles missing categories gracefully
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request without categories parameter
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful with empty data
    assert response.status_code == 200
    assert response.json['chart'] == 'category_breakdown'
    assert response.json['currency'] == 'USD'
    assert response.json['months'] == ['2025-01']
    
    # Check if all categories have zero amounts
    data = response.json['data']
    for item in data:
        assert item['amount'] == 0.0
        assert item['percentage'] == 0.0


def test_expenses_for_dashboard_invalid_chart():
    """
    Test that the expenses_for_dashboard function returns an error if chart is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid chart
    response = client.get('/expenses_for_dashboard?chart=invalid_chart&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid chart'


def test_expenses_for_dashboard_invalid_currency():
    """
    Test that the expenses_for_dashboard function returns an error if currency is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid currency
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=EUR&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid currency'


def test_expenses_for_dashboard_invalid_month_format():
    """
    Test that the expenses_for_dashboard function returns an error if month format is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid month format
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-1&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid month'


def test_expenses_for_dashboard_too_many_months():
    """
    Test that the expenses_for_dashboard function returns an error if too many months are selected
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with too many months (more than 12)
    months = "&months=".join([f"2025-{i:02d}" for i in range(1, 14)]) 
    response = client.get(f'/expenses_for_dashboard?chart=category_breakdown&currency=USD&months={months}&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Too many months selected. Maximum is 12.'


def test_expenses_for_dashboard_invalid_category():
    """
    Test that the expenses_for_dashboard function returns an error if category is invalid
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid category
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=InvalidCategory', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid category'


def test_expenses_for_dashboard_without_session_id():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is not provided
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request without session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All')
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_expenses_for_dashboard_with_invalid_session_id():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is invalid
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with invalid session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': 'invalid-session-id'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_expenses_for_dashboard_no_expenses():
    """
    Test that the expenses_for_dashboard function returns empty data when user has no expenses
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'category_breakdown'
    assert response.json['currency'] == 'USD'
    
    # Check if all categories have zero amounts
    data = response.json['data']
    for item in data:
        assert item['amount'] == 0.0
        assert item['percentage'] == 0.0


def test_expenses_for_dashboard_ils_currency():
    """
    Test that the expenses_for_dashboard function works correctly with ILS currency
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with ILS currency
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=ILS&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['currency'] == 'ILS'
    
    # Check if the amounts are in ILS
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    housing_data = next((item for item in data if item['category'] == 'Housing & Bills'), None)
    
    assert food_data is not None
    assert food_data['amount'] == 370.0
    assert housing_data is not None
    assert housing_data['amount'] == 740.0


def test_expenses_for_dashboard_multiple_months():
    """
    Test that the expenses_for_dashboard function works correctly with multiple months
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months
    insert_test_expense(user_id, "January Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "February Pizza", "Food & Drinks", "2025-02-01T00:00:00", 150, 555)
    insert_test_expense(user_id, "March Pizza", "Food & Drinks", "2025-03-01T00:00:00", 200, 740)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with multiple months
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&months=2025-02&months=2025-03&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['months']) == 3
    
    # Check if the total amount includes all months
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    assert food_data is not None
    assert food_data['amount'] == 450.0 


def test_expenses_for_dashboard_multiple_categories():
    """
    Test that the expenses_for_dashboard function works correctly with multiple categories
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with different categories
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    insert_test_expense(user_id, "Gas", "Transportation", "2025-01-03T00:00:00", 50, 185)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with multiple categories
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&categories=Food%20%26%20Drinks&categories=Housing%20%26%20Bills&categories=Transportation', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'monthly_comparison'
    
    # Check if the data contains the expected month
    data = response.json['data']
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)
    assert jan_data is not None
    assert jan_data['amount'] == 350.0


def test_expenses_for_dashboard_all_category():
    """
    Test that the expenses_for_dashboard function works correctly with 'All' category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with different categories
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    insert_test_expense(user_id, "Gas", "Transportation", "2025-01-03T00:00:00", 50, 185)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with 'All' category
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'monthly_comparison'
    
    # Check if the data contains the expected month
    data = response.json['data']
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)
    assert jan_data is not None
    assert jan_data['amount'] == 350.0 


def test_expenses_for_dashboard_percentage_calculation():
    """
    Test that the expenses_for_dashboard function calculates percentages correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with known amounts for percentage calculation
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    insert_test_expense(user_id, "Gas", "Transportation", "2025-01-03T00:00:00", 100, 370)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the percentages are calculated correctly
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    housing_data = next((item for item in data if item['category'] == 'Housing & Bills'), None)
    transport_data = next((item for item in data if item['category'] == 'Transportation'), None)
    
    assert food_data is not None
    assert food_data['amount'] == 100.0
    assert food_data['percentage'] == 25.0  
    
    assert housing_data is not None
    assert housing_data['amount'] == 200.0
    assert housing_data['percentage'] == 50.0  
    
    assert transport_data is not None
    assert transport_data['amount'] == 100.0
    assert transport_data['percentage'] == 25.0


def test_expenses_for_dashboard_monthly_comparison_percentage():
    """
    Test that the expenses_for_dashboard function calculates monthly comparison percentages correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months with known amounts
    insert_test_expense(user_id, "January Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "February Pizza", "Food & Drinks", "2025-02-01T00:00:00", 200, 740)
    insert_test_expense(user_id, "March Pizza", "Food & Drinks", "2025-03-01T00:00:00", 300, 1110)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&months=2025-02&months=2025-03&categories=Food%20%26%20Drinks', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the percentages are calculated correctly (based on max amount)
    data = response.json['data']
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)
    feb_data = next((item for item in data if item['month'] == '2025-02'), None)
    mar_data = next((item for item in data if item['month'] == '2025-03'), None)
    
    assert jan_data is not None
    assert jan_data['amount'] == 100.0
    assert jan_data['percentage'] == 33.33  
    
    assert feb_data is not None
    assert feb_data['amount'] == 200.0
    assert feb_data['percentage'] == 66.67  
    
    assert mar_data is not None
    assert mar_data['amount'] == 300.0
    assert mar_data['percentage'] == 100.0  


def test_expenses_for_dashboard_session_id_null():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is null
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with null session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': 'null'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_expenses_for_dashboard_session_id_undefined():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is undefined
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with undefined session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': 'undefined'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_expenses_for_dashboard_session_id_empty():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is empty
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with empty session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': ''})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_expenses_for_dashboard_session_id_none():
    """
    Test that the expenses_for_dashboard function returns an error if session ID is none
    """
    # Create client
    client = app.test_client()
    
    # Send a GET request with none session ID
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': 'none'})
    
    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert response.json['message'] == 'Session ID is required'


def test_expenses_for_dashboard_expired_session():
    """
    Test that the expenses_for_dashboard function returns an error for expired session
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
    
    # Send a GET request with expired session
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_expenses_for_dashboard_user_not_found():
    """
    Test that the expenses_for_dashboard function returns an error when user is not found
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
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is unsuccessful
    assert response.status_code == 404
    assert response.json['message'] == 'User not found'


def test_expenses_for_dashboard_edge_case_12_months():
    """
    Test that the expenses_for_dashboard function works correctly with exactly 12 months
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for each month
    for month in range(1, 13):
        insert_test_expense(user_id, f"Month {month} Pizza", "Food & Drinks", f"2025-{month:02d}-01T00:00:00", 100, 370)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with exactly 12 months
    months = "&months=".join([f"2025-{i:02d}" for i in range(1, 13)])
    response = client.get(f'/expenses_for_dashboard?chart=category_breakdown&currency=USD&months={months}&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert len(response.json['months']) == 12
    
    # Check if the total amount includes all months
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    assert food_data is not None
    assert food_data['amount'] == 1200.0 


def test_expenses_for_dashboard_edge_case_single_category():
    """
    Test that the expenses_for_dashboard function works correctly with a single category
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with only one category
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "Coffee", "Food & Drinks", "2025-01-02T00:00:00", 50, 185)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request with single category
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&categories=Food%20%26%20Drinks', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'monthly_comparison'
    
    # Check if the data contains the expected month
    data = response.json['data']
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)
    assert jan_data is not None
    assert jan_data['amount'] == 150.0  # 100 + 50


def test_expenses_for_dashboard_edge_case_zero_amounts():
    """
    Test that the expenses_for_dashboard function handles zero amounts correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with zero amounts
    insert_test_expense(user_id, "Free Pizza", "Food & Drinks", "2025-01-01T00:00:00", 0, 0)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if all categories have zero amounts
    data = response.json['data']
    for item in data:
        assert item['amount'] == 0.0
        assert item['percentage'] == 0.0


def test_expenses_for_dashboard_edge_case_rounding():
    """
    Test that the expenses_for_dashboard function rounds amounts and percentages correctly
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses with amounts that will result in rounding
    insert_test_expense(user_id, "Pizza", "Food & Drinks", "2025-01-01T00:00:00", 33.333, 123.456)
    insert_test_expense(user_id, "Rent", "Housing & Bills", "2025-01-02T00:00:00", 66.666, 246.789)
    
    # Create client
    client = app.test_client()
    
    # Send a GET request to the expenses_for_dashboard route
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the amounts are rounded to 2 decimal places
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    housing_data = next((item for item in data if item['category'] == 'Housing & Bills'), None)
    
    assert food_data is not None
    assert food_data['amount'] == 33.33  
    assert housing_data is not None
    assert housing_data['amount'] == 66.67  


def test_expenses_for_dashboard_comprehensive_multiple_months_categories():
    """
    Test that the expenses_for_dashboard function works correctly with multiple months and categories
    """
    # Insert a test user
    session_id = insert_test_user()
    
    # Get user ID for creating expenses
    user_id = get_user_id_from_email("user@login.com")
    
    # Insert test expenses for different months and categories
    insert_test_expense(user_id, "January Pizza", "Food & Drinks", "2025-01-01T00:00:00", 100, 370)
    insert_test_expense(user_id, "January Rent", "Housing & Bills", "2025-01-02T00:00:00", 200, 740)
    insert_test_expense(user_id, "February Pizza", "Food & Drinks", "2025-02-01T00:00:00", 150, 555)
    insert_test_expense(user_id, "February Gas", "Transportation", "2025-02-02T00:00:00", 50, 185)
    insert_test_expense(user_id, "March Rent", "Housing & Bills", "2025-03-01T00:00:00", 250, 925)
    insert_test_expense(user_id, "March Gas", "Transportation", "2025-03-02T00:00:00", 75, 277.5)
    
    # Create client
    client = app.test_client()
    
    # Test category breakdown with multiple months
    response = client.get('/expenses_for_dashboard?chart=category_breakdown&currency=USD&months=2025-01&months=2025-02&months=2025-03&categories=All', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'category_breakdown'
    assert len(response.json['months']) == 3
    
    # Check if the data contains the expected categories with correct totals
    data = response.json['data']
    food_data = next((item for item in data if item['category'] == 'Food & Drinks'), None)
    housing_data = next((item for item in data if item['category'] == 'Housing & Bills'), None)
    transport_data = next((item for item in data if item['category'] == 'Transportation'), None)
    
    assert food_data is not None
    assert food_data['amount'] == 250.0 
    assert housing_data is not None
    assert housing_data['amount'] == 450.0 
    assert transport_data is not None
    assert transport_data['amount'] == 125.0 
    
    # Test monthly comparison with specific categories
    response = client.get('/expenses_for_dashboard?chart=monthly_comparison&currency=USD&months=2025-01&months=2025-02&months=2025-03&categories=Food%20%26%20Drinks&categories=Transportation', 
                         headers={'Session-ID': session_id})
    
    # Check if the response is successful
    assert response.status_code == 200
    assert response.json['chart'] == 'monthly_comparison'
    
    # Check if the data contains the expected months with correct amounts   
    data = response.json['data']
    jan_data = next((item for item in data if item['month'] == '2025-01'), None)                                                                            
    feb_data = next((item for item in data if item['month'] == '2025-02'), None)                                                                            
    mar_data = next((item for item in data if item['month'] == '2025-03'), None)                                                                            

    assert jan_data is not None
    assert jan_data['amount'] == 100.0  
    assert feb_data is not None
    assert feb_data['amount'] == 200.0                                                                       
    assert mar_data is not None
    assert mar_data['amount'] == 75.0  
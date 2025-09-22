# test_login.py


# type: ignore
from app import app
from db import users_collection, db
import pytest
from password_hashing import hash_password


# Clean the users collection before each test
@pytest.fixture(autouse=True)
def clean_users_collection():
    # Check if the database is FINBRAIN or FINBRAINTEST to make sure we are using the correct database for the test
    if db.name == 'FinBrainTest':
        users_collection.delete_many({})


def insert_test_user():
    """
    Insert a test user into the database
    """
    users_collection.insert_one({
        "firstName": "User",
        "lastName": "Login",
        "email": "user@login.com",
        "password": hash_password("Secret123"),
    })


def test_login_success():
    """
    Test the login function
    This test checks if the login function is successful
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()

    # Create login data for the test
    login_data = {
        "email": "user@login.com",
        "password": "Secret123",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged in
    assert data['message'] == 'Login successful'
    assert data['session_id'] is not None
    assert data['name'] == 'User'


def test_login_fails_with_missing_fields():
    """
    Test the login function
    This test checks if the login function fails with missing fields
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()

    # Create login data for the test
    login_data = {
        "email": "user@login.com",
        "password": "",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    
    # Check if the user was not logged in
    assert data['message'] == 'Email and password are required'
    assert data.get('session_id') is None
    assert data.get('name') is None
    

def test_login_fails_with_invalid_email_format():
    """
    Test the login function
    This test checks if the login function fails with invalid email format
    """
    # Create a test client
    client = app.test_client()
    
    # Insert a test user into the database
    insert_test_user()
    
    # Create login data for the test
    login_data = {
        "email": "invalid-email",
        "password": "Secret123",
    }
    
    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if the response is unsuccessful
    assert response.status_code == 401
    
    # Check if the user was not logged in
    assert data['message'] == 'Invalid credentials'
    assert data.get('session_id') is None
    assert data.get('name') is None
    

def test_login_fails_with_invalid_password():
    """
    Test the login function
    This test checks if the login function fails with invalid password
    """
    # Create a test client
    client = app.test_client()
    
    # Insert a test user into the database
    insert_test_user()
    
    # Create login data for the test
    login_data = {
        "email": "user@login.com",
        "password": "InvalidPassword",
    }
    
    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if the response is unsuccessful
    assert response.status_code == 401
    
    # Check if the user was not logged in
    assert data['message'] == 'Invalid credentials'
    assert data.get('session_id') is None
    assert data.get('name') is None


def test_login_fails_with_user_not_found():
    """
    Test the login function
    This test checks if the login function fails with user not found
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()

    # Create login data for the test
    login_data = {
        "email": "user@notfound.com",
        "password": "Secret123",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 401
    
    # Check if the user was not logged in
    assert data['message'] == 'Invalid credentials'
    assert data.get('session_id') is None
    assert data.get('name') is None


def test_login_trims_and_lowercases_email():
    """
    Test the login function
    This test checks if the login function trims and lowercases the email
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()

    # Create login data for the test
    login_data = {
        "email": "  User@Login.com  ",
        "password": "Secret123",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged in
    assert data['message'] == 'Login successful'
    assert data['session_id'] is not None
    assert data['name'] == 'User'


def test_login_fails_with_email_too_long():
    """
    Test the login function
    This test checks if the login function fails with email too long
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()
    
    # Create login data for the test
    login_data = {
        "email": "a" * 255,
        "password": "Secret123",
    }
    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if the response is unsuccessful
    assert response.status_code == 401
    
    # Check if the user was not logged in
    assert data['message'] == 'Invalid credentials'
    assert data.get('session_id') is None
    assert data.get('name') is None


def test_login_fails_with_email_too_short():
    """
    Test the login function
    This test checks if the login function fails with email too short
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()
    
    # Create login data for the test
    login_data = {
        "email": "a",
        "password": "Secret123",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if the response is unsuccessful
    assert response.status_code == 401

    # Check if the user was not logged in
    assert data['message'] == 'Invalid credentials'
    assert data.get('session_id') is None
    assert data.get('name') is None


def test_login_handles_database_error():
    """
    Test the login function handles database errors
    This test checks if the login function returns 500 when database fails
    """
    # Create a test client
    client = app.test_client()

    # Insert a test user into the database
    insert_test_user()

    # Mock database error by temporarily breaking the collection
    original_find_one = users_collection.find_one
    def mock_find_one(*args, **kwargs):
        raise Exception("Database connection failed")
    
    users_collection.find_one = mock_find_one

    # Create login data for the test
    login_data = {
        "email": "user@login.com",
        "password": "Secret123",
    }

    # Send a POST request to the login route and get the response
    response = client.post('/login', json=login_data)
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 500
    assert data['message'] == 'Login failed'

    # Restore original function
    users_collection.find_one = original_find_one


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
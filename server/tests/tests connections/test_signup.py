# test_signup.py


from app import app
from db import users_collection, db
import pytest


# Clean the users collection before each test
@pytest.fixture(autouse=True)
def clean_users_collection():
    # Check if the database is FINBRAIN or FINBRAINTEST to make sure we are using the correct database for the test
    if db.name == 'FinBrainTest':
        users_collection.delete_many({})


def test_signup_creates_user():
    """
    Test the signup function
    This test creates a user and checks if the user was created in the database
    and if the user's data is correct
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "Test   ",
        "lastName": "User",
        "email": "test@user.com",
        "password": "Password123",
        "confirmPassword": "Password123"
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is successful
    assert response.status_code == 201
    
    # Check if the user was created in the database
    user = users_collection.find_one({"email": "test@user.com"})
    assert user is not None

    # Check if the user's data is correct
    assert user["firstName"] == "Test"
    assert user["lastName"] == "User"
    assert user["password"] == "Password123"


def test_signup_fails_with_missing_fields():
    """
    Test the signup function
    This test checks if the signup function fails with missing fields
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "Test",
        "lastName": "",
        "email": "test@user.com",
        "password": "Password123",
        "confirmPassword": "Password123"
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    user = users_collection.find_one({"email": "test@user.com"})
    assert user is None


def test_signup_fails_with_invalid_email_format():
    """
    Test the signup function
    This test checks if the signup function fails with invalid email format
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "invalid-email",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": "invalid-email"}) is None


def test_signup_fails_with_invalid_name_format():
    """
    Test the signup function
    This test checks if the signup function fails with invalid name format
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "J0hn",
        "lastName": "Doe",
        "email": "nameformat@user.com",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": "nameformat@user.com"}) is None


def test_signup_fails_with_mismatched_passwords():
    """
    Test the signup function
    This test checks if the signup function fails with mismatched passwords
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "Jane",
        "lastName": "Doe",
        "email": "mismatch@user.com",
        "password": "Password123",
        "confirmPassword": "Password124",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": "mismatch@user.com"}) is None


def test_signup_fails_when_email_already_in_use():
    """
    Test the signup function
    This test checks if the signup function fails when email already exists
    """
    # Create a test client
    client = app.test_client()

    # Create a user in the database
    users_collection.insert_one({
        "firstName": "Existing",
        "lastName": "User",
        "email": "duplicate@user.com",
        "password": "Secret123",
    })

    # Create data for the test
    test_data = {
        "firstName": "New",
        "lastName": "User",
        "email": "duplicate@user.com",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 409


def test_signup_normalizes_email_trim_and_lowercase():
    """
    Test the signup function
    This test checks that email is trimmed and lowercased before storing
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "Norm",
        "lastName": "Alized",
        "email": "  MIXED@Example.com  ",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is successful
    assert response.status_code == 201

    # Check if the user was created in the database with normalized email
    user = users_collection.find_one({"email": "mixed@example.com"})
    assert user is not None
    assert user["email"] == "mixed@example.com"


def test_signup_duplicate_detection_is_case_insensitive():
    """
    Test the signup function
    This test checks that duplicate email detection is case-insensitive
    """
    # Create a test client
    client = app.test_client()

    # Add an existing user with lowercased email
    users_collection.insert_one({
        "firstName": "Existing",
        "lastName": "Case",
        "email": "user@x.com",
        "password": "Secret123",
    })

    # Create data for the test with mixed case
    test_data = {
        "firstName": "New",
        "lastName": "Case",
        "email": "User@X.com",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 409


def test_signup_fails_with_email_too_long():
    """
    Test the signup function
    This test checks that email longer than 254 chars fails
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    long_email = ("a" * 250) + "@ex.com"
    test_data = {
        "firstName": "Long",
        "lastName": "Email",
        "email": long_email,
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": long_email.lower()}) is None


def test_signup_fails_with_name_too_long():
    """
    Test the signup function
    This test checks that first/last name longer than 40 chars fails
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    long_name = "A" * 41
    test_data = {
        "firstName": long_name,
        "lastName": long_name,
        "email": "longname@user.com",
        "password": "Password123",
        "confirmPassword": "Password123",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": "longname@user.com"}) is None


def test_signup_fails_with_missing_password():
    """
    Test the signup function
    This test checks that missing password fails
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "No",
        "lastName": "Pass",
        "email": "missingpass@user.com",
        "password": "",
        "confirmPassword": "",
    }

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user was not created in the database
    assert users_collection.find_one({"email": "missingpass@user.com"}) is None


def test_signup_handles_database_error():
    """
    Test the signup function handles database errors gracefully
    This test checks if the signup function returns 500 when database fails
    """
    # Create a test client
    client = app.test_client()

    # Create data for the test
    test_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "dberror@user.com",
        "password": "Password123",
        "confirmPassword": "Password123"
    }

    # Mock database error by temporarily breaking the collection
    original_find_one = users_collection.find_one
    original_insert_one = users_collection.insert_one
    
    def mock_find_one(*args, **kwargs):
        return None 
    
    def mock_insert_one(*args, **kwargs):
        raise Exception("Database connection failed")
    
    users_collection.find_one = mock_find_one
    users_collection.insert_one = mock_insert_one

    # Send a POST request to the signup route
    response = client.post('/signup', json=test_data)
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 500
    assert data['message'] == 'Signup failed'

    # Restore original functions
    users_collection.find_one = original_find_one
    users_collection.insert_one = original_insert_one
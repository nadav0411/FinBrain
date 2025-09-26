# FinBrain Project - test_heartbeat.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import pytest
from datetime import timedelta
import services.logicconnection as lc
from app import app
import time


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def test_heartbeat_valid_session():
    """
    Test that a heartbeat is successful for a valid session
    """
    # Create session ID and email and store it in Redis
    session_id = "s1"
    email = "test@user.com"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user is still active
    assert data['message'] == 'Heartbeat ok'
    assert data['active'] is True
    assert data['ttl_seconds'] == lc.SESSION_TTL_SECONDS


def test_heartbeat_expired_session():
    """
    Test that a heartbeat is not successful for an expired session
    """
    # Create session ID and email and store it in Redis
    session_id = "s2"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    # Set TTL to 1 second
    lc.r.expire(f"session:{session_id}", 1)

    # Wait for session to expire
    time.sleep(2)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful but session not found
    assert response.status_code == 200

    # Check if the user is not active
    assert data['message'] == 'No such session'
    assert data['active'] is False


def test_heartbeat_none_session_id():
    """
    Test that a heartbeat is not successful for a None session ID
    """
    # Create a test client
    client = app.test_client()
    
    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': None})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user is not active
    assert data['message'] == 'Missing session_id'


def test_heartbeat_empty_session_id():
    """
    Test that a heartbeat is not successful for an empty session ID
    """
    # Create a test client
    client = app.test_client()
    
    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': ''})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user is not active
    assert data['message'] == 'Missing session_id'


def test_heartbeat_nonexistent_session_id():
    """
    Test that a heartbeat is not successful for a non-existent session ID
    """
    # Create a test client
    client = app.test_client()
    
    # Use a session ID that doesn't exist in Redis
    session_id = "nonexistent_session_123"
    
    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful but session not found
    assert response.status_code == 200

    # Check if the user is not active
    assert data['message'] == 'No such session'
    assert data['active'] is False


def test_heartbeat_wrong_http_method_get():
    """
    Test that GET /heartbeat is not allowed (only POST)
    """
    # Create a test client
    client = app.test_client()
    
    # Send a GET request to the heartbeat route and get the response
    response = client.get('/heartbeat')

    # Check if the response is unsuccessful
    assert response.status_code == 405


def test_heartbeat_missing_session_id_header():
    """
    Test that a heartbeat is not successful when session_id is missing
    """
    # Create a test client
    client = app.test_client()
    
    # Send a POST request to the heartbeat route without session_id
    response = client.post('/heartbeat')
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400

    # Check if the user is not active
    assert data['message'] == 'Missing session_id'


def test_heartbeat_null_strings():
    """
    Test that heartbeat with various "null" strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various "null" string values
    null_values = ["null", "None", "undefined", "  null  ", "  None  ", "  undefined  "]
    
    for null_val in null_values:
        # Send a POST request to the heartbeat route and get the response
        response = client.post('/heartbeat', headers={'Session-ID': null_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not active
        assert data['message'] == 'Missing session_id'


def test_heartbeat_whitespace_strings():
    """
    Test that heartbeat with whitespace strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various whitespace values
    whitespace_values = ["   ", "\t", "  \t  "]
    
    for whitespace_val in whitespace_values:
        # Send a POST request to the heartbeat route and get the response
        response = client.post('/heartbeat', headers={'Session-ID': whitespace_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not active
        assert data['message'] == 'Missing session_id'


def test_heartbeat_mixed_case_null_strings():
    """
    Test that heartbeat with mixed case "null" strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various mixed case "null" string values
    null_values = ["NULL", "NONE", "UNDEFINED", "Null", "None", "Undefined"]
    
    for null_val in null_values:
        # Send a POST request to the heartbeat route and get the response
        response = client.post('/heartbeat', headers={'Session-ID': null_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not active
        assert data['message'] == 'Missing session_id'


def test_heartbeat_session_ttl_is_refreshed():
    """
    Test that heartbeat refreshes the session TTL
    """
    # Create session ID and email and store it in Redis with short TTL
    session_id = "ttl_refresh_test"
    email = "test@user.com"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", 10) 

    # Get initial TTL
    initial_ttl = lc.r.ttl(f"session:{session_id}")
    assert initial_ttl > 0
    assert initial_ttl < lc.SESSION_TTL_SECONDS

    # Create a test client
    client = app.test_client()

    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    assert data['message'] == 'Heartbeat ok'
    assert data['active'] is True
    assert data['ttl_seconds'] == lc.SESSION_TTL_SECONDS

    # Check if the TTL was refreshed
    new_ttl = lc.r.ttl(f"session:{session_id}")
    assert new_ttl == lc.SESSION_TTL_SECONDS
    assert new_ttl > initial_ttl


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
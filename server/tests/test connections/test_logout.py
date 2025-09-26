# FinBrain Project - test_logout.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from datetime import timedelta
import services.logicconnection as lc
from app import app


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def test_logout():
    """
    Test that a logout is successful
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
    
    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged out
    assert data['message'] == 'Logout successful'

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_logout_none():
    """
    Test that a logout is not successful if the session ID is None
    """
    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': None})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    
    # Check if the user was not logged out
    assert data['message'] == 'Missing session_id'


def test_logout_existing_session():
    """
    Test that a logout is successful if the session ID exists in Redis
    """
    # Create session ID and email and store it in Redis
    session_id = "s2"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged out
    assert data['message'] == 'Logout successful'

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_logout_nonexistent_session():
    """
    Test that a logout is successful even if the session ID doesn't exist
    """
    # Create session ID that doesn't exist in Redis
    session_id = "s3"

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged out
    assert data['message'] == 'Logout successful'

    # Check if the session is not in Redis
    assert not lc.r.exists(f"session:{session_id}")
    


    
def test_logout_no_header():
    """
    POST /logout without session_id should return 400
    """
    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout')
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert data['message'] == 'Missing session_id'


def test_logout_empty_header():
    """
    Empty session_id should be treated as missing
    """    
    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': ''})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert data['message'] == 'Missing session_id'


def test_logout_whitespace_header():
    """
    Whitespace-only session_id should be treated as missing
    """
    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': '   '})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert data['message'] == 'Missing session_id'


@pytest.mark.parametrize('raw', ['null', 'None', 'undefined', '  null  '])
def test_logout_null_like_header_values(raw):
    """
    Common null-like strings should be treated as missing session_id
    """
    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': raw})
    data = response.get_json()

    # Check if the response is unsuccessful
    assert response.status_code == 400
    assert data['message'] == 'Missing session_id'


def test_two_logout_calls_for_the_same_session():
    """
    Logging out twice: both should succeed
    """
    # Create session ID and email and store it in Redis
    session_id = 'same_session'
    email = 'same@session.com'
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Create a test client
    client = app.test_client()

    # First logout
    r1 = client.post('/logout', headers={'Session-ID': session_id})
    d1 = r1.get_json()
    assert r1.status_code == 200
    assert d1['message'] == 'Logout successful'

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")

    # Second logout for same session
    r2 = client.post('/logout', headers={'Session-ID': session_id})
    d2 = r2.get_json()
    assert r2.status_code == 200
    assert d2['message'] == 'Logout successful'


def test_logout_for_multiple_sessions():
    """
    Only the targeted session should be removed; others remain
    """
    # Create session IDs and emails and store them in Redis
    s1, s2 = 'sA', 'sB'
    lc.r.hset(f"session:{s1}", "email", "a@u.com")
    lc.r.hset(f"session:{s1}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{s1}", lc.SESSION_TTL_SECONDS)
    
    lc.r.hset(f"session:{s2}", "email", "b@u.com")
    lc.r.hset(f"session:{s2}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{s2}", lc.SESSION_TTL_SECONDS)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': s1})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    assert data['message'] == 'Logout successful'

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{s1}")

    # Check if the other session is not removed from Redis
    assert lc.r.exists(f"session:{s2}")


def test_logout_wrong_http_method_get():
    """
    GET /logout should not be allowed (only POST)
    """
    # Create a test client
    client = app.test_client()

    # Send a GET request to the logout route and get the response
    response = client.get('/logout')

    # Check if the response is unsuccessful
    assert response.status_code == 405


def test_logout_expired_session():
    """
    Logout should work on expired sessions (logout doesn't check expiry)
    """
    # Create session ID and email and store it in Redis
    session_id = 's_expired'
    email = 'expired@user.com'
    expired_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS + 1)

    # Store the email and timestamp in Redis
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", expired_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    assert data['message'] == 'Logout successful'

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_logout_null_strings():
    """
    Test that logout with various "null" strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various "null" string values
    null_values = ["null", "None", "undefined", "  null  ", "  None  ", "  undefined  "]
    
    for null_val in null_values:
        # Send a POST request to the logout route and get the response
        response = client.post('/logout', headers={'Session-ID': null_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not logged out
        assert data['message'] == 'Missing session_id'


def test_logout_whitespace_strings():
    """
    Test that logout with whitespace only strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various whitespace only values
    whitespace_values = ["   ", "\t", "  \t  "]
    
    for whitespace_val in whitespace_values:
        # Send a POST request to the logout route and get the response
        response = client.post('/logout', headers={'Session-ID': whitespace_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not logged out
        assert data['message'] == 'Missing session_id'


def test_logout_mixed_case_null_strings():
    """
    Test that logout with mixed case "null" strings returns 400
    """
    # Create a test client
    client = app.test_client()
    
    # Test various mixed case "null" string values
    null_values = ["NULL", "NONE", "UNDEFINED", "Null", "None", "Undefined"]
    
    for null_val in null_values:
        # Send a POST request to the logout route and get the response
        response = client.post('/logout', headers={'Session-ID': null_val})
        data = response.get_json()

        # Check if the response is unsuccessful
        assert response.status_code == 400

        # Check if the user is not logged out
        assert data['message'] == 'Missing session_id'


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
# test_session_ttl_validation.py


import pytest
from datetime import timedelta
import logicconnection as lc
from app import app
import time


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def test_session_ttl_is_set_correctly_on_login():
    """
    Test that sessions are created with correct TTL on login
    """
    # Create a test client
    client = app.test_client()

    # First create a user
    signup_data = {
        "firstName": "TTL", "lastName": "Test", 
        "email": "ttl@test.com", "password": "testpass", "confirmPassword": "testpass"
    }
    client.post('/signup', json=signup_data)

    # Login to create session
    login_data = {"email": "ttl@test.com", "password": "testpass"}
    response = client.post('/login', json=login_data)
    data = response.get_json()
    
    # Check if login was successful
    assert response.status_code == 200
    assert data['message'] == 'Login successful'
    session_id = data['session_id']
    
    # Check TTL is set correctly
    ttl = lc.r.ttl(f"session:{session_id}")
    assert 0 < ttl <= lc.SESSION_TTL_SECONDS


def test_session_ttl_is_refreshed_on_heartbeat():
    """
    Test that session TTL is refreshed when heartbeat is called
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

    # Send heartbeat to refresh TTL
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if heartbeat was successful
    assert response.status_code == 200
    assert data['message'] == 'Heartbeat ok'
    assert data['active'] is True

    # Check if the TTL was refreshed
    new_ttl = lc.r.ttl(f"session:{session_id}")
    assert new_ttl == lc.SESSION_TTL_SECONDS
    assert new_ttl > initial_ttl


def test_session_ttl_is_refreshed_on_get_email():
    """
    Test that session TTL is refreshed when get_email_from_session_id is called
    """
    # Create session ID and email and store it in Redis with short TTL
    session_id = "ttl_refresh_email_test"
    email = "test@user.com"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", 10) 

    # Get initial TTL
    initial_ttl = lc.r.ttl(f"session:{session_id}")
    assert initial_ttl > 0
    assert initial_ttl < lc.SESSION_TTL_SECONDS

    # Call get_email_from_session_id to refresh TTL
    returned_email = lc.get_email_from_session_id(session_id)
    
    # Check if email was returned
    assert returned_email == email

    # Check if the TTL was refreshed
    new_ttl = lc.r.ttl(f"session:{session_id}")
    assert new_ttl == lc.SESSION_TTL_SECONDS
    assert new_ttl > initial_ttl


def test_session_expires_after_ttl():
    """
    Test that session expires after TTL seconds
    """
    # Create session ID and email and store it in Redis
    session_id = "expiry_test"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", 2)  # Set short TTL for testing

    # Check if session exists initially
    assert lc.r.exists(f"session:{session_id}")
    assert not lc.is_session_expired(session_id)

    # Wait for session to expire
    time.sleep(3)

    # Check if session is expired
    assert lc.is_session_expired(session_id)
    assert not lc.r.exists(f"session:{session_id}")


def test_session_ttl_constant_value():
    """
    Test that SESSION_TTL_SECONDS constant has expected value
    """
    # Check if the constant has the expected value
    assert lc.SESSION_TTL_SECONDS == 90


def test_multiple_sessions_have_independent_ttl():
    """
    Test that multiple sessions have independent TTL
    """
    # Create two sessions with different TTLs
    session1 = "session1"
    session2 = "session2"
    email1 = "user1@test.com"
    email2 = "user2@test.com"
    
    # Short TTL
    lc.r.hset(f"session:{session1}", "email", email1)
    lc.r.hset(f"session:{session1}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session1}", 2)  
    
    # Longer TTL
    lc.r.hset(f"session:{session2}", "email", email2)
    lc.r.hset(f"session:{session2}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session2}", 5)  

    # Check both sessions exist initially
    assert not lc.is_session_expired(session1)
    assert not lc.is_session_expired(session2)

    # Wait for first session to expire
    time.sleep(3)

    # Check first session is expired but second is not
    assert lc.is_session_expired(session1)
    assert not lc.is_session_expired(session2)

    # Wait for second session to expire
    time.sleep(3)

    # Check both sessions are expired
    assert lc.is_session_expired(session1)
    assert lc.is_session_expired(session2)


def test_session_ttl_after_logout():
    """
    Test that session TTL is not relevant after logout
    """
    # Create session ID and email and store it in Redis
    session_id = "logout_ttl_test"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if session exists initially
    assert lc.r.exists(f"session:{session_id}")

    # Create a test client
    client = app.test_client()

    # Logout
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if logout was successful
    assert response.status_code == 200
    assert data['message'] == 'Logout successful'

    # Check if session is removed
    assert not lc.r.exists(f"session:{session_id}")
    assert lc.is_session_expired(session_id)


def test_session_ttl_with_heartbeat_keeps_alive():
    """
    Test that regular heartbeats keep session alive beyond original TTL
    """
    # Create session ID and email and store it in Redis
    session_id = "heartbeat_keepalive_test"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", 3) 

    # Create a test client
    client = app.test_client()

    # Send heartbeats every 2 seconds to keep session alive
    for i in range(3):
        response = client.post('/heartbeat', headers={'Session-ID': session_id})
        data = response.get_json()
        
        # Check if heartbeat was successful
        assert response.status_code == 200
        assert data['message'] == 'Heartbeat ok'
        assert data['active'] is True
        
        # Check if session still exists
        assert not lc.is_session_expired(session_id)
        assert lc.r.exists(f"session:{session_id}")
        
        # Wait before next heartbeat
        time.sleep(2)

    # Check if session is still alive after multiple heartbeats
    assert not lc.is_session_expired(session_id)
    assert lc.r.exists(f"session:{session_id}")


def test_session_ttl_without_heartbeat_expires():
    """
    Test that session expires without heartbeat
    """
    # Create session ID and email and store it in Redis
    session_id = "no_heartbeat_test"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", 2) 

    # Check if session exists initially
    assert not lc.is_session_expired(session_id)
    assert lc.r.exists(f"session:{session_id}")

    # Wait for session to expire without heartbeat
    time.sleep(3)

    # Check if session is expired
    assert lc.is_session_expired(session_id)
    assert not lc.r.exists(f"session:{session_id}")


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True

# test_heartbeat.py


import pytest
from datetime import timedelta
import logicconnection as lc
from app import app


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()


def test_heartbeat_valid_session():
    """
    Test that a heartbeat is successful for a valid session
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s1"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user is still active
    assert data['message'] == 'Heartbeat ok'

    # Check if the user is still active
    assert data['active'] is True
    assert data['ttl_minutes'] == lc.SESSION_TTL_MINUTES


def test_heartbeat_expired_session():
    """
    Test that a heartbeat is not successful for an expired session
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s2"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the heartbeat route and get the response
    response = client.post('/heartbeat', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response unsuccessful
    assert response.status_code == 200

    # Check if the user is not active
    assert data['message'] == 'Session expired'
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

    # Check if the response unsuccessful
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

    # Check if the response unsuccessful
    assert response.status_code == 400

    # Check if the user is not active
    assert data['message'] == 'Missing session_id'



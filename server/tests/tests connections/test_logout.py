# test_logout.py


import pytest
from datetime import timedelta
import logicconnection as lc
from app import app


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()


def test_logout():
    """
    Test that a logout is successful
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s1"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)

    # Create a test client
    client = app.test_client()
    
    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged out
    assert data['message'] == 'Logout successful'
    assert data['revoked'] is True

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


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


def test_logout_exist_only_connected_session():
    """
    Test that a logout is successful if the session ID is only in the connected sessions dictionary
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s2"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the user was logged out
    assert data['message'] == 'Logout successful'
    assert data['revoked'] is True

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_logout_not_exist_session():
    """
    Test that a logout is not successful if the session ID is not exist
    """
    # Create session ID that not exist in the dictionary
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
    assert data['revoked'] is False

    # Check if the session is not in the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions
    


    
def test_logout_no_header():
    """
    POST /logout without Session-ID header or query param should return 400
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
    Empty Session-ID header should be treated as missing
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
    Whitespace-only Session-ID header should be treated as missing
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
    Logging out twice: first True, then False
    """
    # Create session ID and email and store it in the dictionary
    session_id = 'same_session'
    email = 'same@session.com'
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc()

    # Create a test client
    client = app.test_client()

    # First logout
    r1 = client.post('/logout', headers={'Session-ID': session_id})
    d1 = r1.get_json()
    assert r1.status_code == 200
    assert d1['revoked'] is True

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions

    # Second logout for same session
    r2 = client.post('/logout', headers={'Session-ID': session_id})
    d2 = r2.get_json()
    assert r2.status_code == 200
    assert d2['revoked'] is False


def test_logout_for_multiple_sessions():
    """
    Only the targeted session should be removed; others remain
    """
    # Create session IDs and emails and store them in the dictionary
    s1, s2 = 'sA', 'sB'
    lc.connected_sessions[s1] = 'a@u.com'
    lc.connected_sessions[s2] = 'b@u.com'
    lc.last_seen_sessions[s1] = lc.get_now_utc()
    lc.last_seen_sessions[s2] = lc.get_now_utc()

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': s1})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    assert data['revoked'] is True

    # Check if the session is removed from the dictionary
    assert s1 not in lc.connected_sessions
    assert s1 not in lc.last_seen_sessions

    # Check if the other session is not removed from the dictionary
    assert s2 in lc.connected_sessions
    assert s2 in lc.last_seen_sessions


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
    # Create session ID and email and store it in the dictionary
    session_id = 's_expired'
    email = 'expired@user.com'

    # Store the email and last seen timestamp in the dictionary
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)

    # Create a test client
    client = app.test_client()

    # Send a POST request to the logout route and get the response
    response = client.post('/logout', headers={'Session-ID': session_id})
    data = response.get_json()

    # Check if the response is successful
    assert response.status_code == 200
    assert data['message'] == 'Logout successful'
    assert data['revoked'] is True

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions
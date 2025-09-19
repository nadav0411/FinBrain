# test_email_from_session_id.py


import pytest
from datetime import timedelta
import logicconnection as lc


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()


def test_valid_session():
    """
    Test that a valid session is returned
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s1"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)

    # Check if the email is returned
    assert lc.get_email_from_session_id(session_id) == email

    # Check if the last seen timestamp is updated (allow for small time differences -> 10ms difference)
    now = lc.get_now_utc()
    last_seen = lc.last_seen_sessions[session_id]
    time_diff = abs((now - last_seen).total_seconds())
    assert time_diff < 0.1


def test_expired_session():
    """
    Test that a expired session is returned None
    """
    # Create session ID and email and store it in the dictionary
    session_id = "s2"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)
    
    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_session_not_found():
    """
    Test that a not real session ID is returned None
    """
    # Not real session ID
    session_id = "s3"

    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session is not in the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_last_seen_updated_on_access():
    """
    Test that the last seen timestamp is updated on access
    """
    # Create session ID and email and store it in the dictionary
    session_id = "touch_me"
    email = "touch@test.com"
    lc.connected_sessions[session_id] = email

    # Create a near expiry timestamp
    near_expiry = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 0.1)
    lc.last_seen_sessions[session_id] = near_expiry

    # Check if the email is returned
    returned = lc.get_email_from_session_id(session_id)
    assert returned == email

    # Check if the last seen timestamp is updated
    assert lc.last_seen_sessions[session_id] > near_expiry


def test_only_requested_session_is_touched():
    """
    Test that only the requested session is touched
    """
    # Create session IDs and emails and store them in the dictionary
    s1, s2 = "s1", "s2"
    e1, e2 = "a@a.com", "b@b.com"
    lc.connected_sessions[s1] = e1
    lc.connected_sessions[s2] = e2

    # Create a near expiry timestamp
    t1 = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 0.02)
    t2 = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 0.02)
    # Store the timestamps in the dictionary
    lc.last_seen_sessions[s1] = t1
    lc.last_seen_sessions[s2] = t2

    # Check if the email is returned
    assert lc.get_email_from_session_id(s1) == e1

    # Check if the last seen timestamp is updated for the requested session only
    assert lc.last_seen_sessions[s1] > t1
    assert lc.last_seen_sessions[s2] == t2


def test_none_session_id():
    """
    Test that a None session ID is returned None
    """
    # Check if the email is not returned
    assert lc.get_email_from_session_id(None) is None

    # Check if the session is not in the dictionary
    assert None not in lc.connected_sessions
    assert None not in lc.last_seen_sessions


def test_empty_session_id():
    """
    Test that a empty session ID is returned None
    """
    assert lc.get_email_from_session_id("") is None
    assert "" not in lc.connected_sessions
    assert "" not in lc.last_seen_sessions


def test_session_at_ttl_boundary_is_expired():
    """
    If last_seen is exactly TTL minutes ago, it should be treated as expired.
    """
    # Create session ID and email and store it in the dictionary
    session_id = "ttl_boundary"
    email = "boundary@test.com"

    # Store the email and last seen timestamp in the dictionary
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES)

    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_missing_last_seen_is_initialized_on_access():
    """
    If a session exists without last_seen, accessing should return email and set last_seen.
    """
    # Create session ID and email and store it in the dictionary
    session_id = "no_last_seen"
    email = "init@test.com"
    # Store the email in the dictionary without last seen
    lc.connected_sessions[session_id] = email

    # Check if the email is returned
    returned = lc.get_email_from_session_id(session_id)
    assert returned == email

    # Check if the last seen timestamp is set
    assert session_id in lc.last_seen_sessions
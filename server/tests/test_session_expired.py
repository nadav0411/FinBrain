# test_session_expired.py


import pytest
from datetime import datetime, timedelta
import logicconnection as lc


# Clean the last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_users_collection():
    lc.last_seen_sessions.clear()


def test_session_recently_active():
    """
    Test that a session is not expired if it was recently active
    """
    # Create a session ID with the time now and store it in the dictionary
    session_id = "s1"
    lc.last_seen_sessions[session_id] = lc.get_now_utc()

    # Check if the session is not expired
    assert lc.is_session_expired(session_id) is False


def test_session_expired():
    """
    Test that a session is expired if it was not recently active
    """
    # Create a session ID with the time that expired and store it in the dictionary
    session_id = "s2"
    old_time = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)
    lc.last_seen_sessions[session_id] = old_time

    # Check if the session is expired
    assert lc.is_session_expired(session_id) is True


def test_multiple_sessions_mixed():
    """
    Test that a session is not expired if it was recently active and another session is expired
    """
    # Create two session IDs with the time now and the time that expired and store them in the dictionary
    active_id = "active"
    expired_id = "expired"
    lc.last_seen_sessions[active_id] = lc.get_now_utc()
    lc.last_seen_sessions[expired_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 2)

    # Check if the sessions are expired
    assert lc.is_session_expired(active_id) is False
    assert lc.is_session_expired(expired_id) is True


def test_session_exactly_at_ttl_boundary():
    """
    Test that a session is expired if it was exactly at the TTL boundary
    """
    # Create a session ID with the time exactly at TTL boundary and store it in the dictionary
    session_id = "boundary"
    boundary_time = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES)
    lc.last_seen_sessions[session_id] = boundary_time

    # Check if the session is expired (should be expired at exact boundary)
    assert lc.is_session_expired(session_id) is True


def test_session_just_under_ttl_boundary():
    """
    Test that a session is not expired if it was just under the TTL boundary
    """
    # Create a session ID with the time just under TTL boundary
    session_id = "just_under_boundary"
    under_boundary_time = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 0.001)
    lc.last_seen_sessions[session_id] = under_boundary_time

    # Check if the session is not expired 
    assert lc.is_session_expired(session_id) is False


def test_session_with_very_small_time_difference():
    """
    Test that a session is not expired with a very small time difference
    """
    # Create a session ID with a very small time difference (microseconds)
    session_id = "microseconds_old"
    very_recent_time = lc.get_now_utc() - timedelta(microseconds=1)
    lc.last_seen_sessions[session_id] = very_recent_time

    # Check if the session is not expired
    assert lc.is_session_expired(session_id) is False


def test_nonexistent_session():
    """
    Test that a nonexistent session returns False (not expired)
    """
    # Create a session ID that does not exist in the dictionary
    nonexistent_id = "nonexistent"

    # Check if the nonexistent session is expired
    assert lc.is_session_expired(nonexistent_id) is False

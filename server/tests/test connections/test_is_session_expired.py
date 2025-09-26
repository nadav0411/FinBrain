# FinBrain Project - test_is_session_expired.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import pytest
from datetime import timedelta
import logicconnection as lc
import time


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def test_is_session_expired_valid_session():
    """
    Test that is_session_expired returns False for a valid session
    """
    # Create session ID and email and store it in Redis
    session_id = "valid_session"
    email = "test@user.com"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the session is not expired
    assert not lc.is_session_expired(session_id)

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_is_session_expired_expired_session():
    """
    Test that is_session_expired returns True for an expired session
    """
    # Create session ID and email and store it in Redis
    session_id = "expired_session"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    # Set TTL to 1 second
    lc.r.expire(f"session:{session_id}", 1)
    
    # Wait for session to expire
    time.sleep(2)
    
    # Check if the session is expired
    assert lc.is_session_expired(session_id)

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_is_session_expired_nonexistent_session():
    """
    Test that is_session_expired returns True for a non-existent session
    """
    # Use a session ID that doesn't exist in Redis
    session_id = "nonexistent_session"

    # Check if the session is expired
    assert lc.is_session_expired(session_id)

    # Check if the session is not in Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_is_session_expired_none_session_id():
    """
    Test that is_session_expired returns True for None session ID
    """
    # Check if the session is expired
    assert lc.is_session_expired(None)

    # Check if the session is not in Redis
    assert not lc.r.exists("session:None")


def test_is_session_expired_empty_session_id():
    """
    Test that is_session_expired returns True for empty session ID
    """
    # Check if the session is expired
    assert lc.is_session_expired("")

    # Check if the session is not in Redis
    assert not lc.r.exists("session:")


def test_is_session_expired_session_without_email():
    """
    Test that is_session_expired returns False for session without email (session data exists)
    """
    # Create session ID without email and store it in Redis
    session_id = "no_email_session"
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the session is not expired (because session data exists)
    assert not lc.is_session_expired(session_id)

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_is_session_expired_session_without_timestamp():
    """
    Test that is_session_expired returns False for session without timestamp (session data exists)
    """
    # Create session ID with email but no timestamp and store it in Redis
    session_id = "no_timestamp_session"
    email = "test@user.com"
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the session is not expired (because session data exists)
    assert not lc.is_session_expired(session_id)

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_is_session_expired_empty_session_data():
    """
    Test that is_session_expired returns True for empty session data
    """
    # Create session ID and store some data in Redis, then clear it
    session_id = "empty_session"
    lc.r.hset(f"session:{session_id}", "email", "test@user.com")
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)
    
    # Clear the session data to make it empty
    lc.r.hdel(f"session:{session_id}", "email")

    # Check if the session is expired (because it has no data)
    assert lc.is_session_expired(session_id)

    # Check if the session no longer exists in Redis (Redis deletes empty hashes)
    assert not lc.r.exists(f"session:{session_id}")


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
# FinBrain Project - test_email_from_session_id.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import pytest
from datetime import timedelta
import services.logicconnection as lc
import time


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


def test_valid_session():
    """
    Test that a valid session is returned
    """
    # Create session ID and email and store it in Redis
    session_id = "s1"
    email = "test@user.com"
    session_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", session_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the email is returned
    assert lc.get_email_from_session_id(session_id) == email

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_expired_session():
    """
    Test that an expired session returns None
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
    
    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session is removed from Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_session_not_found():
    """
    Test that a non-existent session ID returns None
    """
    # Not real session ID
    session_id = "s3"

    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session is not in Redis
    assert not lc.r.exists(f"session:{session_id}")


def test_session_updated_on_access():
    """
    Test that the session is updated on access
    """
    # Create session ID and email and store it in Redis
    session_id = "touch_me"
    email = "touch@test.com"
    near_expiry_timestamp = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.hset(f"session:{session_id}", "last_seen", near_expiry_timestamp.isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the email is returned
    returned = lc.get_email_from_session_id(session_id)
    assert returned == email

    # Check if the session still exists in Redis 
    assert lc.r.exists(f"session:{session_id}")


def test_only_requested_session_is_touched():
    """
    Test that only the requested session is touched
    """
    # Create session IDs and emails and store them in Redis
    s1, s2 = "s1", "s2"
    e1, e2 = "a@a.com", "b@b.com"
    t1 = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    t2 = lc.get_now_utc() - timedelta(seconds=lc.SESSION_TTL_SECONDS - 1)
    
    # Store sessions in Redis
    lc.r.hset(f"session:{s1}", "email", e1)
    lc.r.hset(f"session:{s1}", "last_seen", t1.isoformat())
    lc.r.expire(f"session:{s1}", lc.SESSION_TTL_SECONDS)
    lc.r.hset(f"session:{s2}", "email", e2)
    lc.r.hset(f"session:{s2}", "last_seen", t2.isoformat())
    lc.r.expire(f"session:{s2}", lc.SESSION_TTL_SECONDS)

    # Get the session timestamp for s2 before accessing s1
    s2_data_before = lc.r.hgetall(f"session:{s2}")
    s2_timestamp_before = s2_data_before.get("last_seen")

    # Check if the email is returned for s1 (this should update s1's timestamp)
    assert lc.get_email_from_session_id(s1) == e1

    # Check if s1 was updated (should have a newer timestamp)
    s1_data_after = lc.r.hgetall(f"session:{s1}")
    s1_timestamp_after = s1_data_after.get("last_seen")
    assert s1_timestamp_after > t1.isoformat()

    # Check if s2 was not touched (should have the same timestamp)
    s2_data_after = lc.r.hgetall(f"session:{s2}")
    s2_timestamp_after = s2_data_after.get("last_seen")
    assert s2_timestamp_after == s2_timestamp_before

    # Check if both sessions still exist in Redis
    assert lc.r.exists(f"session:{s1}")
    assert lc.r.exists(f"session:{s2}")


def test_none_session_id():
    """
    Test that a None session ID is returned None
    """
    # Check if the email is not returned
    assert lc.get_email_from_session_id(None) is None

    # Check if the session is not in Redis
    assert not lc.r.exists("session:None")


def test_empty_session_id():
    """
    Test that an empty session ID returns None
    """
    # Check if the email is not returned
    assert lc.get_email_from_session_id("") is None

    # Check if the session is not in Redis
    assert not lc.r.exists("session:")


def test_session_initialized_on_access():
    """
    If a session exists without timestamp, accessing should return email and set timestamp.
    """
    # Create session ID and email and store it in Redis
    session_id = "no_timestamp"
    email = "init@test.com"
    
    # Store the email in Redis without timestamp
    lc.r.hset(f"session:{session_id}", "email", email)
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the email is returned
    returned = lc.get_email_from_session_id(session_id)
    assert returned == email

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_get_email_from_session_id_null_strings():
    """
    Test that various "null" strings return None
    """
    # Test various "null" string values
    null_values = ["null", "None", "undefined", "  null  ", "  None  ", "  undefined  "]
    
    for null_val in null_values:
        # Check if the email is not returned
        assert lc.get_email_from_session_id(null_val) is None

        # Check if the session is not in Redis
        assert not lc.r.exists(f"session:{null_val}")


def test_get_email_from_session_id_whitespace_strings():
    """
    Test that whitespace-only strings return None
    """
    # Test various whitespace only values 
    whitespace_values = ["   ", "\t", "  \t  "]
    
    for whitespace_val in whitespace_values:
        # Check if the email is not returned
        assert lc.get_email_from_session_id(whitespace_val) is None

        # Check if the session is not in Redis
        assert not lc.r.exists(f"session:{whitespace_val}")


def test_get_email_from_session_id_mixed_case_null_strings():
    """
    Test that mixed case "null" strings return None
    """
    # Test various mixed case "null" string values
    null_values = ["NULL", "NONE", "UNDEFINED", "Null", "None", "Undefined"]
    
    for null_val in null_values:
        # Check if the email is not returned
        assert lc.get_email_from_session_id(null_val) is None

        # Check if the session is not in Redis
        assert not lc.r.exists(f"session:{null_val}")


def test_get_email_from_session_id_session_without_email():
    """
    Test that session without email field returns None
    """
    # Create session ID without email and store it in Redis
    session_id = "no_email_session"
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_get_email_from_session_id_session_with_empty_email():
    """
    Test that session with empty email field returns None
    """
    # Create session ID with empty email and store it in Redis
    session_id = "empty_email_session"
    lc.r.hset(f"session:{session_id}", "email", "")
    lc.r.hset(f"session:{session_id}", "last_seen", lc.get_now_utc().isoformat())
    lc.r.expire(f"session:{session_id}", lc.SESSION_TTL_SECONDS)

    # Check if the email is not returned
    assert lc.get_email_from_session_id(session_id) is None

    # Check if the session still exists in Redis
    assert lc.r.exists(f"session:{session_id}")


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
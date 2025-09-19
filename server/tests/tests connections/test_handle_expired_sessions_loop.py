# test_handle_expired_sessions_loop.py


from tkinter import N
import pytest
from datetime import timedelta
import logicconnection as lc
from app import app


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()


def test_expired_session_removed():
    """
    Test that an expired session is removed from the dictionary
    """
    # Create session ID and email and store it in the dictionary
    session_id = "expired"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)

    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)

    # Check if the session is removed from the dictionary
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_active_session_not_removed():
    """
    Test that an active session is not removed from the dictionary
    """
    # Create session ID and email and store it in the dictionary
    session_id = "active"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)

    # Check if the session is not removed from the dictionary
    assert session_id in lc.connected_sessions
    assert session_id in lc.last_seen_sessions


def test_mixed_sessions():
    """
    Test that a mixed session is not removed from the dictionary
    """
    # Create session IDs and emails and store them in the dictionary
    expired_session_id = "expired"
    active_session_id = "active"
    expired_email = "expired@user.com"
    active_email = "active@user.com"
    lc.connected_sessions[expired_session_id] = expired_email
    lc.last_seen_sessions[expired_session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)
    lc.connected_sessions[active_session_id] = active_email
    lc.last_seen_sessions[active_session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)

    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)

    # Check session 1 is removed and session 2 is not removed
    assert expired_session_id not in lc.connected_sessions
    assert expired_session_id not in lc.last_seen_sessions
    assert active_session_id in lc.connected_sessions
    assert active_session_id in lc.last_seen_sessions


def test_function_handles_exception():
    """
    Test that the function handles an exception
    """
    # Create session ID and email and store it in the dictionary
    session_id = "exception"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = "None"
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    try:
        lc.handle_expired_session_loop(now)
    except Exception:
        pytest.fail("Exception should not be raised")


def test_empty_dictionaries():
    """
    Test that the function handles empty dictionaries
    """
    # Ensure dictionaries are empty
    assert len(lc.connected_sessions) == 0
    assert len(lc.last_seen_sessions) == 0
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)
    
    # Dictionaries should still be empty
    assert len(lc.connected_sessions) == 0
    assert len(lc.last_seen_sessions) == 0


def test_session_in_connected_but_not_last_seen():
    """
    Test session exists in connected_sessions but not in last_seen_sessions
    """
    # Create session ID and email and store them in the dictionary (only connected_sessions)
    session_id = "test"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)
    
    # Session should remain in connected_sessions since it's not in last_seen_sessions
    assert session_id in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions


def test_session_in_last_seen_but_not_connected():
    """
    Test session exists in last_seen_sessions but not in connected_sessions
    """
    # Create session ID and store it in the dictionary (only last_seen_sessions)
    session_id = "test"
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)
    
    # Session should be removed from last_seen_sessions
    assert session_id not in lc.last_seen_sessions
    assert session_id not in lc.connected_sessions


def test_exactly_at_ttl_boundary():
    """
    Test session exactly at TTL boundary
    """
    # Create session ID and email and store them in the dictionary
    session_id = "boundary"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES)
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)
    
    # Session should be removed
    assert session_id not in lc.connected_sessions
    assert session_id not in lc.last_seen_sessions

   
def test_none_last_seen_timestamp():
    """
    Test handling of None values in last_seen_sessions
    """
    session_id = "none_timestamp"
    email = "test@user.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = None
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    try:
        lc.handle_expired_session_loop(now)
    except Exception:
        pytest.fail("Exception should not be raised for None timestamp")


def test_large_number_of_sessions():
    """
    Test performance with large number of sessions
    """
    # Create many sessions (mix of expired and active)
    for i in range(100):
        session_id = f"session_{i}"
        email = f"user{i}@test.com"
        lc.connected_sessions[session_id] = email
        
        # Make every other session expired
        if i % 2 == 0:
            lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES + 1)
        else:
            lc.last_seen_sessions[session_id] = lc.get_now_utc() - timedelta(minutes=lc.SESSION_TTL_MINUTES - 1)
    
    # Handle the expired session loop
    now = lc.get_now_utc()
    lc.handle_expired_session_loop(now)
    
    # Should have exactly 50 sessions remaining (the active ones)
    assert len(lc.connected_sessions) == 50
    assert len(lc.last_seen_sessions) == 50
    
    # Verify only active sessions remain
    for i in range(100):
        session_id = f"session_{i}"
        if i % 2 == 0: 
            assert session_id not in lc.connected_sessions
            assert session_id not in lc.last_seen_sessions
        else: 
            assert session_id in lc.connected_sessions
            assert session_id in lc.last_seen_sessions


def test_handle_invalid_timestamp_data():
    """
    Test handling of invalid timestamp data in last_seen_sessions
    """
    # Create session with invalid timestamp data
    session_id = "invalid_timestamp"
    email = "invalid@test.com"
    lc.connected_sessions[session_id] = email
    lc.last_seen_sessions[session_id] = "invalid_string_timestamp"
    
    # Handle the expired session loop - should not crash
    now = lc.get_now_utc()
    try:
        lc.handle_expired_session_loop(now)
    except Exception as e:
        pytest.fail(f"handle_expired_session_loop should handle invalid timestamps gracefully, but raised: {e}")
    
    # Session should still exist since we can't determine if it's expired
    assert session_id in lc.connected_sessions
    assert session_id in lc.last_seen_sessions







# test_email_from_session_id.py


import pytest
from datetime import datetime, timedelta, timezone
import logicconnection as lc


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()


def test_valid_session():
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
    assert time_diff < 0.01





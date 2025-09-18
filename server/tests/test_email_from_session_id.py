# test_email_from_session_id.py


import pytest
from datetime import datetime, timedelta, timezone
import logicconnection as lc


# Clean the connected and last seen sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    lc.connected_sessions.clear()
    lc.last_seen_sessions.clear()



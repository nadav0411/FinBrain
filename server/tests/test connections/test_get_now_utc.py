# FinBrain Project - test_get_now_utc.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import pytest
import services.logicconnection as lc
from datetime import datetime, timezone
import time


def test_get_now_utc_returns_datetime():
    """
    Test that get_now_utc returns a datetime object
    """
    # Get current UTC time
    now = lc.get_now_utc()
    
    # Check if it's a datetime object
    assert isinstance(now, datetime)


def test_get_now_utc_returns_utc_timezone():
    """
    Test that get_now_utc returns timezone-aware UTC datetime
    """
    # Get current UTC time
    now = lc.get_now_utc()
    
    # Check if it has timezone info
    assert now.tzinfo is not None
    
    # Check if it's UTC timezone
    assert now.tzinfo == timezone.utc


def test_get_now_utc_returns_recent_time():
    """
    Test that get_now_utc returns a recent time (within last second)
    """
    # Get current UTC time
    now = lc.get_now_utc()
    
    # Get expected time
    expected = datetime.now(timezone.utc)
    
    # Check if the difference is less than 1 second
    time_diff = abs((now - expected).total_seconds())
    assert time_diff < 1.0


def test_get_now_utc_returns_different_times():
    """
    Test that get_now_utc returns different times when called at different moments
    """
    # Get first time
    time1 = lc.get_now_utc()
    
    # Wait a small amount
    time.sleep(0.01)
    
    # Get second time
    time2 = lc.get_now_utc()
    
    # Check if they are different
    assert time1 != time2
    
    # Check if time2 is after time1
    assert time2 > time1


def test_get_now_utc_returns_iso_format_compatible():
    """
    Test that get_now_utc returns time that can be converted to ISO format
    """
    # Get current UTC time
    now = lc.get_now_utc()
    
    # Check if it can be converted to ISO format 
    iso_string = now.isoformat()
    
    # Check if the ISO string is not empty
    assert iso_string != ""
    
    # Check if the ISO string contains timezone info
    assert iso_string.endswith("+00:00") or iso_string.endswith("Z")


def test_get_now_utc_consistency():
    """
    Test that get_now_utc is consistent with Python's datetime.now(timezone.utc)
    """
    # Get time from our function
    our_time = lc.get_now_utc()
    
    # Get time from Python's built-in function
    python_time = datetime.now(timezone.utc)
    
    # Check if they are very close (within 1 second)
    time_diff = abs((our_time - python_time).total_seconds())
    assert time_diff < 1.0


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
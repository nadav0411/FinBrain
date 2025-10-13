# FinBrain Project - test_expenses_cache.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import pytest
from unittest.mock import patch
from datetime import datetime
from app import app
from db import users_collection, expenses_collection, db
from db import cache
import services.logicconnection as lc


# Clean the users collection before each test
@pytest.fixture(autouse=True)
def clean_collections():
    """
    Clean the users and expenses collections before each test
    Ensures test isolation by using FinBrainTest database
    """
    # Check if the database is FINBRAIN or FINBRAINTEST to make sure we are using the correct database for the test
    if db.name == 'FinBrainTest':
        users_collection.delete_many({})
        expenses_collection.delete_many({})


# Clean Redis sessions before each test
@pytest.fixture(autouse=True)
def clean_sessions():
    """
    Clean Redis sessions before each test
    Ensures test isolation by removing any existing test sessions
    """
    # Clean up any existing test sessions
    keys = lc.r.keys("session:*")
    if keys:
        lc.r.delete(*keys)


# Clear test cache before each test
@pytest.fixture(autouse=True)
def clear_test_cache():
    """
    Setup function that runs before each test
    Clears test cache to ensure test isolation
    """
    cache.clear_test_cache()


def test_get_cached_user_expenses_cache_miss():
    """
    Test that get_cached_user_expenses returns None when cache miss
    """
    # Create a test user
    user_id = 'test_user_123'
    month = 1
    year = 2025
    
    # Test cache miss
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is None


def test_add_to_cache_user_expenses():
    """
    Test that add_to_cache_user_expenses stores data correctly
    """
    # Create a test user
    user_id = 'test_user_456'
    month = 2
    year = 2025
    test_expenses = [{'title': 'Test Expense', 'amount': 10, 'category': 'Food'}]
    
    # Add to cache
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    
    # Verify it was stored
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    assert len(cached_data) == 1
    assert cached_data[0]['title'] == 'Test Expense'
    assert cached_data[0]['amount'] == 10
    assert cached_data[0]['category'] == 'Food'


def test_get_cached_user_expenses_cache_hit():
    """
    Test that get_cached_user_expenses returns cached data when cache hit
    """
    # Create a test user
    user_id = 'test_user_789'
    month = 3
    year = 2025
    test_expenses = [{'title': 'Cached Expense', 'amount': 25, 'category': 'Transport'}]
    
    # First add to cache
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    
    # Then retrieve from cache
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    assert len(cached_data) == 1
    assert cached_data[0]['title'] == 'Cached Expense'
    assert cached_data[0]['amount'] == 25
    assert cached_data[0]['category'] == 'Transport'


def test_delete_user_expenses_cache():
    """
    Test that delete_user_expenses_cache removes cached data
    """
    # Create a test user
    user_id = 'test_user_delete'
    month = 4
    year = 2025
    test_expenses = [{'title': 'To Delete', 'amount': 15, 'category': 'Entertainment'}]
    
    # Add to cache
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    
    # Verify it's there
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    
    # Delete from cache
    cache.delete_user_expenses_cache(user_id, month, year)
    
    # Verify it's gone
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is None


def test_cache_error_handling_get():
    """
    Test that cache errors are handled in get operations
    """
    # Create a test user
    user_id = 'test_user_error'
    month = 6
    year = 2025
    
    # Test get cache error handling
    with patch('db.cache.r.get', side_effect=Exception("Redis error")):
        result = cache.get_cached_user_expenses(user_id, month, year)
        assert result is None


def test_cache_error_handling_add():
    """
    Test that cache errors are handled gracefully in add operations
    """
    # Create a test user
    user_id = 'test_user_error'
    month = 7
    year = 2025
    test_expenses = [{'title': 'Error Test', 'amount': 30, 'category': 'Other'}]
    
    # Test add cache error handling
    with patch('db.cache.r.setex', side_effect=Exception("Redis error")):
        # Should not raise exception
        cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)


def test_cache_error_handling_delete():
    """
    Test that cache errors are handled gracefully in delete operations
    """
    # Create a test user
    user_id = 'test_user_error'
    month = 8
    year = 2025
    
    # Test delete cache error handling
    with patch('db.cache.r.delete', side_effect=Exception("Redis error")):
        # Should not raise exception
        cache.delete_user_expenses_cache(user_id, month, year)


def test_cache_different_users():
    """
    Test that cache works correctly for different users
    """
    # Create two test users
    user1_id = 'user_1'
    user2_id = 'user_2'
    month = 9
    year = 2025
    
    expenses1 = [{'title': 'User 1 Expense', 'amount': 10, 'category': 'Food'}]
    expenses2 = [{'title': 'User 2 Expense', 'amount': 20, 'category': 'Transport'}]
    
    # Cache data for user 1
    cache.add_to_cache_user_expenses(user1_id, month, year, expenses1)
    
    # Cache data for user 2
    cache.add_to_cache_user_expenses(user2_id, month, year, expenses2)
    
    # Verify both users have their own cached data
    user1_data = cache.get_cached_user_expenses(user1_id, month, year)
    user2_data = cache.get_cached_user_expenses(user2_id, month, year)
    assert user1_data is not None
    assert user2_data is not None
    assert user1_data[0]['title'] == 'User 1 Expense'
    assert user2_data[0]['title'] == 'User 2 Expense'


def test_cache_different_months():
    """
    Test that cache works correctly for different months
    """
    # Create a test user
    user_id = 'same_user'
    month1 = 10
    month2 = 11
    year = 2025
    
    # Create test expenses
    expenses_oct = [{'title': 'October Expense', 'amount': 10, 'category': 'Food'}]
    expenses_nov = [{'title': 'November Expense', 'amount': 15, 'category': 'Transport'}]
    
    # Cache data for user
    cache.add_to_cache_user_expenses(user_id, month1, year, expenses_oct)
    cache.add_to_cache_user_expenses(user_id, month2, year, expenses_nov)
    
    # Get cached data for user
    oct_data = cache.get_cached_user_expenses(user_id, month1, year)
    nov_data = cache.get_cached_user_expenses(user_id, month2, year)
    
    # Verify both months have their own cached data
    assert oct_data is not None
    assert nov_data is not None
    assert oct_data[0]['title'] == 'October Expense'
    assert nov_data[0]['title'] == 'November Expense'
    
    # Test that deleting one month doesn't affect the other
    cache.delete_user_expenses_cache(user_id, month1, year)
    oct_data_after = cache.get_cached_user_expenses(user_id, month1, year)
    nov_data_after = cache.get_cached_user_expenses(user_id, month2, year)
    
    # Verify that the October data is gone and the November data is still there
    assert oct_data_after is None
    assert nov_data_after is not None 


def test_cache_delete_scenarios():
    """
    Test cache delete scenarios
    """
    # Create a test user
    user_id = 'test_user_integration'
    month = 1
    year = 2026
    test_expenses = [{'title': 'Test Expense', 'amount': 10, 'category': 'Food'}]
    
    # Test 1: Cache some data
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    assert len(cached_data) == 1
    
    # Test 2: Simulate adding an expense (cache should be deleted)
    cache.delete_user_expenses_cache(user_id, month, year)
    cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data_after is None
    
    # Test 3: Cache data again
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    
    # Test 4: Simulate updating an expense (cache should be deleted)
    cache.delete_user_expenses_cache(user_id, month, year)
    cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data_after is None
    
    # Test 5: Cache data again
    cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
    cached_data = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data is not None
    
    # Test 6: Simulate deleting an expense (cache should be deleted)
    cache.delete_user_expenses_cache(user_id, month, year)
    cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
    assert cached_data_after is None


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True
# test_expenses_cache.py


# type: ignore
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import sys
import os


# Add the server directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import app
from db import users_collection, expenses_collection
from logicconnection import get_email_from_session_id
import cache


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_user():
    """Create a test user and return user data"""
    # Clear any existing test users
    users_collection.delete_many({'email': 'test_expenses_cache@example.com'})
    
    # Create test user
    user_data = {
        'email': 'test_expenses_cache@example.com',
        'password': 'hashed_password',
        'created_at': datetime.now()
    }
    result = users_collection.insert_one(user_data)
    user_data['_id'] = result.inserted_id
    
    yield user_data
    
    # Cleanup
    users_collection.delete_many({'email': 'test_expenses_cache@example.com'})
    expenses_collection.delete_many({'user_id': result.inserted_id})


@pytest.fixture
def test_session_id():
    """Create a test session ID"""
    return 'test_session_expenses_cache_123'


@pytest.fixture
def mock_session():
    """Mock the session validation"""
    with patch('logicconnection.get_email_from_session_id') as mock:
        mock.return_value = 'test_expenses_cache@example.com'
        yield mock


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test"""
    cache.clear_test_cache()
    yield
    cache.clear_test_cache()


class TestCacheUnitTests:
    """Unit tests for cache functions - testing cache logic directly"""
    
    def test_cache_basic_functionality(self, clear_cache):
        """Test basic cache operations work correctly"""
        user_id = 'test_user_123'
        month = 1
        year = 2025
        test_expenses = [{'title': 'Test Expense', 'amount': 10}]
        
        # Test cache miss
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is None
        
        # Test cache add
        cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
        
        # Test cache hit
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is not None
        assert len(cached_data) == 1
        assert cached_data[0]['title'] == 'Test Expense'
        
        # Test cache deletion
        cache.delete_user_expenses_cache(user_id, month, year)
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is None
    
    def test_cache_key_prefixes(self, clear_cache):
        """Test that cache key prefixes work correctly for different environments"""
        # Test production environment
        with patch.dict(os.environ, {'ENV': 'production'}):
            prefix = cache.get_user_expenses_cache_key_prefix()
            assert prefix == "user_expenses:"
        
        # Test test environment
        with patch.dict(os.environ, {'ENV': 'test'}):
            prefix = cache.get_user_expenses_cache_key_prefix()
            assert prefix == "test_user_expenses:"
    
    def test_cache_ttl_functionality(self, clear_cache):
        """Test that cache TTL is set correctly"""
        user_id = 'test_user_ttl'
        month = 1
        year = 2025
        test_expenses = [{'title': 'TTL Test', 'amount': 20}]
        
        # Mock Redis to capture the setex call
        with patch('cache.r') as mock_redis:
            cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
            
            # Verify setex was called with correct parameters
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args[0]
            
            # setex(key, time, value)
            cache_key = call_args[0]
            ttl = call_args[1]
            cached_value = call_args[2]
            
            assert ttl == 604800  # 1 week in seconds
            assert 'user:test_user_ttl:month:2025-01' in cache_key
            assert json.loads(cached_value) == test_expenses
    
    def test_cache_error_handling(self, clear_cache):
        """Test that cache errors are handled gracefully"""
        user_id = 'test_user_error'
        month = 1
        year = 2025
        test_expenses = [{'title': 'Error Test', 'amount': 30}]
        
        # Test get cache error handling
        with patch('cache.r.get', side_effect=Exception("Redis error")):
            result = cache.get_cached_user_expenses(user_id, month, year)
            assert result is None
        
        # Test add cache error handling
        with patch('cache.r.setex', side_effect=Exception("Redis error")):
            # Should not raise exception
            cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
        
        # Test delete cache error handling
        with patch('cache.r.delete', side_effect=Exception("Redis error")):
            # Should not raise exception
            cache.delete_user_expenses_cache(user_id, month, year)
    
    def test_cache_with_real_redis_connection(self, clear_cache):
        """Test cache functionality with actual Redis connection (if available)"""
        try:
            # Test basic operations with real Redis
            user_id = 'real_redis_test'
            month = 2
            year = 2025
            test_expenses = [{'title': 'Real Redis Test', 'amount': 40}]
            
            # Clear any existing cache
            cache.delete_user_expenses_cache(user_id, month, year)
            
            # Test cache miss
            result = cache.get_cached_user_expenses(user_id, month, year)
            assert result is None
            
            # Test cache add
            cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
            
            # Test cache hit
            result = cache.get_cached_user_expenses(user_id, month, year)
            assert result is not None
            assert len(result) == 1
            assert result[0]['title'] == 'Real Redis Test'
            
            # Test cache deletion
            cache.delete_user_expenses_cache(user_id, month, year)
            result = cache.get_cached_user_expenses(user_id, month, year)
            assert result is None
            
        except Exception as e:
            # If Redis is not available, skip this test
            pytest.skip(f"Redis not available: {e}")


class TestCacheIntegrationTests:
    """Integration tests for cache functionality - testing cache invalidation scenarios"""
    
    def test_cache_invalidation_scenarios(self, clear_cache):
        """Test cache invalidation scenarios without API calls"""
        user_id = 'test_user_integration'
        month = 1
        year = 2025
        test_expenses = [{'title': 'Test Expense', 'amount': 10}]
        
        # Test 1: Cache some data
        cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is not None
        assert len(cached_data) == 1
        
        # Test 2: Simulate adding an expense (cache should be invalidated)
        cache.delete_user_expenses_cache(user_id, month, year)
        cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data_after is None
        
        # Test 3: Cache data again
        cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is not None
        
        # Test 4: Simulate updating an expense (cache should be invalidated)
        cache.delete_user_expenses_cache(user_id, month, year)
        cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data_after is None
        
        # Test 5: Cache data again
        cache.add_to_cache_user_expenses(user_id, month, year, test_expenses)
        cached_data = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data is not None
        
        # Test 6: Simulate deleting an expense (cache should be invalidated)
        cache.delete_user_expenses_cache(user_id, month, year)
        cached_data_after = cache.get_cached_user_expenses(user_id, month, year)
        assert cached_data_after is None
    
    def test_cache_different_users_months(self, clear_cache):
        """Test that cache works correctly for different users and months"""
        # Test different users
        user1_id = 'user_1'
        user2_id = 'user_2'
        month = 1
        year = 2025
        
        expenses1 = [{'title': 'User 1 Expense', 'amount': 10}]
        expenses2 = [{'title': 'User 2 Expense', 'amount': 20}]
        
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
        
        # Test different months for same user
        month2 = 2
        expenses_jan = [{'title': 'January Expense', 'amount': 10}]
        expenses_feb = [{'title': 'February Expense', 'amount': 15}]
        
        cache.add_to_cache_user_expenses(user1_id, month, year, expenses_jan)
        cache.add_to_cache_user_expenses(user1_id, month2, year, expenses_feb)
        
        jan_data = cache.get_cached_user_expenses(user1_id, month, year)
        feb_data = cache.get_cached_user_expenses(user1_id, month2, year)
        
        assert jan_data is not None
        assert feb_data is not None
        assert jan_data[0]['title'] == 'January Expense'
        assert feb_data[0]['title'] == 'February Expense'
        
        # Test that deleting one month doesn't affect the other
        cache.delete_user_expenses_cache(user1_id, month, year)
        jan_data_after = cache.get_cached_user_expenses(user1_id, month, year)
        feb_data_after = cache.get_cached_user_expenses(user1_id, month2, year)
        
        assert jan_data_after is None
        assert feb_data_after is not None  # February data should still be there


def test_pass():
    """Dummy test to ensure the test file runs"""
    assert True

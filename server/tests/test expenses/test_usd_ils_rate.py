# test_usd_ils_rate.py


# type: ignore
import pytest
import logicexpenses as le
import requests
from unittest.mock import patch, MagicMock
import cache


@pytest.fixture(autouse=True)
def clear_test_cache():
    """
    Setup function that runs before each test
    Clears test cache to ensure test isolation
    """
    cache.clear_test_cache()


def test_get_usd_to_ils_rate():
    """
    Test that the get_usd_to_ils_rate function returns the correct rate
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Mock the response from the API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'rates': {
            'ILS': 3.7
        }
    }

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == 3.7


def test_get_usd_to_ils_rate_non_200_status_code():
    """
    Test that the get_usd_to_ils_rate function returns None if the API returns a non-200 status code
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Mock the response from the API
    mock_response = MagicMock()
    mock_response.status_code = 500

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_exception():
    """
    Test that the get_usd_to_ils_rate function returns None if the API returns an exception
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Patch the requests.get function to return an exception
    with patch('logicexpenses.requests.get', side_effect=Exception("Network error")):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_invalid_date():
    """
    Test that the get_usd_to_ils_rate function returns None if the date is invalid
    """
    # Test with invalid date format
    rate = le.get_usd_to_ils_rate('invalid-date')
    assert rate == None


def test_get_usd_to_ils_rate_future_date():
    """
    Test that the get_usd_to_ils_rate function returns None for future dates
    """
    # Mock the response for future date
    mock_response = MagicMock()
    mock_response.status_code = 404  # API returns 404 for future dates

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate('2030-01-01')
        assert rate == None


def test_get_usd_to_ils_rate_malformed_json():
    """
    Test that the get_usd_to_ils_rate function returns None if API returns malformed JSON
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Mock the response from the API with malformed JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_missing_ils_key():
    """
    Test that the get_usd_to_ils_rate function returns None if API response is missing ILS key
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Mock the response from the API without ILS key
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'rates': {
            # Missing ILS key
            'EUR': 0.85 
        }
    }

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_missing_rates_key():
    """
    Test that the get_usd_to_ils_rate function returns None if API response is missing rates key
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Mock the response from the API without rates key
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        # Missing rates key
        'error': 'Invalid date'
    }

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_timeout():
    """
    Test that the get_usd_to_ils_rate function returns None if the API times out
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Patch the requests.get function to raise a timeout exception
    with patch('logicexpenses.requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_connection_error():
    """
    Test that the get_usd_to_ils_rate function returns None if there's a connection error
    """
    # Test Date
    test_date = '2025-09-20'
    
    # Patch the requests.get function to raise a connection error
    with patch('logicexpenses.requests.get', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == None


def test_get_usd_to_ils_rate_none_date():
    """
    Test that the get_usd_to_ils_rate function returns None if date is None
    """
    rate = le.get_usd_to_ils_rate(None)
    assert rate == None


def test_get_usd_to_ils_rate_empty_date():
    """
    Test that the get_usd_to_ils_rate function returns None if date is empty string
    """
    rate = le.get_usd_to_ils_rate('')
    assert rate == None


def test_get_usd_to_ils_rate_cache_hit():
    """
    Test that the get_usd_to_ils_rate function returns cached rate when available
    """
    # Test Date
    test_date = '2025-09-20'
    
    # First, cache a rate manually
    test_rate = 3.75
    cache.add_to_cache_currency_rate(test_date, test_rate)
    
    # Now call the function - it should return the cached rate without hitting API
    with patch('logicexpenses.requests.get') as mock_get:
        rate = le.get_usd_to_ils_rate(test_date)
        
        # Should return cached rate
        assert rate == test_rate
        
        # Should NOT have called the API
        mock_get.assert_not_called()


def test_get_usd_to_ils_rate_cache_miss_then_cache():
    """
    Test that the get_usd_to_ils_rate function calls API when cache miss, then caches result
    """
    # Test Date
    test_date = '2025-09-21'
    
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'rates': {
            'ILS': 3.8
        }
    }
    
    with patch('logicexpenses.requests.get', return_value=mock_response):
        # First call should hit API and cache result
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate == 3.8
        
        # Verify it was cached
        cached_rate = cache.get_cached_currency_rate(test_date)
        assert cached_rate == 3.8


def test_get_usd_to_ils_rate_cache_miss_api_failure():
    """
    Test that the get_usd_to_ils_rate function handles API failure when cache miss
    """
    # Test Date
    test_date = '2025-09-22'
    
    # Mock API failure
    with patch('logicexpenses.requests.get', side_effect=Exception("API Error")):
        rate = le.get_usd_to_ils_rate(test_date)
        assert rate is None
        
        # Verify nothing was cached
        cached_rate = cache.get_cached_currency_rate(test_date)
        assert cached_rate is None


def test_get_usd_to_ils_rate_cache_error_fallback():
    """
    Test that the get_usd_to_ils_rate function falls back to API when cache has errors
    """
    # Test Date
    test_date = '2025-09-23'
    
    # Mock cache error by patching the cache function to return None (simulating cache error)
    with patch('cache.get_cached_currency_rate', return_value=None):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {
                'ILS': 3.9
            }
        }
        
        # Patch the requests.get function to return the mock response
        with patch('logicexpenses.requests.get', return_value=mock_response):
            rate = le.get_usd_to_ils_rate(test_date)
            assert rate == 3.9


def test_get_usd_to_ils_rate_cache_store_error():
    """
    Test that the get_usd_to_ils_rate function continues working even if cache store fails
    """    
    # Test Date
    test_date = '2025-09-24'
    
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'rates': {
            'ILS': 4.0
        }
    }
    
    # Mock cache store error
    with patch('cache.add_to_cache_currency_rate', side_effect=Exception("Cache Store Error")):
        # Patch the requests.get function to return the mock response
        with patch('logicexpenses.requests.get', return_value=mock_response):
            rate = le.get_usd_to_ils_rate(test_date)
            # Should still return the rate even if caching failed
            assert rate == 4.0


def test_add_to_cache_currency_rate_function():
    """
    Test the add_to_cache_currency_rate function directly
    """    
    # Test Date and Rate
    test_date = '2025-09-25'
    test_rate = 3.85
    
    # Cache the rate
    cache.add_to_cache_currency_rate(test_date, test_rate)
    
    # Verify it was stored
    cached_rate = cache.get_cached_currency_rate(test_date)
    assert cached_rate == test_rate


def test_get_cached_currency_rate_function():
    """
    Test the get_cached_currency_rate function directly
    """
    # Test Date and Rate
    test_date = '2025-09-26'
    test_rate = 3.9
    
    # Test cache miss
    cached_rate = cache.get_cached_currency_rate(test_date)
    assert cached_rate is None
    
    # Store rate and test cache hit
    cache.add_to_cache_currency_rate(test_date, test_rate)
    cached_rate = cache.get_cached_currency_rate(test_date)
    assert cached_rate == test_rate


def test_cache_different_dates():
    """
    Test that different dates are cached separately
    """   
    # Test Dates and Rates
    date1 = '2025-09-27'
    date2 = '2025-09-28'
    rate1 = 3.7
    rate2 = 3.8
    
    # Cache different rates for different dates
    cache.add_to_cache_currency_rate(date1, rate1)
    cache.add_to_cache_currency_rate(date2, rate2)
    
    # Verify they are stored separately
    assert cache.get_cached_currency_rate(date1) == rate1
    assert cache.get_cached_currency_rate(date2) == rate2
    
    # Verify they don't interfere with each other
    assert cache.get_cached_currency_rate(date1) != rate2
    assert cache.get_cached_currency_rate(date2) != rate1


def test_cache_roundtrip():
    """
    Test complete cache roundtrip: cache miss -> API call -> cache store -> cache hit
    """   
    # Test Date
    test_date = '2025-09-29'
    
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'rates': {
            'ILS': 3.95
        }
    }
    
    # First call - should hit API and cache
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate1 = le.get_usd_to_ils_rate(test_date)
        assert rate1 == 3.95
        
        # Verify rate was cached
        cached_rate = cache.get_cached_currency_rate(test_date)
        assert cached_rate == 3.95
    
    # Second call with same date - should hit cache (no API call)
    with patch('logicexpenses.requests.get') as mock_get_second:
        rate2 = le.get_usd_to_ils_rate(test_date)
        assert rate2 == 3.95
        
        # Should not have called API again
        mock_get_second.assert_not_called()


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True


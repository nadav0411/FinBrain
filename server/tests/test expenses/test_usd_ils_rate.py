# test_usd_ils_rate.py


import logicexpenses as le
import requests
from unittest.mock import patch, MagicMock


def test_get_usd_to_ils_rate():
    """
    Test that the get_usd_to_ils_rate function returns the correct rate
    """
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
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == 3.7


def test_get_usd_to_ils_rate_non_200_status_code():
    """
    Test that the get_usd_to_ils_rate function returns None if the API returns a non-200 status code
    """
    # Mock the response from the API
    mock_response = MagicMock()
    mock_response.status_code = 500

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == None


def test_get_usd_to_ils_rate_exception():
    """
    Test that the get_usd_to_ils_rate function returns None if the API returns an exception
    """
    # Patch the requests.get function to return an exception
    with patch('logicexpenses.requests.get', side_effect=Exception("Network error")):
        rate = le.get_usd_to_ils_rate('2025-09-20')
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
    # Mock the response from the API with malformed JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == None


def test_get_usd_to_ils_rate_missing_ils_key():
    """
    Test that the get_usd_to_ils_rate function returns None if API response is missing ILS key
    """
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
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == None


def test_get_usd_to_ils_rate_missing_rates_key():
    """
    Test that the get_usd_to_ils_rate function returns None if API response is missing rates key
    """
    # Mock the response from the API without rates key
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        # Missing rates key
        'error': 'Invalid date'
    }

    # Patch the requests.get function to return the mock response
    with patch('logicexpenses.requests.get', return_value=mock_response):
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == None


def test_get_usd_to_ils_rate_timeout():
    """
    Test that the get_usd_to_ils_rate function returns None if the API times out
    """
    # Patch the requests.get function to raise a timeout exception
    with patch('logicexpenses.requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
        rate = le.get_usd_to_ils_rate('2025-09-20')
        assert rate == None


def test_get_usd_to_ils_rate_connection_error():
    """
    Test that the get_usd_to_ils_rate function returns None if there's a connection error
    """
    # Patch the requests.get function to raise a connection error
    with patch('logicexpenses.requests.get', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        rate = le.get_usd_to_ils_rate('2025-09-20')
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




    




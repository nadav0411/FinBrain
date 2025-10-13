# FinBrain Project - cache.py - MIT License (c) 2025 Nadav Eshed


# type: ignore
import os
import redis
from dotenv import load_dotenv
import logging
import json


# Create a logger for this module
logger = logging.getLogger(__name__)

# Load environment variables from config file
env = os.getenv('ENV', 'development')
if env == 'test':
    load_dotenv('configs/.env.test')
else:
    load_dotenv('configs/.env.development')

# Get the Redis URL from environment or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Use test-specific key prefix to avoid conflicts with production data
def get_cache_key_prefix():
    """Get cache key prefix based on environment"""
    if os.getenv("ENV") == "test":
        return "test_usd_ils_rate:"
    else:
        return "usd_ils_rate:"

# Connect to Redis (decode_responses=True means we get strings instead of bytes)
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    # Test the connection
    r.ping()
    logger.info(f"Connected to Redis | redis_url={REDIS_URL}")
except Exception as e:
    logger.error(f"Failed to connect to Redis | redis_url={REDIS_URL} | error={str(e)}")
    raise


def get_cached_currency_rate(date_str):
    """
    Get cached USD to ILS rate for a given date
    Returns the rate if found in cache, None otherwise
    """
    try:
        # Get the cache key with our test currency rate prefix
        cache_key = f"{get_cache_key_prefix()}{date_str}"

        # Get the cached rate if it exists (None if not found)
        cached_rate = r.get(cache_key)
        if cached_rate:
            logger.info(f"Currency rate found in cache | date={date_str} | rate={cached_rate}")
            return float(cached_rate)
        return None
    except Exception as e:
        logger.error(f"Error getting cached currency rate | date={date_str} | error={str(e)}")
        return None


def add_to_cache_currency_rate(date_str, rate):
    """
    Add USD to ILS rate for a given date to the cache
    """
    try:
        # Get the cache key with our test currency rate prefix
        cache_key = f"{get_cache_key_prefix()}{date_str}"
        # Add the rate to the cache
        r.set(cache_key, str(rate))
        logger.info(f"Currency rate added to cache | date={date_str} | rate={rate}")
    except Exception as e:
        logger.error(f"Error adding currency rate to cache | date={date_str} | rate={rate} | error={str(e)}")


def get_cached_user_expenses(email, month, year):
    """
    Get cached user expenses for a specific month and year
    Returns the expenses if found in cache, None otherwise
    """
    try:
        # Get the cache key with user expenses prefix
        cache_key = f"{get_user_expenses_cache_key_prefix()}user:{str(email).strip().lower()}:month:{year}-{month:02d}"
        
        # Get the cached expenses if they exist (None if not found)
        cached_expenses = r.get(cache_key)
        if cached_expenses:
            logger.info(f"User expenses found in cache | email={str(email)} | month={month} | year={year}")
            return json.loads(cached_expenses)
        return None
    except Exception as e:
        logger.error(f"Error getting cached user expenses | email={str(email)} | month={month} | year={year} | error={str(e)}")
        return None


def add_to_cache_user_expenses(email, month, year, expenses):
    """
    Add user expenses for a specific month and year to the cache
    TTL is set to 1 week (604800 seconds)
    """
    try:
        # Get the cache key with user expenses prefix
        cache_key = f"{get_user_expenses_cache_key_prefix()}user:{str(email).strip().lower()}:month:{year}-{month:02d}"
        
        # Add the expenses to the cache with TTL of 1 week (604800 seconds)
        r.setex(cache_key, 604800, json.dumps(expenses))
        logger.info(f"User expenses added to cache | email={str(email)} | month={month} | year={year} | expense_count={len(expenses)}")
    except Exception as e:
        logger.error(f"Error adding user expenses to cache | email={str(email)} | month={month} | year={year} | error={str(e)}")


def delete_user_expenses_cache(email, month, year):
    """
    Delete cached user expenses for a specific month and year
    """
    try:
        # Get the cache key with user expenses prefix
        cache_key = f"{get_user_expenses_cache_key_prefix()}user:{str(email).strip().lower()}:month:{year}-{month:02d}"
        
        # Delete the cached expenses
        result = r.delete(cache_key)
        if result:
            logger.info(f"User expenses cache invalidated | email={str(email)} | month={month} | year={year}")
        else:
            logger.info(f"No cache found to invalidate | email={str(email)} | month={month} | year={year}")
    except Exception as e:
        logger.error(f"Error invalidating user expenses cache | email={str(email)} | month={month} | year={year} | error={str(e)}")


def get_user_expenses_cache_key_prefix():
    """Get cache key prefix for user expenses based on environment"""
    if os.getenv("ENV") == "test":
        return "test_user_expenses:"
    else:
        return "user_expenses:"


def clear_test_cache():
    """
    Clear all test cache data - ONLY use in test environment
    """
    # Check if the environment is test
    if os.getenv("ENV") != "test":
        logger.warning("clear_test_cache called in non-test environment - ignoring")
        return
    
    try:
        # Clear all keys with our test prefixes
        currency_keys = r.keys("test_usd_ils_rate:*")
        expense_keys = r.keys("test_user_expenses:*")
        all_keys = currency_keys + expense_keys
        
        if all_keys:
            r.delete(*all_keys)
            logger.info(f"Test cache cleared | keys_cleared={len(all_keys)}")
    except Exception as e:
        logger.error(f"Error clearing test cache | error={str(e)}")


def delete_all_user_expenses_cache(email):
    """
    Delete all cached user expenses for the given user across all months/years
    """
    try:
        key_prefix = get_user_expenses_cache_key_prefix()
        # Keys are in format: {prefix}user:{email}:month:YYYY-MM
        pattern = f"{key_prefix}user:{str(email).strip().lower()}:month:*"
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
            logger.info(f"All user expenses cache invalidated | email={str(email)} | keys_cleared={len(keys)}")
        else:
            logger.info(f"No user expenses cache found to invalidate | email={str(email)}")
    except Exception as e:
        logger.error(f"Error invalidating all user expenses cache | email={str(email)} | error={str(e)}")
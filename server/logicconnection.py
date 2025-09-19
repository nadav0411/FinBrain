# logicconnection.py

import logging
from typing import Mapping
from db import users_collection
from flask import jsonify
from datetime import datetime, timezone
import re
import uuid
from pymongo.errors import DuplicateKeyError
from cache import r


# Session expiry in seconds (logout from the client after 1.5 minutes of inactivity / heartbeat)
SESSION_TTL_SECONDS = 90

# Create a logger for this module
logger = logging.getLogger(__name__)


def get_now_utc():
    """
    Get the current UTC time
    """
    return datetime.now(timezone.utc)


def is_session_expired(session_id):
    """
    Check if the session is expired by checking if it exists in Redis
    """
    session_data = r.hgetall(f"session:{session_id}")
    return not session_data


def handle_signup(data):
    """
    Signup function
    This function is called when the user wants to signup for an account
    It checks if all the required fields are present and does validation for the fields,
    then creates the user in the database
    """
    required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']

    # Normalize and trim inputs
    first_name = (data.get('firstName') or '').strip()
    last_name = (data.get('lastName') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirmPassword') or ''

    # Check if all required fields are present
    normalized = {
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'password': password,
        'confirmPassword': confirm_password,
    }
    for field in required_fields:
        if not normalized.get(field):
            return jsonify({'message': f'Missing field {field}'}), 400

    # Check email format and length
    email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if not email_regex.match(email) or len(email) > 254:
        return jsonify({'message': 'Invalid email'}), 400

    # Check names validation
    name_regex = re.compile(r"^[A-Za-z\s\-']+$")
    if not name_regex.match(first_name) or not name_regex.match(last_name):
        return jsonify({'message': 'Invalid name'}), 400
    if len(first_name) > 40 or len(last_name) > 40:
        return jsonify({'message': 'First name and last name must be 40 characters or less'}), 400

    # Password checks
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    # Check if the email is already in use
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    # Create the user
    try:
        users_collection.insert_one({
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password,
        })
    # If there is any error, return an error message
    except DuplicateKeyError:
        return jsonify({'message': 'Email already in use'}), 409
    except Exception:
        logger.exception("Signup failed unexpectedly", extra={"email": email})
        return jsonify({'message': 'Signup failed'}), 500

    logger.info("Signup successful", extra={"email": email})
    return jsonify({'message': 'Signup successful'}), 201


def handle_login(data):
    """
    Login function
    This function is called when the user wants to log in to their account
    It checks if the email and password are present and if the user exists
    It then checks if the password is correct
    If everything is correct, it returns a success message
    """
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    # Check if the email and password are present
    if not email or not password:
        logger.warning("Login missing fields", extra={"email": email, "password_provided": bool(password)})
        return jsonify({'message': 'Email and password are required'}), 400
    
    # Email checks (format and max length)
    email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if len(email) > 254 or not email_regex.match(email):
        logger.warning("Invalid login credentials", extra={"email": email})
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Fetch user and validate credentials
    try:
        user = users_collection.find_one({'email': email})
    except Exception:
        logger.exception("Login DB error", extra={"email": email})
        return jsonify({'message': 'Login failed'}), 500

    stored_password = (user or {}).get('password')
    if not stored_password or stored_password != password:
        # Use a single generic message to avoid account enumeration
        logger.warning("Invalid login credentials", extra={"email": email})
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create a session ID and store it in the dictionary
    session_id = str(uuid.uuid4())
    r.hset(f"session:{session_id}", mapping={"email": email, 
    "last_seen": get_now_utc().isoformat()})
    r.expire(f"session:{session_id}", SESSION_TTL_SECONDS)

    # Only include the first name in the response
    first_name = (user or {}).get('firstName') or ''

    logger.info("Login successful", extra={"email": email, "session_id": session_id, "first_name": first_name})
    return jsonify({'message': 'Login successful', 'session_id': session_id, 'name': first_name}), 200


def get_email_from_session_id(session_id):
    """
    Get the email from the session ID
    This function is called when the user wants to get their email from the session ID
    It returns the email from Redis
    """
    # Treat None, empty, or string forms of "null" values as missing
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        logger.debug("Session ID not found", extra={"session_id": session_id})
        return None
    
    # Get session data from Redis
    session_data = r.hgetall(f"session:{session_id}")
    if not session_data:
        return None

    # Get the email from the session data
    email = session_data.get("email")
    if not email:
        return None

    # Update the last seen timestamp
    r.hset(f"session:{session_id}", "last_seen", get_now_utc().isoformat())
    r.expire(f"session:{session_id}", SESSION_TTL_SECONDS)
    return email


def handle_logout(session_id):
    """
    Logout function
    This function is called when the user wants to logout from their account
    It removes the session ID from the dictionary
    """
    # Treat None, empty, or string forms of "null" values as missing
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Missing session_id'}), 400
    
    # Remove the session if it exists
    r.delete(f"session:{session_id}")

    # Return success regardless of whether it existed
    logger.info("Logout", extra={"session_id": session_id})
    return jsonify({'message': 'Logout successful'}), 200


def handle_heartbeat(session_id):
    """
    Update session last_seen timestamp to keep it alive.
    """
    # Check if the session ID is present (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        logger.info("Heartbeat for unknown session", extra={"session_id": session_id})
        return jsonify({'message': 'Missing session_id'}), 400
    
    # Get session data from Redis
    session_data = r.hgetall(f"session:{session_id}")
    if not session_data:
        logger.info("Heartbeat for non-existent session", extra={"session_id": session_id})
        return jsonify({'message': 'No such session', 'active': False}), 200

    # Update the last seen timestamp
    r.hset(f"session:{session_id}", "last_seen", get_now_utc().isoformat())
    r.expire(f"session:{session_id}", SESSION_TTL_SECONDS)

    logger.debug("Heartbeat ok", extra={"session_id": session_id})
    return jsonify({'message': 'Heartbeat ok', 'active': True, 'ttl_seconds': SESSION_TTL_SECONDS}), 200

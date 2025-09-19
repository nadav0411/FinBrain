# logicconnection.py

import logging
from db import users_collection
from flask import jsonify
from datetime import datetime, timedelta, timezone
from threading import Thread, Event
import re
import uuid
from pymongo.errors import DuplicateKeyError


# This is a dictionary that will store the connected sessions
# The key is the session ID and the value is the user's email
connected_sessions = {}

# Track last activity per session for expiry handling
last_seen_sessions = {}

# Session expiry in minutes (logout from the client after 1.5 minutes of inactivity / heartbeat)
SESSION_TTL_MINUTES = 1.5

# Sweep interval in seconds (check the dictionary for expired sessions every 60 seconds)
SWEEP_INTERVAL_SECONDS = 60

# This is used to stop the sweeper
sweeper_stop_event = Event()

# Create a logger for this module
logger = logging.getLogger(__name__)


def get_now_utc():
    """
    Get the current UTC time
    """
    return datetime.now(timezone.utc)


def is_session_expired(session_id):
    """
    Check if the session is expired
    """
    last_seen = last_seen_sessions.get(session_id)
    if last_seen is None:
        return False 
    return get_now_utc() - last_seen >= timedelta(minutes=SESSION_TTL_MINUTES)


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
        logger.warning("Login missing fields")
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
    connected_sessions[session_id] = email
    last_seen_sessions[session_id] = get_now_utc()

    # Only include the first name in the response
    first_name = (user or {}).get('firstName') or ''

    logger.info("Login successful", extra={"email": email, "session_id": session_id, "first_name": first_name})
    return jsonify({'message': 'Login successful', 'session_id': session_id, 'name': first_name}), 200


def get_email_from_session_id(session_id):
    """
    Get the email from the session ID
    This function is called when the user wants to get their email from the session ID
    It returns the email from the dictionary
    """
    # Treat None, empty, or string forms of "null" values as missing
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        logger.debug("Session ID not found", extra={"session_id": session_id})
        return None
    
    # Get current time once to avoid timing issues
    now = get_now_utc()
    
    # Check expiry of the session using the same timestamp
    last_seen = last_seen_sessions.get(session_id)
    if last_seen is not None and now - last_seen >= timedelta(minutes=SESSION_TTL_MINUTES):
        connected_sessions.pop(session_id, None)
        last_seen_sessions.pop(session_id, None)
        logger.info("Session expired on access", extra={"session_id": session_id})
        return None
    
    email = connected_sessions.get(session_id)
    # Update last seen on the authenticated user
    if email:
        last_seen_sessions[session_id] = now
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
    
    # Remove the session if it exists (no error if it doesn't)
    removed = connected_sessions.pop(session_id, None)
    last_seen_sessions.pop(session_id, None)

    # Return success regardless of whether it existed
    logger.info("Logout", extra={"session_id": session_id, "revoked": bool(removed)})
    return jsonify({'message': 'Logout successful', 'revoked': bool(removed)}), 200


def handle_heartbeat(session_id):
    """
    Update session last_seen timestamp to keep it alive.
    """
    # Check if the session ID is present (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        logger.info("Heartbeat for unknown session", extra={"session_id": session_id})
        return jsonify({'message': 'Missing session_id'}), 400
    # Check if the session ID is in the dictionary
    if session_id not in connected_sessions:
        logger.info("Heartbeat for non-existent session", extra={"session_id": session_id})
        return jsonify({'message': 'No such session', 'active': False}), 200
    # Check if the session is expired
    if is_session_expired(session_id):
        logger.info("Heartbeat expired session", extra={"session_id": session_id})
        connected_sessions.pop(session_id, None)
        last_seen_sessions.pop(session_id, None)
        return jsonify({'message': 'Session expired', 'active': False}), 200
    # Update the last seen timestamp
    last_seen_sessions[session_id] = get_now_utc()

    logger.debug("Heartbeat ok", extra={"session_id": session_id})
    return jsonify({'message': 'Heartbeat ok', 'active': True, 'ttl_minutes': SESSION_TTL_MINUTES}), 200


def sweep_expired_sessions_loop():
    """
    Background loop to remove expired sessions periodically.
    This function is called when the user wants to sweep the expired sessions
    It removes the expired sessions from the dictionary
    """
    while not sweeper_stop_event.is_set():
        # Get the current time
        now = get_now_utc()
        # Handle the expired session loop
        handle_expired_session_loop(now)

        # Wait for the next sweep
        sweeper_stop_event.wait(SWEEP_INTERVAL_SECONDS)
        logger.debug("Sweeper tick", extra={
        "time": now.strftime("%H:%M:%S"),
        "connected_count": len(connected_sessions),
        "last_seen_count": len(last_seen_sessions),
        })


def handle_expired_session_loop(now):
    """
    Handle expired session loop
    This function is called when the server wants to handle the expired session loop
    It removes the expired sessions from the dictionary
    """
    try:
        for session_id, last_seen in list(last_seen_sessions.items()):
            # Check if the session is expired
            if now - last_seen >= timedelta(minutes=SESSION_TTL_MINUTES):
                # Remove the session from the dictionary (if expired)
                connected_sessions.pop(session_id, None)
                last_seen_sessions.pop(session_id, None)
    except Exception:
        logger.exception("Error in handle_expired_session_loop")


def start_session_sweeper():
    """
    Start the session sweeper
    This function is called when the server wants to start the session sweeper
    It starts the thread that will check the dictionary for expired sessions every 60 seconds
    """
    thread = Thread(target=sweep_expired_sessions_loop, name="session-sweeper", daemon=True)
    thread.start()
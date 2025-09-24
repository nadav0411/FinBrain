# logicconnection.py


import logging
from db import users_collection
from flask import jsonify
from datetime import datetime, timezone
import re
import uuid
from pymongo.errors import DuplicateKeyError
from cache import r
from password_hashing import hash_password, verify_password


# Session expiry in seconds (1.5 minutes of inactivity)
SESSION_TTL_SECONDS = 90

# Create a logger for this module
logger = logging.getLogger(__name__)


def get_now_utc():
    """
    Get current UTC timestamp
    """
    return datetime.now(timezone.utc)


def validate_session_id(session_id):
    """
    Validate and normalize session ID, handling null/empty values
    """
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return None
    return str(session_id).strip()


def is_session_expired(session_id):
    """
    Check if session exists in Redis (not expired)
    """
    try:
        session_data = r.hgetall(f"session:{session_id}")
        return not session_data
    except Exception:
        logger.exception(f"Redis error in is_session_expired | session_id={session_id}")
        return True 


def handle_signup(data):
    """
    Process user signup with validation and database storage
    """
    required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']

    # Extract and normalize input data
    first_name = (data.get('firstName') or '').strip()
    last_name = (data.get('lastName') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirmPassword') or ''

    # Validate required fields
    user_data = {
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'password': password,
        'confirmPassword': confirm_password,
    }
    for field in required_fields:
        if not user_data.get(field):
            return jsonify({'message': f'Missing field {field}'}), 400

    # Validate email format and length
    email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if not email_regex.match(email) or len(email) > 254:
        return jsonify({'message': 'Invalid email'}), 400

    # Validate name format and length
    name_regex = re.compile(r"^[A-Za-z\s\-']+$")
    if not name_regex.match(first_name) or not name_regex.match(last_name):
        return jsonify({'message': 'Invalid name'}), 400
    if len(first_name) > 40 or len(last_name) > 40:
        return jsonify({'message': 'First name and last name must be 40 characters or less'}), 400

    # Validate password confirmation
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    # Check for existing email
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    # Create user account
    try:
        # Hash the password before storing
        hashed_password = hash_password(password)
        users_collection.insert_one({
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': hashed_password,
        })
    except DuplicateKeyError:
        return jsonify({'message': 'Email already in use'}), 409
    except Exception:
        logger.exception(f"Signup failed unexpectedly | email={email}")
        return jsonify({'message': 'Signup failed'}), 500

    logger.info(f"Signup successful | email={email}")
    return jsonify({'message': 'Signup successful'}), 201


def handle_login(data):
    """
    Process user login with authentication and session creation
    """
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    demo = data.get('demo')

    # Treat demo user specially: allow email=="demo" and password is empty and demo flag is True
    is_demo_user = email == 'demo' and password == '' and demo is True

    if not is_demo_user:
        # Validate required fields
        if not email or not password:
            logger.warning(f"Login missing fields | email={email} | password_provided={bool(password)}")
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        if len(email) > 254 or not email_regex.match(email):
            logger.warning(f"Invalid login credentials | email={email}")
            return jsonify({'message': 'Invalid credentials'}), 401
    
    # Authenticate user
    try:
        user = users_collection.find_one({'email': email})
    except Exception:
        logger.exception(f"Login DB error | email={email}")
        return jsonify({'message': 'Login failed'}), 500

    # For demo user, auto-provision if missing and bypass email format
    if is_demo_user and not user:
        try:
            users_collection.insert_one({
                'firstName': 'Guest',
                'lastName': 'Demo',
                'email': 'demo',
                'password': hash_password('')
            })
            user = users_collection.find_one({'email': 'demo'})
        except Exception:
            logger.exception(f"Demo user auto-provision failed | email={email}")
            return jsonify({'message': 'Login failed'}), 500

    # Check password
    stored_password = (user or {}).get('password')
    if not is_demo_user:
        if not stored_password or not verify_password(password, stored_password):
            logger.warning(f"Invalid login credentials | email={email}")
            return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create session
    session_id = str(uuid.uuid4())
    try:
        r.hset(f"session:{session_id}", mapping={"email": email, 
        "last_seen": get_now_utc().isoformat()})
        r.expire(f"session:{session_id}", SESSION_TTL_SECONDS)
    except Exception:
        logger.exception(f"Redis error during login | email={email} | session_id={session_id}")
        return jsonify({'message': 'Login failed'}), 500

    # Extract user name for response
    first_name = (user or {}).get('firstName') or ''

    logger.info(f"Login successful | email={email} | session_id={session_id} | first_name={first_name}")
    return jsonify({'message': 'Login successful', 'session_id': session_id, 'name': first_name}), 200


def get_email_from_session_id(session_id):
    """
    Retrieve user email from session ID and update session timestamp
    """
    validated_session_id = validate_session_id(session_id)
    if not validated_session_id:
        logger.debug(f"Session ID not found | session_id={session_id}")
        return None
    
    try:
        # Get session data
        session_data = r.hgetall(f"session:{validated_session_id}")
        if not session_data:
            return None

        # Get the email from the session data
        email = session_data.get("email")
        if not email:
            return None

        # Update session timestamp
        r.hset(f"session:{validated_session_id}", "last_seen", get_now_utc().isoformat())
        r.expire(f"session:{validated_session_id}", SESSION_TTL_SECONDS)
        return email
    except Exception:
        logger.exception(f"Redis error in get_email_from_session_id | session_id={validated_session_id}")
        return None


def handle_logout(session_id):
    """
    Process user logout by removing session from Redis
    """
    validated_session_id = validate_session_id(session_id)
    if not validated_session_id:
        return jsonify({'message': 'Missing session_id'}), 400
    
    # Remove session from Redis
    try:
        r.delete(f"session:{validated_session_id}")
    except Exception:
        logger.exception(f"Redis error during logout | session_id={validated_session_id}")

    logger.info(f"Logout | session_id={validated_session_id}")
    return jsonify({'message': 'Logout successful'}), 200


def handle_heartbeat(session_id):
    """
    Update session timestamp to keep it alive
    """
    validated_session_id = validate_session_id(session_id)
    if not validated_session_id:
        logger.info(f"Heartbeat for unknown session | session_id={session_id}")
        return jsonify({'message': 'Missing session_id'}), 400
    
    # Get session data from Redis
    try:
        session_data = r.hgetall(f"session:{validated_session_id}")
        if not session_data:
            logger.info(f"Heartbeat for non-existent session | session_id={validated_session_id}")
            return jsonify({'message': 'No such session', 'active': False}), 200

        # Update session timestamp
        r.hset(f"session:{validated_session_id}", "last_seen", get_now_utc().isoformat())
        r.expire(f"session:{validated_session_id}", SESSION_TTL_SECONDS)

        logger.debug(f"Heartbeat ok | session_id={validated_session_id}")
        return jsonify({'message': 'Heartbeat ok', 'active': True, 'ttl_seconds': SESSION_TTL_SECONDS}), 200
    except Exception:
        logger.exception(f"Redis error during heartbeat | session_id={validated_session_id}")
        return jsonify({'message': 'Heartbeat failed', 'active': False}), 500

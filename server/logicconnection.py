from db import users_collection
from flask import jsonify
import re
import uuid


# This is a dictionary that will store the connected sessions
# The key is the session ID and the value is the user's email
connected_sessions = {}


def handle_signup(data):
    """
    Signup function
    This function is called when the user wants to signup for an account
    It checks if all the required fields are present and if the name is valid,
    the passwords match and if the email is already in use
    It then creates the user in the database
    """
    required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']

    # Check if all required fields are present
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Missing field {field}'}), 400
    
    # Check if the name is valid
    name_regex = re.compile(r'^[A-Za-z\s]*$')
    if not name_regex.match(data['firstName']) or not name_regex.match(data['lastName']):
        return jsonify({'message': 'Invalid name'}), 400
    
    # Check if the name length is within limits (40 characters max)
    if len(data['firstName']) > 40 or len(data['lastName']) > 40:
        return jsonify({'message': 'First name and last name must be 40 characters or less'}), 400
    
    # Check if the passwords match
    if data.get('password') != data.get('confirmPassword'):
        return jsonify({'message': 'Passwords do not match'}), 400
    
    # Check if the email is already in use
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already in use'}), 400
    
    # Create the user
    users_collection.insert_one({
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'email': data['email'],
        'password': data['password'],
        'expenses': [],
        'incomes': []
    })
    
    return jsonify({'message': 'Signup successful'}), 201


def handle_login(data):
    """
    Login function
    This function is called when the user wants to login to their account
    It checks if the email and password are present and if the user exists
    It then checks if the password is correct
    If everything is correct, it returns a success message
    """
    email = data.get('email')
    password = data.get('password')

    # Check if the email and password are present
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    # Check if the user exists
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Check if the password is correct
    if user['password'] != password:
        return jsonify({'message': 'Incorrect password'}), 401
    
    # Create a session ID and store it in the dictionary
    session_id = str(uuid.uuid4())
    connected_sessions[session_id] = email

    # Get the name of the user
    name = f"{user['firstName']}"

    return jsonify({'message': 'Login successful', 'session_id': session_id, 'name': name}), 200


def get_email_from_session_id(session_id):
    """
    Get the email from the session ID
    This function is called when the user wants to get their email from the session ID
    It returns the email from the dictionary
    """
    return connected_sessions.get(session_id)

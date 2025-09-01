from db import users_collection
from flask import jsonify
import re


def handle_signup(data):
    required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']

    # Check if all required fields are present
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Missing field {field}'}), 400
    
    # Check if the name is valid
    name_regex = re.compile(r'^[A-Za-z\s]*$')
    if not name_regex.match(data['firstName']) or not name_regex.match(data['lastName']):
        return jsonify({'message': 'Invalid name'}), 400
    
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
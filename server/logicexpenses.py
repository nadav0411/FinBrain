from flask import jsonify
from db import users_collection
from logicconnection import get_email_from_session_id
from datetime import datetime
import requests
import re


def get_usd_to_ils_rate(date_str):
    """ 
    Get the USD to ILS rate for a given date
    This function is called when the user wants to add an expense
    It returns the USD to ILS rate for the given date
    """
    url = f"https://api.frankfurter.app/{date_str}?from=USD&to=ILS"
    try:
        # Wait for the API to respond
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return(data['rates']['ILS'])
        else:
            print("API returned non-200 status:", response.status_code)
    # If the API returns an error, return a default rate
    except Exception as e:
        print("Error calling exchange rate API:", e)
    return 3.4 


def handle_add_expense(data, session_id):
    # Get the email from the session ID
    email = get_email_from_session_id(session_id)
    if not email:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Get the required fields
    title = data.get('title')
    date = data.get('date')
    amount = data.get('amount')
    currency = data.get('currency')
    if not title or not date or not amount or not currency:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if the title is valid
    title_regex = re.compile(r'^[A-Za-z\s]*$')
    if not title_regex.match(title):
        return jsonify({'message': 'Invalid title'}), 400
    
    # Check valid amount
    try:
        amount = float(amount)
        if amount < 0:
            return jsonify({'message': 'Amount must be greater than 0'}), 400
    except ValueError:
        return jsonify({'message': 'Amount must be a number'}), 400
    
    # Check valid date
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        if date > datetime.now().date() or date < datetime(2015, 1, 1).date():
            return jsonify({'message': 'Date cannot be in the future or before 2015'}), 400
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    
    # Check valid currencies and convert
    usd_to_ils_rate = get_usd_to_ils_rate(date)
    if currency == 'USD':
        amount_usd = amount
        amount_ils = amount * usd_to_ils_rate
    elif currency == 'ILS':
        amount_ils = amount
        amount_usd = amount / usd_to_ils_rate
    else:
        return jsonify({'message': 'Invalid currency'}), 400
    
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Create the expense item
    serial_number = len(user['expenses']) + 1
    expense_item = {
        "title": title,
        "date": date.isoformat(),
        "amount_usd": amount_usd,
        "amount_ils": amount_ils,
        "category": "",
        "serial_number": serial_number
    }
    users_collection.update_one({'email': email}, {'$push': {'expenses': expense_item}})

    return jsonify({'message': 'Expense added'}), 200
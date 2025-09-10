from flask import jsonify
from db import users_collection, expenses_collection
from logicconnection import get_email_from_session_id
from datetime import datetime
import requests
import re
from predictmodelloader import model, vectorizer



def classify_expense(text):
    """
    This function gets a sentence (like 'Bought medicine')
    and returns the best category (like 'health')
    """
    # First, make sure the input is a string and is not empty
    if not text or not isinstance(text, str):
        return "other"  # If the text is bad, we return 'other' by default

    # Use the saved vectorizer to turn the text into a number vector
    vector = vectorizer.transform([text])

    # Now we use the trained model to predict the category
    prediction = model.predict(vector)

    # Return the predicted category (it's a list with one value)
    return prediction[0]


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
    """
    This function is called when the user wants to add an expense to their account
    It checks if the required fields are present and if the title is valid
    It then checks if the amount is valid and if the date is valid
    It then checks if the currency is valid and if the expense is valid
    It then adds the expense to the database
    """
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
    title_regex = re.compile(r'^[A-Za-z0-9\s]*$')
    if not title_regex.match(title):
        return jsonify({'message': 'Invalid title'}), 400
    
    # Check if the title is <= 60 characters
    if len(title) > 60:
        return jsonify({'message': 'Title must be less than 60 characters'}), 400
    
    # Check valid amount
    try:
        amount = float(amount)
        if amount < 0:
            return jsonify({'message': 'Amount must be greater than 0'}), 400
    except ValueError:
        return jsonify({'message': 'Amount must be a number'}), 400
    
    # Check if the amount is <= 10 digits
    if len(amount) > 10:
        return jsonify({'message': 'Amount must be less than 10 digits'}), 400
    
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
    
    # Classify the expense
    category = classify_expense(title)
    
    # Get the last expense number
    last_expense = expenses_collection.find_one(
    {"user_id": user["_id"]},
    sort=[("serial_number", -1)]
)
    # If there is a last expense, add 1 to the serial number
    if last_expense:
        serial_number = last_expense.get("serial_number", 0) + 1
    else:
        serial_number = 1
    
    # Create the expense item
    expenses_collection.insert_one({
        "user_id": user['_id'],
        "title": title,
        "date": date.isoformat(),
        "amount_usd": amount_usd,
        "amount_ils": amount_ils,
        "category": category,
        "serial_number": serial_number
    })

    return jsonify({'message': 'Expense added'}), 200


def handle_get_expenses(month, year, session_id):
    # Get the user from the session ID
    email = get_email_from_session_id(session_id)
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Check if the month and year are valid
    if month is None or year is None:
        return jsonify({"error": "Missing month or year"}), 400
    
    # Calculate the start and end dates for the month
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    except ValueError:
        return jsonify({"error": "Invalid month or year"}), 400
    
    # Get the expenses for the month
    expenses = list(expenses_collection.find({
        "user_id": user["_id"],
        "date": {
            "$gte": start_date.isoformat(),
            "$lt": end_date.isoformat()
    }}))

    # Convert the ObjectId to a string and remove the user_id field
    for expense in expenses:
        expense["_id"] = str(expense["_id"])
        if "user_id" in expense:
            expense["user_id"] = str(expense["user_id"])

    return jsonify({"expenses": expenses}), 200
    
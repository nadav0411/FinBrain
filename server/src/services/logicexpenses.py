# FinBrain Project - logicexpenses.py - MIT License (c) 2025 Nadav Eshed


from flask import jsonify
from db import users_collection, expenses_collection
from services.logicconnection import get_email_from_session_id
from datetime import datetime
import requests
import re
import pandas as pd
import logging
import os
from db import cache
import sys
try:
    from models.predictmodelloader import model, vectorizer
except ModuleNotFoundError:
    if (os.getenv('GITHUB_ACTIONS') or '').lower() in ('1', 'true', 'yes'):
        from src.models.predictmodelloader import model, vectorizer
    else:
        raise


# Create a logger for this module
logger = logging.getLogger(__name__)

# List of categories
categories = [
    'Food & Drinks',
    'Housing & Bills',
    'Transportation',
    'Education & Personal Growth',
    'Health & Essentials',
    'Leisure & Gifts',
    'Other'
]


def classify_expense(text):
    """
    This function gets a sentence (like 'Bought medicine')
    and returns the best category (like 'health & essentials')
    """
    # First, make sure the input is a string and is not empty or whitespace-only
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning(f"Invalid text input for classification | text={text}")
        # If the text is bad, we return 'other' by default
        return "Other"  

    try:
        # Use the saved vectorizer to turn the text into a number vector
        vector = vectorizer.transform([text])

        # Now we use the trained model to predict the category
        prediction = model.predict(vector)

        # Return the predicted category (it's a list with one value)
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during expense classification | text={text} | error={str(e)}")
        return "Other"


def get_usd_to_ils_rate(date_str):
    """ 
    Get the USD to ILS rate for a given date
    This function is called when the user wants to add an expense
    It returns the USD to ILS rate for the given date
    """
    # Check cache first
    cached_rate = cache.get_cached_currency_rate(date_str)
    if cached_rate is not None:
        return cached_rate
    
    # If not in cache, get from API
    url = f"https://api.frankfurter.app/{date_str}?from=USD&to=ILS"
    try:
        # Wait for the API to respond
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates']['ILS']
            logger.info(f"Exchange rate retrieved successfully | date={date_str} | rate={rate}")
            
            # Cache the rate for future use (don't fail if caching fails)
            try:
                cache.add_to_cache_currency_rate(date_str, rate)
            except Exception as cache_error:
                logger.warning(f"Failed to cache currency rate | date={date_str} | rate={rate} | error={str(cache_error)}")
            
            return rate
        else:
            logger.warning(f"API returned non-200 status | status_code={response.status_code}")
    # If the API returns an error, return a default rate
    except Exception as e:
        logger.exception(f"Error calling exchange rate API | url={url}")
    return None


def handle_add_expense(data, session_id):
    """
    This function is called when the user wants to add an expense to their account
    It checks if the required fields are present and if the title is valid
    It then checks if the amount is valid and if the date is valid
    It then checks if the currency is valid and if the expense is valid
    It then adds the expense to the database
    """
    # Check if session ID is valid (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Session ID is required'}), 400

    # Get the email from the session ID
    email = get_email_from_session_id(session_id)
    if not email:
        logger.warning(f"Unauthorized access attempt | session_id={session_id}")
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Check if the user is a demo user
    if email == 'demo':
        return jsonify({'message': 'Demo user cannot add expenses'}), 400
    
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
    if len(str(amount)) > 10:
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
    if usd_to_ils_rate is None:
        return jsonify({'message': 'Failed to get exchange rate'}), 500
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
        logger.warning(f"User not found during expense addition | email={email}")
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
    try:
        expenses_collection.insert_one({
            "user_id": user['_id'],
            "title": title,
            "date": date.isoformat(),
            "amount_usd": amount_usd,
            "amount_ils": amount_ils,
            "category": category,
            "serial_number": serial_number
        })
    except Exception as e:
        logger.error(f"Failed to insert expense | title={title} | email={email} | error={str(e)}")
        return jsonify({'message': 'Failed to add expense'}), 500

    # delete cache for this month and year for the user
    try:
        cache.delete_user_expenses_cache(email, date.month, date.year)
    except Exception as cache_error:
        logger.warning(f"Failed to delete cache after adding expense | month={date.month} | year={date.year} | email={email} | error={str(cache_error)}")

    logger.info(f"Expense added | title={title} | date={date} | amount={amount} | currency={currency} | category={category} | serial_number={serial_number}")
    return jsonify({'message': 'Expense added'}), 200


def handle_get_expenses(month, year, session_id):
    """    
    This function is called when the user wants to get their expenses from their account
    It gets the user from the session ID, checks if the month and year are valid,
    calculates the start and end dates for the month, gets the expenses for the month,
    converts the ObjectId to a string and removes the user_id field, and returns the expenses
    """
    # Check if session ID is valid (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Session ID is required'}), 400

    # Get the user from the session ID
    email = get_email_from_session_id(session_id)
    user = users_collection.find_one({'email': email})
    if not user:
        logger.warning(f"User not found during get expenses | email={email}")
        return jsonify({'message': 'User not found'}), 404

    # Check if the month and year are valid (None or not int)
    if month is None or year is None:
        return jsonify({"message": "Missing month or year"}), 400
    
    # Check if the month and year are valid
    if month < 1 or month > 12 or year < 2015 or year > 2027:
        return jsonify({"message": "Invalid month or year"}), 400
    
    # Check cache first
    cached_expenses = cache.get_cached_user_expenses(email, month, year)
    if cached_expenses is not None:
        logger.info(f"Get expenses from cache successful | month={month} | year={year} | expense_count={len(cached_expenses)} | email={email}")
        return jsonify({"expenses": cached_expenses}), 200
    
    # Calculate the start and end dates for the month
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    except ValueError:
        return jsonify({"message": "Invalid month or year"}), 400
    
    # Get the expenses for the month
    expenses = list(expenses_collection.find({
        "user_id": user["_id"],
        "date": {
            "$gte": start_date.date().isoformat(),
            "$lt": end_date.date().isoformat()
    }}))

    # Convert the ObjectId to a string and remove the user_id field
    for expense in expenses:
        expense["_id"] = str(expense["_id"])
        if "user_id" in expense:
            expense["user_id"] = str(expense["user_id"])

    # Cache the expenses for future use (don't fail if caching fails)
    try:
        cache.add_to_cache_user_expenses(email, month, year, expenses)
    except Exception as cache_error:
        logger.warning(f"Failed to cache user expenses | month={month} | year={year} | email={email} | error={str(cache_error)}")

    logger.info(f"Get expenses successful | month={month} | year={year} | expense_count={len(expenses)} | email={email}")
    return jsonify({"expenses": expenses}), 200


def handle_get_expenses_for_dashboard(chart, currency, months, categories, session_id):
    """
    This function is called when the user wants to get the expenses for the dashboard
    It gets the user from the session ID, checks if the chart and currency are valid,
    checks if the months are valid, gets the user ID, gets the month regexes,
    gets the expenses for the months, initializes the categories totals, sets the amount key,
    sums the expenses for the categories, calculates the total amount, calculates the percentage for each category,
    and returns the result
    """
    # Check if session ID is valid (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Session ID is required'}), 400

    # Get the user from the session ID
    email = get_email_from_session_id(session_id)
    user = users_collection.find_one({'email': email})
    if not user:
        logger.warning(f"User not found during dashboard request | email={email}")
        return jsonify({'message': 'User not found'}), 404
    
    # Check if the chart is valid
    if chart not in ['category_breakdown', 'monthly_comparison']:
        return jsonify({'message': 'Invalid chart'}), 400
    
    # Check if the currency is valid
    if currency not in ['ILS', 'USD']:
        return jsonify({'message': 'Invalid currency'}), 400
    
    # Check if the months are valid [year-month]
    for month in months:
        if not re.match(r'^\d{4}-\d{2}$', month):
            return jsonify({'message': 'Invalid month'}), 400
            
    # Limit selection to at most 12 months
    if len(months) > 12:
        return jsonify({'message': 'Too many months selected. Maximum is 12.'}), 400
    
    # Check if the categories are not empty
    if categories is None:
        return jsonify({'message': 'Categories are required'}), 400
    
    # Check if the categories are valid
    valid_categories = ['Food & Drinks', 'Housing & Bills', 'Transportation', 'Education & Personal Growth', 'Health & Essentials', 'Leisure & Gifts', 'Other'] + ['All']
    if len(categories) == 1:
        if categories[0] not in valid_categories:
            return jsonify({'message': 'Invalid category'}), 400
    else:
        for category in categories:
            if category not in valid_categories:
                return jsonify({'message': 'Invalid category'}), 400
    
    # Get the user ID
    user_id = user['_id']
    # Get the month regexes
    month_regexes = [re.compile(f'^{month}') for month in months]

    # Handle the category breakdown chart
    if chart == 'category_breakdown':
        result = handle_category_breakdown(month_regexes, user_id, currency)

    # Handle the monthly comparison chart
    elif chart == 'monthly_comparison':
        result = handle_monthly_comparison(month_regexes, user_id, currency, categories, months)
    
    logger.info(f"Get expenses for dashboard successful | chart={chart} | currency={currency} | months={months} | categories={categories} | email={email}")
    return jsonify({
        'currency': currency,
        'chart': chart,
        'months': months,
        'data': result
    }), 200


def handle_category_breakdown(month_regexes, user_id, currency):
    """
    This function is called when the user wants to get the category breakdown for the dashboard
    It gets the expenses for the months, initializes the categories totals, sets the amount key,
    sums the expenses for the categories, calculates the total amount, calculates the percentage for each category,
    and returns the result
    """
    # Get the expenses for the months
    expenses_cursor = expenses_collection.find({
        'user_id': user_id,
        'date': {'$in': month_regexes}
    })

    # Initialize the categories totals
    categories_totals = {
        "Food & Drinks": 0,
        "Housing & Bills": 0,
        "Transportation": 0,
        "Education & Personal Growth": 0,
        "Health & Essentials": 0,
        "Leisure & Gifts": 0,
        "Other": 0
    }

    # Set the amount key
    amount_key = 'amount_ils'
    if currency == 'USD':
        amount_key = 'amount_usd'
    
    # Sum the expenses for the categories
    for expense in expenses_cursor:
        category = expense.get('category', 'Other')
        if category not in categories_totals:
            category = 'Other'
        categories_totals[category] += expense.get(amount_key, 0)
    
    # Calculate the total amount
    total_amount = sum(categories_totals.values())

    result = []
    # Calculate the percentage for each category
    for category, amount in categories_totals.items():
        if total_amount > 0:
            percentage = (amount / total_amount) * 100
        else:
            percentage = 0
        # Add the category to the result
        result.append({
            'category': category,
            # Round the amount to 2 decimal places
            'amount': round(amount, 2),
            'percentage': round(percentage, 2)
        })
    
    return result


def handle_monthly_comparison(month_regexes, user_id, currency, categories, months):
    """
    This function is called when the user wants to get the monthly comparison for the dashboard
    It gets the expenses for the months and categories, initializes monthly comparison dictionary,
    sums the expenses for each month, calculates percentages, and returns the result
    """
    # Get the expenses for the months and categories
    # If "All" is in categories, don't filter by category
    if 'All' in categories:
        expenses_cursor = expenses_collection.find({
            'user_id': user_id,
            'date': {'$in': month_regexes}
        })
    else:
        expenses_cursor = expenses_collection.find({
            'user_id': user_id,
            'date': {'$in': month_regexes},
            'category': {'$in': categories} 
        })

    # Initialize dictionary for monthly comparison
    monthly_comparison = {}
    for month in months:
        monthly_comparison[month] = 0

    # Set the amount key
    amount_key = 'amount_ils'
    if currency == 'USD':
        amount_key = 'amount_usd'

    # Sum the expenses for each month
    for expense in expenses_cursor:
        expense_date = expense['date']
        # Extract month from full date (e.g., "2025-09-10" -> "2025-09")
        expense_month = expense_date[:7]  # Take first 7 characters (YYYY-MM)
        monthly_comparison[expense_month] += expense[amount_key]
    
    # Get the value of the month with the max amount
    max_amount = max(monthly_comparison.values()) if monthly_comparison else 0
    
    result = []
    # Add the month and amount to the result
    for month, amount in monthly_comparison.items():
        if max_amount > 0:
            percentage = (amount / max_amount) * 100
        else:
            percentage = 0
        result.append({
            'month': month,
            'amount': round(amount, 2),
            'percentage': round(percentage, 2)
        })
    
    return result

def handle_update_expense_category(data, session_id):
    """
    This function is called when the user wants to update the category of an expense
    It gets the user from the session ID, checks if the serial number is valid,
    checks if the current category is valid, checks if the new category is valid,
    updates the category of the expense, and returns the result
    """
    # Check if session ID is valid (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Session ID is required'}), 400
    
    # Get the email from the session ID
    email = get_email_from_session_id(session_id)

    # Check if the user is a demo user
    if email == 'demo':
        return jsonify({'message': 'Demo user cannot update expenses'}), 400
    
    # Get the user from the email
    user = users_collection.find_one({'email': email})
    if not user:
        logger.warning(f"User not found during category update | email={email}")
        return jsonify({'message': 'User not found'}), 404
    
    # Check if data is None (missing JSON)
    if data is None:
        return jsonify({'message': 'Serial number is required'}), 400
    
    # Get the serial number from the data and check if it is valid
    serial_number = data.get('serial_number')
    if serial_number is None or serial_number == '':
        return jsonify({'message': 'Serial number is required'}), 400
    
    # Get the current category
    current_category_client = data.get('current_category')
    if not current_category_client:
        return jsonify({'message': 'Current category is required'}), 400

    # Get the new category from the data and check if it is valid
    new_category = data.get('new_category')
    if not new_category:
        return jsonify({'message': 'New category is required'}), 400
    
    # Get the current category of the expense
    existing_expense = expenses_collection.find_one({
        'user_id': user['_id'],
        'serial_number': serial_number
    })

    if not existing_expense:
        return jsonify({'message': 'Expense not found'}), 404

    # Check if the current category in the database is the same as the current category from the client
    if existing_expense.get('category') != current_category_client:
        return jsonify({'message': 'Category is already updated'}), 400
    
    # Check if the new category is in the list of categories
    if new_category not in categories or new_category == existing_expense.get('category'):
        return jsonify({'message': 'Invalid category'}), 400

    # Update the category of the expense
    try:
        result = expenses_collection.update_one({
            'user_id': user['_id'],
            'serial_number': serial_number
        }, {
            '$set': {
                'category': new_category
            }
        })
    except Exception as e:
        logger.error(f"Failed to update expense category | serial_number={serial_number} | email={email} | error={str(e)}")
        return jsonify({'message': 'Failed to update category'}), 500

    # Check if the expense was found
    if result.matched_count == 0:
        return jsonify({'message': 'Expense not found'}), 404
    
    # Get the title of the expense
    expense_title = existing_expense.get('title')
    
    # Add the expense and the new category to user_feedback file to optimize the model
    try:
        # Skip feedback file updates in test environment
        is_test_env = any('pytest' in arg for arg in sys.argv)
        if not is_test_env:
            # Use relative path from the current file location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            feedback_path = os.path.join(current_dir, "..", "models", "finbrain_model", "user_feedback.csv")
            df = pd.read_csv(feedback_path)
            new_row = pd.DataFrame([{'description': expense_title, 'category': new_category}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(feedback_path, index=False)
            logger.info(f"User feedback updated | expense_title={expense_title} | new_category={new_category}")
        else:
            logger.info("Skipping user_feedback.csv update in test environment")
    except Exception as e:
        logger.error(f"Failed to update user feedback | expense_title={expense_title} | new_category={new_category} | error={str(e)}")

    # delete cache for the month and year of this expense
    try:
        expense_date = datetime.strptime(existing_expense.get('date'), '%Y-%m-%d').date()
        cache.delete_user_expenses_cache(email, expense_date.month, expense_date.year)
    except Exception as cache_error:
        logger.warning(f"Failed to delete cache after updating expense category | serial_number={serial_number} | email={email} | error={str(cache_error)}")

    logger.info(f"Expense category updated | serial_number={serial_number} | old_category={existing_expense.get('category')} | new_category={new_category} | email={email}")
    return jsonify({'message': 'Category updated', 'new_category': new_category}), 200


def handle_delete_expense(data, session_id):
    """
    This function is called when the user wants to delete an expense from their account
    It gets the user from the session ID, checks if the serial number is valid,
    deletes the expense, and returns the result
    """
    # Check if session ID is valid (handle common "null" strings)
    if not session_id or str(session_id).strip().lower() in {"", "none", "null", "undefined"}:
        return jsonify({'message': 'Session ID is required'}), 400
    
    # Get the email from the session ID
    email = get_email_from_session_id(session_id)

    # Check if the user is a demo user
    if email == 'demo':
        return jsonify({'message': 'Demo user cannot delete expenses'}), 400
    
    # Get the user from the email
    user = users_collection.find_one({'email': email})
    if not user:
        logger.warning(f"User not found during expense deletion | email={email}")
        return jsonify({'message': 'User not found'}), 404
    
    # Check if data is None (missing JSON)
    if data is None:
        return jsonify({'message': 'Serial number is required'}), 400
    
    # Get the serial number from the data and check if it is valid
    serial_number = data.get('serial_number')
    if serial_number is None or serial_number == '':
        return jsonify({'message': 'Serial number is required'}), 400
    
    # Check if the expense exists for this user first
    existing_expense = expenses_collection.find_one({
        'user_id': user['_id'],
        'serial_number': serial_number
    })
    
    if not existing_expense:
        return jsonify({'message': 'Expense not found'}), 404
    
    # Delete the expense
    try:
        result = expenses_collection.delete_one({
            'user_id': user['_id'],
            'serial_number': serial_number
        })
    except Exception as e:
        logger.error(f"Failed to delete expense | serial_number={serial_number} | email={email} | error={str(e)}")
        return jsonify({'message': 'Failed to delete expense'}), 500
    
    # Check if the expense was found
    if result.deleted_count == 0:
        return jsonify({'message': 'Expense not found'}), 404
    
    # delete cache for the month and year of this expense
    try:
        expense_date = datetime.strptime(existing_expense.get('date'), '%Y-%m-%d').date()
        cache.delete_user_expenses_cache(email, expense_date.month, expense_date.year)
    except Exception as cache_error:
        logger.warning(f"Failed to delete cache after deleting expense | serial_number={serial_number} | email={email} | error={str(cache_error)}")

    logger.info(f"Expense deleted | serial_number={serial_number} | email={email}")
    return jsonify({'message': 'Expense deleted', 'serial_number': serial_number}), 200
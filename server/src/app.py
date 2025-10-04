# FinBrain Project - app.py - MIT License (c) 2025 Nadav Eshed


import os
from dotenv import load_dotenv


# Auto-load environment file based on ENV variable (defaults to development)
env = os.getenv('ENV', 'development')
if env == 'test':
    load_dotenv('configs/.env.test')
elif env == 'development':
    load_dotenv('configs/.env.development')
elif env == 'production':
    load_dotenv('configs/.env.docker')
else:
    load_dotenv('configs/.env.development') 


import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from services import logicconnection as logic_connection
from services import logicexpenses as logic_expenses
from db import db as mongo_db


# Configure logging at the main entry point
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# Create logger for this module
logger = logging.getLogger(__name__)


# Creates a Flask app - my web server and allows other applications to connect to it (such as my React client)
app = Flask(__name__)

# Print environment and DB info for diagnostics
env_val = os.getenv('ENV')
mongo_name = getattr(mongo_db, 'name', 'unknown')
logger.info(f"Mongo URI in use | database={mongo_name}")

# Allow CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})


# Health check route - deployment monitoring
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'FinBrain API is running'}), 200


# Signup route - This is where the user will sign up for an account
@app.route('/signup', methods=['POST'])
def signup():
    logger.info(f"Signup request received | remote_addr={request.remote_addr}")

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning(f"Signup request with invalid JSON | remote_addr={request.remote_addr}")
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning(f"Signup request with invalid JSON | remote_addr={request.remote_addr} | error={str(e)}")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    result = logic_connection.handle_signup(data)
    logger.info(f"Signup request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Login route - This is where the user will login to their account
@app.route('/login', methods=['POST'])
def login():
    logger.info(f"Login request received | remote_addr={request.remote_addr}")

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning(f"Login request with invalid JSON | remote_addr={request.remote_addr}")
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning(f"Login request with invalid JSON | remote_addr={request.remote_addr} | error={str(e)}")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    result = logic_connection.handle_login(data)
    logger.info(f"Login request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Logout route - revoke the current session
@app.route('/logout', methods=['POST'])
def logout():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    logger.info(f"Logout request received | remote_addr={request.remote_addr} | session_id={(session_id[:8] if session_id else None)}")
    result = logic_connection.handle_logout(session_id)
    logger.info(f"Logout request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Heartbeat route - keep session alive while tab is open
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    logger.info(f"Heartbeat request received | remote_addr={request.remote_addr} | session_id={(session_id[:8] if session_id else None)}")
    result = logic_connection.handle_heartbeat(session_id)
    logger.info(f"Heartbeat request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Add expense route - This is where the user will add an expense to their account
@app.route('/add_expense', methods=['POST'])
def add_expense():
    logger.info(f"Add expense request received | remote_addr={request.remote_addr}")

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning(f"Add expense request with invalid JSON | remote_addr={request.remote_addr}")
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning(f"Add expense request with invalid JSON | remote_addr={request.remote_addr} | error={str(e)}")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_add_expense(data, session_id)
    logger.info(f"Add expense request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Get expenses route - This is where the user will get their expenses from their account
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    session_id = request.headers.get('Session-ID')
    logger.info(f"Get expenses request received | month={month} | year={year} | remote_addr={request.remote_addr}")
    result = logic_expenses.handle_get_expenses(month, year, session_id)
    logger.info(f"Get expenses request completed | status_code={result[1]} | month={month} | year={year} | remote_addr={request.remote_addr}")
    return result


# Get expenses for dashboard route - This is where the user will get their expenses for the dashboard
@app.route('/expenses_for_dashboard', methods=['GET'])
def expenses_for_dashboard():
    chart = request.args.get('chart', type=str)
    currency = request.args.get('currency', type=str)
    months = request.args.getlist('months')
    categories = request.args.getlist('categories')
    session_id = request.headers.get('Session-ID')
    logger.info(f"Get expenses for dashboard request received | chart={chart} | currency={currency} | months={months} | categories={categories} | remote_addr={request.remote_addr}")
    result = logic_expenses.handle_get_expenses_for_dashboard(chart, currency, months, categories, session_id)
    logger.info(f"Get expenses for dashboard request completed | status_code={result[1]} | chart={chart} | currency={currency} | remote_addr={request.remote_addr}")
    return result


# Update expense category route - This is where the user will update the category of an expense
@app.route('/update_expense_category', methods=['POST'])
def update_expense_category():
    logger.info(f"Update expense category request received | remote_addr={request.remote_addr}")
    
    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning(f"Update expense category request with invalid JSON | remote_addr={request.remote_addr}")
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning(f"Update expense category request with invalid JSON | remote_addr={request.remote_addr} | error={str(e)}")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_update_expense_category(data, session_id)
    logger.info(f"Update expense category request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


# Delete expense route - This is where the user will delete an expense from their account
@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    logger.info(f"Delete expense request received | remote_addr={request.remote_addr}")
    
    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning(f"Delete expense request with invalid JSON | remote_addr={request.remote_addr}")
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning(f"Delete expense request with invalid JSON | remote_addr={request.remote_addr} | error={str(e)}")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_delete_expense(data, session_id)
    logger.info(f"Delete expense request completed | status_code={result[1]} | remote_addr={request.remote_addr}")
    return result


if __name__ == '__main__':
    # Get the environment from the environment variable (if not set, default to development)
    env = os.getenv('ENV', 'development')
    if env == 'development':
        # host = 0.0.0.0 means the server will be accessible from any IP address
        # port = 5000 means the server will run on port 5000
        # In development, we want to use debug mode to see errors and changes
        # But we set use_reloader=False to avoid the app running twice
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
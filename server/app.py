# app.py


import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import logicconnection as logic_connection
import logicexpenses as logic_expenses



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
CORS(app, resources={r"/*": {"origins": "*"}})


# Signup route - This is where the user will sign up for an account
@app.route('/signup', methods=['POST'])
def signup():
    logger.info("Signup request received", extra={"remote_addr": request.remote_addr})

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Signup request with invalid JSON", extra={"remote_addr": request.remote_addr})
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning("Signup request with invalid JSON", extra={"remote_addr": request.remote_addr, "error": str(e)})
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    result = logic_connection.handle_signup(data)
    logger.info("Signup request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Login route - This is where the user will login to their account
@app.route('/login', methods=['POST'])
def login():
    logger.info("Login request received", extra={"remote_addr": request.remote_addr})

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Login request with invalid JSON", extra={"remote_addr": request.remote_addr})
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning("Login request with invalid JSON", extra={"remote_addr": request.remote_addr, "error": str(e)})
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    result = logic_connection.handle_login(data)
    logger.info("Login request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Logout route - revoke the current session
@app.route('/logout', methods=['POST'])
def logout():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    logger.info("Logout request received", extra={"remote_addr": request.remote_addr, "session_id": session_id[:8] if session_id else None})
    result = logic_connection.handle_logout(session_id)
    logger.info("Logout request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Heartbeat route - keep session alive while tab is open
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    logger.info("Heartbeat request received", extra={"remote_addr": request.remote_addr, "session_id": session_id[:8] if session_id else None})
    result = logic_connection.handle_heartbeat(session_id)
    logger.info("Heartbeat request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Add expense route - This is where the user will add an expense to their account
@app.route('/add_expense', methods=['POST'])
def add_expense():
    logger.info("Add expense request received", extra={"remote_addr": request.remote_addr})

    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Add expense request with invalid JSON", extra={"remote_addr": request.remote_addr})
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning("Add expense request with invalid JSON", extra={"remote_addr": request.remote_addr, "error": str(e)})
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_add_expense(data, session_id)
    logger.info("Add expense request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Get expenses route - This is where the user will get their expenses from their account
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    session_id = request.headers.get('Session-ID')
    logger.info("Get expenses request received", extra={"month": month, "year": year, "remote_addr": request.remote_addr})
    result = logic_expenses.handle_get_expenses(month, year, session_id)
    logger.info("Get expenses request completed", extra={"status_code": result[1], "month": month, "year": year, "remote_addr": request.remote_addr})
    return result


# Get expenses for dashboard route - This is where the user will get their expenses for the dashboard
@app.route('/expenses_for_dashboard', methods=['GET'])
def expenses_for_dashboard():
    chart = request.args.get('chart', type=str)
    currency = request.args.get('currency', type=str)
    months = request.args.getlist('months')
    categories = request.args.getlist('categories')
    session_id = request.headers.get('Session-ID')
    logger.info("Get expenses for dashboard request received", extra={"chart": chart, "currency": currency, "months": months, "categories": categories, "remote_addr": request.remote_addr})
    result = logic_expenses.handle_get_expenses_for_dashboard(chart, currency, months, categories, session_id)
    logger.info("Get expenses for dashboard request completed", extra={"status_code": result[1], "chart": chart, "currency": currency, "remote_addr": request.remote_addr})
    return result


# Update expense category route - This is where the user will update the category of an expense
@app.route('/update_expense_category', methods=['POST'])
def update_expense_category():
    logger.info("Update expense category request received", extra={"remote_addr": request.remote_addr})
    
    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Update expense category request with invalid JSON", extra={"remote_addr": request.remote_addr})
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning("Update expense category request with invalid JSON", extra={"remote_addr": request.remote_addr, "error": str(e)})
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_update_expense_category(data, session_id)
    logger.info("Update expense category request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


# Delete expense route - This is where the user will delete an expense from their account
@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    logger.info("Delete expense request received", extra={"remote_addr": request.remote_addr})
    
    # Get the JSON data from the request 
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Delete expense request with invalid JSON", extra={"remote_addr": request.remote_addr})
            return jsonify({'message': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.warning("Delete expense request with invalid JSON", extra={"remote_addr": request.remote_addr, "error": str(e)})
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    # Get the session ID from the request headers and handle the request
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_delete_expense(data, session_id)
    logger.info("Delete expense request completed", extra={"status_code": result[1], "remote_addr": request.remote_addr})
    return result


if __name__ == '__main__':
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
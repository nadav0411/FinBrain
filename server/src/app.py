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
from src.services import logicconnection as logic_connection
from src.services import logicexpenses as logic_expenses
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
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Root route - check if the backend is running
@app.route('/')
def root():
    return jsonify({'message': 'FinBrain Backend is live!'}), 200


# Version route - check the version of the backend
@app.route('/version')
def version():
    return jsonify({'version': '1.0.0', 'env': env}), 200


# Health check route - deployment monitoring (check Flask + MongoDB + Redis are running)
@app.route('/health', methods=['GET'])
def health_check():
    from db import db
    from db.cache import r

    mongo_ok = False
    redis_ok = False

    # Check MongoDB connection
    try:
        db.command('ping')
        mongo_ok = True
    except Exception as e:
        logger.error(f"[Health Check] MongoDB connection failed | error={str(e)}")
    
    # Check Redis connection
    try:
        r.ping()
        redis_ok = True
    except Exception as e:
        logger.error(f"[Health Check] Redis connection failed | error={str(e)}")
    
    # Return the result
    status = 'healthy' if mongo_ok and redis_ok else 'degraded'

    return jsonify({
        'status': status,
        'mongo': mongo_ok,
        'redis': redis_ok,
        'message': 'FinBrain API health check'
    }), 200


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
    from os import environ
    port = int(environ.get('PORT', 5000))
    # host = 0.0.0.0 means the server will be accessible from any IP address
    # port = means the server will run on 'PORT' environment variable (if not set, default to 5000)
    # debug = False means the server will run in production mode
    # use_reloader = False to avoid the app running twice
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


# Render Deployment:
# The backend of FinBrain is deployed on Render.
# A cloud platform that automatically builds and hosts the server directly from the GitHub repository.
# Every time I push new code to the main branch, Render detects the update, 
# rebuilds the Flask backend using Docker, and redeploys it to production — providing a fully automated CI/CD workflow.
# The server connects to two main managed services:
# 1. MongoDB Atlas - The connection is securely handled through environment variables defined in Render.
# 2. Redis (Value Keys) - Render provides a managed Redis (Value Keys) service that the Flask backend connects to via the 
#    REDIS_URL environment variable for real-time caching and session storage.


# Vercel Deployment:
# The frontend of FinBrain (built with React + Vite) is deployed on Vercel.
# Vercel automatically builds and hosts the client directly from the GitHub repository.
# Each time I push new code to the main branch, Vercel triggers a new build,
# compiles the React app into optimized static files, and redeploys it globally via CDN.
# Environment variables such as VITE_API_URL are securely managed in Vercel’s dashboard,
# allowing the frontend to communicate seamlessly with the Flask backend hosted on Render.
# CDN = Content Delivery Network, is a global network of servers that delivers my website’s files (like images, scripts, and pages)
# from the location closest to each user — making the site load faster and more reliably everywhere.
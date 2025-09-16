# app.py

from flask import Flask, request
from flask_cors import CORS
import logicconnection as logic_connection
import logicexpenses as logic_expenses


# Creates a Flask app - my web server and allows other applications to connect to it (such as my React client)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Signup route - This is where the user will sign up for an account
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    result = logic_connection.handle_signup(data)
    return result

# Login route - This is where the user will login to their account
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result = logic_connection.handle_login(data)
    return result

# Logout route - revoke the current session
@app.route('/logout', methods=['POST'])
def logout():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    result = logic_connection.handle_logout(session_id)
    return result

# Add expense route - This is where the user will add an expense to their account
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_add_expense(data, session_id)
    return result

# Get expenses route - This is where the user will get their expenses from their account
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_get_expenses(month, year, session_id)
    return result

# Get expenses for dashboard route - This is where the user will get their expenses for the dashboard
@app.route('/expenses_for_dashboard', methods=['GET'])
def expenses_for_dashboard():
    chart = request.args.get('chart', type=str)
    currency = request.args.get('currency', type=str)
    months = request.args.getlist('months')
    categories = request.args.getlist('categories')
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_get_expenses_for_dashboard(chart, currency, months, categories, session_id)
    return result

# Update expense category route - This is where the user will update the category of an expense
@app.route('/update_expense_category', methods=['POST'])
def update_expense_category():
    data = request.get_json()
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_update_expense_category(data, session_id)
    return result

# Delete expense route - This is where the user will delete an expense from their account
@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    data = request.get_json()
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_delete_expense(data, session_id)
    return result

# Heartbeat route - keep session alive while tab is open
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    session_id = request.headers.get('Session-ID') or request.args.get('session_id')
    result = logic_connection.handle_heartbeat(session_id)
    return result



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
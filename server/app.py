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

# Add expense route - This is where the user will add an expense to their account
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_add_expense(data, session_id)
    return result

@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_get_expenses(month, year, session_id)
    return result

@app.route('/expenses_for_dashboard', methods=['GET'])
def expenses_for_dashboard():
    chart = request.args.get('chart', type=str)
    currency = request.args.get('currency', type=str)
    months = request.args.getlist('months')
    session_id = request.headers.get('Session-ID')
    result = logic_expenses.handle_get_expenses_for_dashboard(chart, currency, months, session_id)
    return result

if __name__ == '__main__':
    app.run(debug=True)
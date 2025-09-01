from flask import Flask, request
from flask_cors import CORS
import logicconnection as logic_connection


# Creates a Flask app - my web server and allows other applications to connect to it (such as my React client)
app = Flask(__name__)
CORS(app)

# Signup route - This is where the user will sign up for an account
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    result = logic_connection.handle_signup(data)
    return result
    

if __name__ == '__main__':
    app.run(debug=True)
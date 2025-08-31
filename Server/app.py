from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']

    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Missing field {field}'}), 400
    
    if data.get('password') != data.get('confirmPassword'):
        return jsonify({'message': 'Passwords do not match'}), 400
    
    return jsonify({'message': 'Signup successful'}), 201

if __name__ == '__main__':
    app.run(debug=True)
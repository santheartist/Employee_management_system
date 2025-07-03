from flask import Flask, request, jsonify, render_template, redirect, session
from services.auth import check_user
from services.db import (
    initialize_db, get_all_employees, add_employee,
    update_employee, delete_employee, get_stats
)
from services.mail import send_email
from services.insights import generate_ai_graph # Make sure this import is correct
import os # Import the os module to access environment variables

app = Flask(__name__)
# It's highly recommended to use an environment variable for app.secret_key in production
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super-secret-key') # Using os.getenv for secret key
initialize_db()

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template("dashboard.html")

@app.route('/add')
def add_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template("employee_form.html")

@app.route('/stats')
def stats_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template("stats.html")

@app.route('/ai')
def ai_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template("ai.html")

@app.route('/logout')
def logout():
    print("✅ LOGOUT triggered")
    session.clear()
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if check_user(data.get("username"), data.get("password")):
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/employees', methods=['GET'])
def get_employees():
    return jsonify(get_all_employees())

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    return jsonify(add_employee(data))

@app.route('/employees/<emp_id>', methods=['PUT'])
def edit_employee(emp_id):
    data = request.json
    return jsonify(update_employee(emp_id, data))

@app.route('/employees/<emp_id>', methods=['DELETE'])
def remove_employee(emp_id):
    return jsonify(delete_employee(emp_id))

@app.route('/email/send', methods=['POST'])
def email_employee():
    data = request.json
    return jsonify(send_email(data))

@app.route('/stats/data', methods=['GET'])
def stats_data():
    return jsonify(get_stats())

@app.route('/insight', methods=['POST'])
def ai_insight():
    try:
        data = request.json
        prompt = data.get("prompt", "")

        if not prompt:
            print("Error: No prompt provided to /insight endpoint.")
            return jsonify({"error": "No prompt provided"}), 400

        img_base64 = generate_ai_graph(prompt)

        if img_base64:
            return jsonify({"image": img_base64})
        else:
            print(f"Error: generate_ai_graph returned None for prompt: {prompt}")
            return jsonify({"error": "Failed to generate chart. Please check server logs for details or try a different prompt."}), 500
    except Exception as e:
        print(f"An unexpected error occurred in /insight endpoint: {e}")
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Get the PORT from the environment variable, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    # Bind to '0.0.0.0' to be accessible from outside localhost (required for Render)
    app.run(host='0.0.0.0', port=port, debug=True)

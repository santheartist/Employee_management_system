users = {"admin": "admin"}  # Replace with DB or hashed passwords later

def check_user(username, password):
    return users.get(username.lower()) == password

import json
import os

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(username, role):
    users = load_users()
    if username in users:
        return False, 'User already exists.'
    users[username] = {'role': role}
    save_users(users)
    return True, 'User added.'

def remove_user(username):
    users = load_users()
    if username not in users:
        return False, 'User not found.'
    del users[username]
    save_users(users)
    return True, 'User removed.'

def list_users():
    return load_users()

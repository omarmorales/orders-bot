# bot/sessions = {}

sessions = {}

def get_session(phone_number):
    if phone_number not in sessions:
        sessions[phone_number] = {
            "state": "start",
            "order": [],
            "name": "",
            "history": [],
            "email": "",
        }
    return sessions[phone_number]

def reset_session(phone_number):
    sessions[phone_number] = {
        "state": "start",
        "order": [],
        "name": "",
        "history": [],
        "email": "",
    }
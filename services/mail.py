from mailjet_rest import Client
import re

api_key = 'your_api_key'
api_secret = 'your_api_secret'

def send_email(data):
    name = data.get("name")
    lname = data.get("lname")
    email_address = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    if not validate_email(email_address):
        return {"success": False, "error": "Invalid email"}

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    payload = {
        'Messages': [
            {
                "From": {"Email": "your_email@example.com", "Name": "HT Employee System"},
                "To": [{"Email": email_address, "Name": f"{name} {lname}"}],
                "Subject": subject,
                "TextPart": "Message from HT Employee System",
                "HTMLPart": f"<h3>Hi {name} {lname},</h3><p>{message}</p>",
                "CustomID": "EmployeeMessage"
            }
        ]
    }
    result = mailjet.send.create(data=payload)
    return {"success": result.status_code == 200}

def validate_email(email):
    pattern = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    return re.match(pattern, email) is not None

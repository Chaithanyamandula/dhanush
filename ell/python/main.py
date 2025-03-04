import eel
import os
import database as db  # Import database functions
import smtplib
from email.mime.text import MIMEText
import secrets  # For generating secure tokens

eel.init('python')

# Email configuration (replace with your own)
EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_email_password'  # Use an app password for Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

@eel.expose
def check_login(username, password):
    """Checks login credentials against database."""
    return db.check_user_credentials_mysql(username, password)

@eel.expose
def register_user(user_id, name, email, password, re_password):
    """Registers a new user after validation."""
    if password != re_password:
        return "Passwords do not match."
    if not db.is_allowed_user_id_mysql(user_id): #removed password check from allowed users.
        return "User ID is not allowed to register."
    if not name or not email or not password:
        return "All fields are required."
    if db.add_new_user_mysql(user_id, name, email, password): #Used mysql functions
        return True  # Signup successful
    else:
        return "User ID or email already exists."

def send_reset_email(email, reset_token):
    """Sends a password reset email."""
    msg = MIMEText(f"Click this link to reset your password: http://yourwebsite.com/reset?token={reset_token}&email={email}") #replace yourwebsite.com
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = EMAIL_SENDER
    msg['To'] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@eel.expose
def reset_password_request(username_or_email):
    """Handles forgot password request."""
    user = db.get_user_by_username_or_email_mysql(username_or_email)
    if user:
        email = user[3]  # Email is the 4th column (index 3)
        reset_token = secrets.token_urlsafe(16)  # Generate a secure token
        # Store the token with the user's email in your database (not shown here)
        # In a real app, you would have a table to store these tokens with expiration times.
        if send_reset_email(email, reset_token):
            print(f"Password reset requested for: {username_or_email} (Email sent)")
            return True
        else:
            return "Failed to send reset email."
    else:
        return "Username or Email not found."

@eel.expose
def reset_password(email, token, new_password, re_new_password):
    """Resets password in database after validation."""
    if new_password != re_new_password:
        return "Passwords do not match."

    # Verify the token and email against your stored tokens (not shown here)
    # In a real app, check if the token is valid and not expired.

    if db.update_password_mysql(email, new_password):
        print(f"Password reset for {email} successful.")
        return True
    else:
        return "Password reset failed."

@eel.expose
def open_python_file(filepath):
    """Opens a python file using the default system application."""
    try:
        full_filepath = os.path.join("python", filepath)
        if os.path.exists(full_filepath) and full_filepath.lower().endswith('.py'):
            os.startfile(full_filepath)  # For Windows
            return True
        else:
            return "File not found or not a Python file."
    except Exception as e:
        return f"Could not open file: {e}"

if __name__ == '__main__':
    eel.start('index.html', size=(800, 600))
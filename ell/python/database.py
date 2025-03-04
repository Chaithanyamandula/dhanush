import sqlite3  # You might still need sqlite3 for allowed_user_ids table OR remove if you move allowed_user_ids to MySQL as well
import mysql.connector
from datetime import datetime

# MySQL database setup
MYSQL_DATABASE_NAME = 'login'  # Database name is login as per your connection
MYSQL_TABLE_USERS = 'users' # Table name for users in MySQL
MYSQL_TABLE_ALLOWED_IDS = 'allowed_user_ids' # Table name for allowed users in MySQL

try:
    conn_mysql = mysql.connector.connect(
        host='localhost',
        user='root',
        password='tiger',
        database=MYSQL_DATABASE_NAME,
        auth_plugin='mysql_native_password'
    )
    print("Connected to MySQL successfully!")
    cursor_mysql = conn_mysql.cursor() # Create a cursor for MySQL connection
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    conn_mysql = None # Handle the case where connection fails

# SQLite database setup (You can remove this entire section if you only want to use MySQL)
DATABASE_NAME = 'users.db' # You can remove this if not using SQLite anymore

def create_mysql_tables():
    """Creates the users and allowed_user_ids tables in MySQL if they don't exist."""
    if conn_mysql is None: # Check if MySQL connection is established
        print("MySQL connection is not available. Cannot create tables.")
        return

    try:
        cursor_mysql.execute(f'''
            CREATE TABLE IF NOT EXISTS {MYSQL_TABLE_USERS} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                signup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')

        cursor_mysql.execute(f'''
            CREATE TABLE IF NOT EXISTS {MYSQL_TABLE_ALLOWED_IDS} (
                user_id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY
            )
        ''')
        conn_mysql.commit()
        print("MySQL tables created or already exist.")

    except mysql.connector.Error as err:
        print(f"Error creating MySQL tables: {err}")


def initialize_allowed_user_ids_mysql():
    """Initializes allowed user IDs in MySQL. Add more as needed."""
    if conn_mysql is None:
        print("MySQL connection is not available. Cannot initialize allowed user IDs.")
        return

    allowed_ids = ['user101', 'user102', 'user103']  # Example allowed user IDs
    for user_id in allowed_ids:
        try:
            cursor_mysql.execute(f"INSERT INTO {MYSQL_TABLE_ALLOWED_IDS} (user_id) VALUES (%s)", (user_id,))
        except mysql.connector.IntegrityError:
            # Ignore if user_id already exists
            pass
    conn_mysql.commit()
    print("MySQL allowed user IDs initialized.")


def is_allowed_user_id_mysql(user_id):
    """Checks if the user_id is in the allowed_user_ids table in MySQL."""
    if conn_mysql is None:
        print("MySQL connection is not available. Cannot check allowed user ID.")
        return False

    cursor_mysql.execute(f"SELECT user_id FROM {MYSQL_TABLE_ALLOWED_IDS} WHERE user_id = %s", (user_id,))
    result = cursor_mysql.fetchone()
    return result is not None


def get_user_by_username_or_email_mysql(username_or_email):
    """Retrieves user by username or email from MySQL."""
    if conn_mysql is None:
        print("MySQL connection is not available. Cannot get user.")
        return None

    cursor_mysql.execute(f"SELECT * FROM {MYSQL_TABLE_USERS} WHERE user_id = %s OR email = %s", (username_or_email, username_or_email))
    user = cursor_mysql.fetchone()
    return user


def check_user_credentials_mysql(username, password):
    """Verifies user credentials against MySQL database."""
    user = get_user_by_username_or_email_mysql(username)
    if user:
        stored_password = user[4]  # Password is the 5th column (index 4)
        if password == stored_password:  # In real app, use password hashing!
            return True
    return False


def add_new_user_mysql(user_id, name, email, password):
    """Adds a new user to the MySQL database."""
    if conn_mysql is None:
        print("MySQL connection is not available. Cannot add new user.")
        return False

    try:
        cursor_mysql.execute(f"INSERT INTO {MYSQL_TABLE_USERS} (user_id, name, email, password) VALUES (%s, %s, %s, %s)", (user_id, name, email, password))
        conn_mysql.commit()
        print(f"User {user_id} added to MySQL database.")
        return True
    except mysql.connector.IntegrityError:
        print(f"Error adding user {user_id} to MySQL: User ID or email already exists.")
        return False  # User ID or email already exists


def update_password_mysql(username_or_email, new_password):
    """Updates a user's password in MySQL."""
    if conn_mysql is None:
        print("MySQL connection is not available. Cannot update password.")
        return False

    cursor_mysql.execute(f"UPDATE {MYSQL_TABLE_USERS} SET password = %s WHERE user_id = %s OR email = %s", (new_password, username_or_email, username_or_email))
    conn_mysql.commit()
    print(f"Password updated for user/email: {username_or_email} in MySQL.")
    return True


# Initialize MySQL database tables and allowed user IDs on startup
create_mysql_tables()
initialize_allowed_user_ids_mysql()

# Example Usage (You would replace your SQLite function calls with these MySQL versions)
if __name__ == '__main__':
    if conn_mysql: # Only proceed if MySQL connection is successful
        # Example of adding a new user to MySQL
        if add_new_user_mysql('testuser', 'Test User', 'test@example.com', 'password123'):
            print("New user added successfully to MySQL.")

        # Example of checking user credentials against MySQL
        if check_user_credentials_mysql('testuser', 'password123'):
            print("User credentials verified against MySQL.")
        else:
            print("User credentials verification failed against MySQL.")

        # Example of updating password in MySQL
        if update_password_mysql('testuser', 'newpassword'):
            print("Password updated successfully in MySQL.")

        # Example of checking if user is allowed from MySQL
        if is_allowed_user_id_mysql('user101'):
            print("user101 is an allowed user (MySQL).")
        else:
            print("user101 is not an allowed user (MySQL).")

        user_data = get_user_by_username_or_email_mysql('test@example.com')
        if user_data:
            print(f"Retrieved user from MySQL: {user_data}")
        else:
            print("User not found in MySQL.")

    else:
        print("Skipping example usage due to failed MySQL connection.")

    if conn_mysql and conn_mysql.is_connected(): # Close MySQL connection only if it was established
        cursor_mysql.close()
        conn_mysql.close()
        print("MySQL connection closed.")
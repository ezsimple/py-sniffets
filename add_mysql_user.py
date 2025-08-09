#!/usr/bin/env python3
"""
A Python script to create a MySQL user and database with sudo privileges.

Usage:
    python3 add_mysql_user.py <user> <db_name> [password]

This updated version generates a secure, random password for the new user,
satisfying modern MySQL password policy requirements.
"""
import sys
import subprocess
import getpass
import secrets
import string

def usage():
    """
    Prints the usage information for the script and exits.
    """
    print("Usage: add_mysql_user.py <user> <db_name> [password]")
    print("Example: add_mysql_user.py myuser mydb mypassword123")
    print("Note: If a password is not provided, a secure random password will be generated.")
    sys.exit(1)

def run_mysql_command(command, root_password):
    """
    Executes a MySQL command using 'sudo mysql -e' with the provided root password.
    """
    print(f"Executing: {command}")
    try:
        # Pass the MySQL root password to the stdin of the subprocess.
        # The '-p' flag tells the mysql client to expect a password.
        subprocess.run(
            ['sudo', 'mysql', '-u', 'root', '-p', '-e', command],
            input=root_password,
            check=True,
            text=True,
            capture_output=True
        )
        print("... Success.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)

def generate_secure_password(length=10):
    """
    Generates a cryptographically secure random password.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def main():
    """
    Main function to parse arguments and create the MySQL user and database.
    """
    # Check for the correct number of command-line arguments.
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        usage()

    db_user = sys.argv[1]
    db_name = sys.argv[2]
    # If a password is provided as an argument, use it.
    # Otherwise, generate a secure random password.
    db_user_pass = sys.argv[3] if len(sys.argv) == 4 else generate_secure_password()

    print(f"Creating MySQL database '{db_name}' and user '{db_user}'...")
    print("----------------------------------------------------------")

    # Prompt for the MySQL root password securely.
    # This password is required for the script to perform administrative tasks.
    root_password = getpass.getpass("Enter MySQL ROOT password: ")

    # --- SQL Commands ---
    create_db_cmd = f"CREATE DATABASE IF NOT EXISTS `{db_name}`; "
    create_user_cmd = f"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{db_user_pass}';"
    grant_privileges_cmd = f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost';"
    flush_privileges_cmd = "FLUSH PRIVILEGES;"

    # Execute the SQL commands in order, passing the root password.
    run_mysql_command(create_db_cmd, root_password)
    run_mysql_command(create_user_cmd, root_password)
    run_mysql_command(grant_privileges_cmd, root_password)
    run_mysql_command(flush_privileges_cmd, root_password)

    print(f"\n✅ MySQL User '{db_user}' and database '{db_name}' created successfully.")
    print(f"The generated password for user '{db_user}' is: {db_user_pass}")
    print(f"Connection test command: mysql -u {db_user} -p -h localhost -D {db_name}")

if __name__ == "__main__":
    main()


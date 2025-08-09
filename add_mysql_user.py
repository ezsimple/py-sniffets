#!/usr/bin/env python3
"""
A Python script to create a MySQL user and database with sudo privileges.

Usage:
    python3 add_mysql_user.py <user> <db_name> [password]

The script uses 'sudo mysql' to run commands, assuming the current user
has sudo privileges and can access MySQL as root.
"""
import sys
import subprocess

def usage():
    """
    Prints the usage information for the script and exits.
    """
    print("Usage: add_mysql_user.py <user> <db_name> [password]")
    print("Example: add_mysql_user.py myuser mydb mypassword123")
    sys.exit(1)

def run_mysql_command(command):
    """
    Executes a MySQL command using 'sudo mysql -e'.
    The command is run with subprocess and error checking.
    """
    print(f"Executing: {command}")
    try:
        # Use subprocess.run to execute the command with sudo and mysql client.
        # 'check=True' will raise an exception if the command fails.
        subprocess.run(
            ['sudo', 'mysql', '-e', command],
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

def main():
    """
    Main function to parse arguments and create the MySQL user and database.
    """
    # Check for the correct number of command-line arguments.
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        usage()

    db_user = sys.argv[1]
    db_name = sys.argv[2]
    # Set a default password if not provided.
    db_user_pass = sys.argv[3] if len(sys.argv) == 4 else 'qwer!@34'

    print(f"Creating MySQL database '{db_name}' and user '{db_user}'...")

    # --- SQL Commands ---
    # Use backticks for database names to avoid issues with reserved keywords.
    # The 'localhost' specifies that the user can only connect from the local machine.
    # To allow remote connections, change 'localhost' to '%'
    create_db_cmd = f"CREATE DATABASE IF NOT EXISTS `{db_name}`; "
    create_user_cmd = f"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{db_user_pass}';"
    grant_privileges_cmd = f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost';"
    flush_privileges_cmd = "FLUSH PRIVILEGES;"

    # Execute the SQL commands in order.
    run_mysql_command(create_db_cmd)
    run_mysql_command(create_user_cmd)
    run_mysql_command(grant_privileges_cmd)
    run_mysql_command(flush_privileges_cmd)

    print(f"\n✅ MySQL User '{db_user}' and database '{db_name}' created successfully.")
    print(f"Connection test command: mysql -u {db_user} -p -h localhost -D {db_name}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
A Python script to create a PostgreSQL user and database.

Usage:
    python3 add_pg_user.py <user> <db_name> [password]

The script uses 'sudo -u postgres' to run commands, assuming the current user
has sudo privileges.
"""
import sys
import subprocess

def usage():
    """
    Prints the usage information for the script and exits.
    """
    print("Usage: add_pg_user.py <user> <db_name> [password]")
    print("Example: add_pg_user.py myuser mydb mypassword123")
    sys.exit(1)

def run_pg_command(command, is_sql_command=False, db_name=None):
    """
    Executes a PostgreSQL command using 'sudo -u postgres'.
    Handles both `createdb` and `psql` commands.
    """
    # The command to be executed by subprocess
    cmd = ['sudo', '-u', 'postgres']
    if is_sql_command:
        # For psql commands, add '-c' flag for a single command.
        # If a specific database is required, add '-d' flag.
        psql_cmd = ['psql', '-c', command]
        if db_name:
            psql_cmd = ['psql', '-d', db_name, '-c', command]
        cmd.extend(psql_cmd)
    else:
        # For createdb or other shell commands.
        cmd.extend(command.split())

    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(
            cmd,
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
    Main function to parse arguments and create the PostgreSQL user and database.
    """
    # Check for the correct number of command-line arguments.
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        usage()

    db_user = sys.argv[1]
    db_name = sys.argv[2]
    # Set a default password if not provided.
    db_user_pass = sys.argv[3] if len(sys.argv) == 4 else 'qwer!@34'

    print(f"Creating PostgreSQL database '{db_name}' and user '{db_user}'...")

    # --- PostgreSQL Commands ---
    # Create the database.
    run_pg_command(f"createdb {db_name}")

    # Create the user and set password.
    run_pg_command(
        f"CREATE USER {db_user} WITH PASSWORD '{db_user_pass}';",
        is_sql_command=True
    )

    # Grant all privileges on the new database to the new user.
    run_pg_command(
        f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};",
        is_sql_command=True
    )
    
    # Enable the TimescaleDB extension in the newly created database.
    run_pg_command(
        "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
        is_sql_command=True,
        db_name=db_name
    )

    print(f"\n✅ PostgreSQL User '{db_user}' and database '{db_name}' created successfully.")
    print(f"Connection test command: psql -U {db_user} -d {db_name} -h localhost -p 5432")

if __name__ == "__main__":
    main()

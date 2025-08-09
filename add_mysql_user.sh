#!/bin/bash

# A simple shell script to create a MySQL user and database.
# This script requires sudo privileges to execute MySQL commands.

# Set the script to exit on error
set -e

# Function to display usage information
usage() {
    echo "Usage: $0 <user> <db_name> [password]"
    echo "Example: $0 myuser mydb"
    echo "Example: $0 myuser mydb mypassword123"
}

# Check if the number of arguments is correct
if [ -z "$1" ] || [ -z "$2" ]; then
    usage
    exit 1
fi

# Assign arguments to variables
DB_USER=${1}
DB_NAME=${2}
DB_USER_PASS=${3:-Qwer!@34}

# --- SQL Commands ---
# Create the SQL commands as a single string
# We use a heredoc to pass multiple commands to the mysql client
# -u root: Connect as the root user
# -p: Prompt for the MySQL root password
# -e: Execute the following commands
SQL_COMMANDS="
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_USER_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
"

# Execute the SQL commands with sudo and the mysql client
# The user will be prompted for the system sudo password and then the MySQL root password.
echo "Creating MySQL database '$DB_NAME' and user '$DB_USER'..."
echo "Please enter your system sudo password, then your MySQL root password when prompted."
sudo mysql -u root -p -e "$SQL_COMMANDS"

echo "----------------------------------------------------------"
echo "✅ MySQL User '$DB_USER' and database '$DB_NAME' created successfully."
echo "The password for user '$DB_USER' is: $DB_USER_PASS"
echo "Connection test command: mysql -u $DB_USER -p -h localhost -D $DB_NAME"


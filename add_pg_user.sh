#!/bin/bash

# 1. 사용자 조회
# postgres=# select * from pg_user;
# 2. 사용자 암호 변경
# postgres=# alter user ezsimple password 'qwer!@34';
# psql -U ezsimple -d ezsimple -h localhost -p 5432

usage() {
	echo "add_pg_user.sh user db_name password"
}

if [ -z "$1" ]; then
	usage
	exit -1
fi

set -e

DB_USER=${1}
DB_NAME=${2}
DB_USER_PASS=${3:-Qwer!@34}

sudo su postgres <<EOF
createdb  $DB_NAME;
psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_USER_PASS';"
psql -c "grant all privileges on database $DB_NAME to $DB_USER;"
psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
echo "Postgres User '$DB_USER' and database '$DB_NAME' created."
echo "TimescaleDB activated for database '$DB_NAME'."
EOF

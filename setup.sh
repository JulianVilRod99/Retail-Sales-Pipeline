#!/bin/bash
set -e
pip install -r requirements.txt 
mkdir -p mysql/files postgres/files
docker compose --profile mysql --profile phpmyadmin up -d
docker compose --profile postgres --profile pgadmin up -d

MAX_TRIES=30
COUNTER=0
while ! docker exec mysql_project mysqladmin ping -h "localhost" --silent &> /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "❌ MySQL did not start in time. Exiting."
        exit 1
    fi
    sleep 2
done
echo "✅ MySQL is up and running!"

MAX_TRIES1=30
COUNTER1=0
while ! docker exec postgres_project pg_isready -U admin321 > /dev/null 2>&1; do
    COUNTER1=$((COUNTER+1))
    if [ $COUNTER1 -ge $MAX_TRIES1 ]; then
        echo "❌ PostgreSQL did not start in time. Exiting."
        exit 1
    fi
    sleep 2
done
echo "✅ PostgreSQL is up and running!"

echo "Download the SQL file to configure the database, create it, and load the data into it"
python ./airflow/dags/scripts/mysql_config.py

echo "Load the schema.sql file to create the sales_data table into sales PostgreSQL Database"
python ./airflow/dags/scripts/postgres_config.py

echo "Querying the last rowid for the sales_data table in PostgreSQL and display 
the records of the table sales in MySQL"
python ./airflow/dags/scripts/automation.py
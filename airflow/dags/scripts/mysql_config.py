import requests
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from helpers.db_helper import DatabaseHelper

load_dotenv()


class MySQLConfig:
    def __init__(self):
        self.mysql_helper = DatabaseHelper(db_type='mysql', database=None)
        self.sql_url = os.getenv('MYSQL_SQL_URL')
        self.file_path = os.getenv('MYSQL_FILE_PATH')

    def download_sql_file(self):
        print("📥 Downloading SQL file...")
        response = requests.get(self.sql_url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "wb") as f:
            f.write(response.content)
        print(f"✅ SQL file downloaded: {self.file_path}")

    def execute_sql_commands(self):
        print("🚀 Executing SQL script...")
        with open(self.file_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()
        
        self.mysql_helper.execute_command("DROP DATABASE IF EXISTS sales;")
        self.mysql_helper.execute_command("CREATE DATABASE sales;")
        self.mysql_helper.reconnect_with_database("sales")
        print("✅ Database 'sales' recreated.")
        
        for command in sql_commands.split(";"):
            command = command.strip()
            if command:
                try:
                    self.mysql_helper.execute_command(command)
                except Exception as err:
                    print(f"⚠️ Skipped command due to error: {err}")
        
        print("✅ Database successfully populated!")

    def get_row_count(self):
        query = "SELECT COUNT(*) FROM sales_data;"
        result = self.mysql_helper.execute_query(query)
        row_count = result[0][0] if result else 0
        print(f"📊 Rows imported into sales_data: {row_count}")

    def setup(self):
        self.download_sql_file()
        self.execute_sql_commands()
        self.get_row_count()
        self.mysql_helper.close()


def main():
    config = MySQLConfig()
    config.setup()


if __name__ == "__main__":
    main()


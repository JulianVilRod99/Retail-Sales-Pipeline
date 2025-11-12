import requests
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from helpers.db_helper import DatabaseHelper

load_dotenv()


class PostgreSQLConfig:
    def __init__(self):
        self.postgres_helper = DatabaseHelper(db_type='postgresql')
        self.csv_url = os.getenv('POSTGRES_CSV_URL')
        self.csv_path = os.getenv('POSTGRES_FILE_PATH')

    def download_csv_file(self):
        print("📥 Downloading CSV file...")
        response = requests.get(self.csv_url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        with open(self.csv_path, "wb") as f:
            f.write(response.content)
        print(f"✅ CSV file downloaded: {self.csv_path}")

    def create_table(self):
        sql = """DROP TABLE IF EXISTS sales_data;
CREATE TABLE IF NOT EXISTS sales_data(
    rowid INTEGER PRIMARY KEY NOT NULL,
    product_id INT NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
    quantity INTEGER NOT NULL,
    timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);"""
        self.postgres_helper.execute_command(sql)
        print("Table created")

    def load_csv_data(self):
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            self.postgres_helper.copy_expert("""
                COPY sales_data (rowid, product_id, customer_id, price, quantity, timestamp)
                FROM STDIN WITH CSV HEADER
            """, f)
        print("✅ CSV loaded into sales_data table")

    def get_row_count(self):
        query = "SELECT COUNT(*) FROM sales_data;"
        result = self.postgres_helper.execute_query(query)
        row_count = result[0][0] if result else 0
        print(f"📊 Rows imported: {row_count}")

    def setup(self):
        self.download_csv_file()
        self.create_table()
        self.load_csv_data()
        self.get_row_count()
        self.postgres_helper.close()


def main():
    config = PostgreSQLConfig()
    config.setup()


if __name__ == "__main__":
    main()


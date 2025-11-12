import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from helpers.db_helper import DatabaseHelper

load_dotenv()


class SalesDataSync:
    def __init__(self):
        self.mysql_helper = DatabaseHelper(db_type='mysql')
        self.postgres_helper = DatabaseHelper(db_type='postgresql')

    def get_last_rowid(self):
        query = "SELECT MAX(rowid) FROM sales_data"
        result = self.postgres_helper.execute_query(query)
        return result[0][0] if result and result[0][0] else 0

    def get_latest_records(self, rowid):
        query = "SELECT * FROM sales_data WHERE rowid > %s"
        return self.mysql_helper.execute_query(query, (rowid,))

    def _calculate_default_price(self):
        query = "SELECT product_id, price FROM sales_data WHERE price IS NOT NULL"
        rows = self.postgres_helper.execute_query(query)
        existing_prices = {r[0]: float(r[1]) for r in rows} if rows else {}
        
        if existing_prices:
            return sum(existing_prices.values()) / len(existing_prices)
        return 0.0

    def insert_records(self, records):
        if not records:
            return
        
        existing_prices_query = "SELECT product_id, price FROM sales_data WHERE price IS NOT NULL"
        rows = self.postgres_helper.execute_query(existing_prices_query)
        existing_prices = {r[0]: float(r[1]) for r in rows} if rows else {}
        
        default_price = self._calculate_default_price()
        
        records_to_insert = []
        for r in records:
            rowid = r[0]
            product_id = r[1]
            customer_id = r[2]
            quantity = r[3]
            price = existing_prices.get(product_id, default_price)
            records_to_insert.append((rowid, product_id, customer_id, price, quantity))
        
        insert_sql = """
            INSERT INTO sales_data (rowid, product_id, customer_id, price, quantity)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (rowid) DO NOTHING
        """
        self.postgres_helper.execute_many(insert_sql, records_to_insert)

    def sync(self):
        last_row_id = self.get_last_rowid()
        print(f"Last row id on production datawarehouse = {last_row_id}")
        
        new_records = self.get_latest_records(last_row_id)
        print(f"New rows on staging data warehouse = {len(new_records)}")
        
        self.insert_records(new_records)
        print(f"New rows inserted into production datawarehouse = {len(new_records)}")
        
        self.mysql_helper.close()
        self.postgres_helper.close()


def main():
    syncer = SalesDataSync()
    syncer.sync()


if __name__ == "__main__":
    main()


import mysql.connector
import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class DatabaseHelper:
    def __init__(self, db_type='mysql', database=None):
        self.db_type = db_type.lower()
        self.connection = None
        self.database = database
        self._connect()

    def _connect(self):
        if self.db_type == 'mysql':
            config = {
                'user': os.getenv('MYSQL_USER'),
                'password': os.getenv('MYSQL_PASSWORD'),
                'host': os.getenv('MYSQL_HOST'),
                'port': int(os.getenv('MYSQL_PORT'))
            }
            if self.database or os.getenv('MYSQL_DATABASE'):
                config['database'] = self.database or os.getenv('MYSQL_DATABASE')
            self.connection = mysql.connector.connect(**config)
        elif self.db_type in ('postgresql', 'postgres'):
            self.connection = psycopg2.connect(
                database=self.database or os.getenv('POSTGRES_DATABASE'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                host=os.getenv('POSTGRES_HOST'),
                port=int(os.getenv('POSTGRES_PORT'))
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    @contextmanager
    def _get_cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            if self.db_type == 'mysql':
                cursor.close()

    def reconnect_with_database(self, database):
        self.close()
        self.database = database
        self._connect()

    def execute_query(self, query, params=None):
        with self._get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def execute_command(self, command, params=None):
        with self._get_cursor() as cursor:
            if params:
                cursor.execute(command, params)
            else:
                cursor.execute(command)
        self.connection.commit()

    def execute_many(self, command, params_list):
        with self._get_cursor() as cursor:
            cursor.executemany(command, params_list)
        self.connection.commit()

    def copy_expert(self, sql, file):
        if self.db_type not in ('postgresql', 'postgres'):
            raise NotImplementedError("copy_expert is only available for PostgreSQL")
        with self._get_cursor() as cursor:
            cursor.copy_expert(sql, file)
        self.connection.commit()

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()


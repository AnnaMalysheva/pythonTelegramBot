import os
import logging
import sqlite3


class Database:
    """ Класс работы с базой данных """

    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f"{self.name}.db")
        logging.info("Database created")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE analytics
                          (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                           user_id INTEGER NOT NULL,
                           eventdate VARCHAR(10) NOT NULL);
                          ''')
        cursor.execute('''CREATE TABLE all_analytics
                          (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                           updated_date INTEGER NOT NULL,
                           event_date VARCHAR(30) NOT NULL,
                           event_data TEXT NOT NULL);''')
        connection.commit()
        cursor.close()

    def connection(self):
        db_path = os.path.join(os.getcwd(), f"{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.db")

    def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def insert_analytics(self, user_id: int, date: str):
        insert_query = f"""INSERT INTO analytics (user_id, eventdate)
                           VALUES ({user_id}, "{date}")"""
        self._execute_query(insert_query)
        logging.info(f"Event date for user {user_id} added")

    async def select_analytics(self, user_id: int):
        insert_query = f"""select eventdate from analytics where user_id = {user_id}"""
        record = self._execute_query(insert_query, select=True)
        logging.info(f"Event date for user {user_id} returned")
        return record

    async def delete_analytics(self, user_id: int):
        delete_query = f"""DELETE from analytics
                           where user_id = {user_id}"""
        self._execute_query(delete_query)

        logging.info(f"Event dates for user {user_id} deleted")

    async def insert_all_analytics(self, eventdate: str, eventdata: str):
        insert_query = f"""INSERT INTO all_analytics (updated_date, event_date, event_data)
                           VALUES (strftime('%s','now'), "{eventdate}", "{eventdata}")"""
        self._execute_query(insert_query)
        logging.info(f"Event data added")

database = Database('analytics')

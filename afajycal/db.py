import sqlite3


class DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

    def cursor(self):
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

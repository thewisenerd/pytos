import sqlite3


class Database:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)

    def execute(self, query, data=None, cursor=None, commit=True):
        if data is None:
            data = {}
        if cursor is None:
            cursor = self.conn.cursor()
        cursor.execute(query, data)
        if commit:
            self.conn.commit()

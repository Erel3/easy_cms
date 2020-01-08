import sqlite3


class DBHelper:
    def __init__(self, dbname="db.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (user integer UNIQUE)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, user_id):
        stmt = "INSERT INTO users (user) VALUES (?)"
        args = (user_id, )
        try:
            self.conn.execute(stmt, args)
            self.conn.commit()
        except:
            pass

    def delete_user(self, user_id):
        stmt = "DELETE FROM users WHERE user = (?)"
        args = (user_id, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_users(self):
        stmt = "SELECT user FROM users"
        users = [x[0] for x in self.conn.execute(stmt)]
        return {x[0]: 0 for x in self.conn.execute(stmt)}

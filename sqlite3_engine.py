import sqlite3


# TODO: interface for engines?
class SQLite3Engine():
    """class for executing sql statements"""
    def __init__(self, constr):
        self.conn = sqlite3.connect(constr)


    def execute(self, sql, bind=(), func=None):
        """execute statement"""
        if func is None:
            def func(cursor):
                return cursor.lastrowid

        cur = self.conn.cursor()
        cur.execute(sql, bind)
        self.conn.commit()

        return func(cur)


    def execute_ddl(self, ddl=()):
        cur = self.conn.cursor()
        for stmt in ddl:
            cur.execute(stmt)

        self.conn.commit()



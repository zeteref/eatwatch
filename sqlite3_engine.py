import sqlite3


# TODO: interface for engines?
class SQLite3Engine():
    """class for executing sql statements"""
    def __init__(self, constr):
        self.constr = constr


    def execute(self, sql, bind=(), func=None):
        """execute statement"""
        if func is None:
            def func(cursor):
                return cursor.lastrowid

        with sqlite3.connect(self.constr) as c:
            cur = c.cursor()
            cur.execute(sql, bind)

            return func(cur)


    def execute_ddl(self, ddl=()):
        with sqlite3.connect(self.constr) as c:
            cur = c.cursor()
            for stmt in ddl:
                cur.execute(stmt)

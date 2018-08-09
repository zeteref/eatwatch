import sys
import re
import sqlite3
from datetime import datetime
from functools import namedtuple
from model import *

class InvalidFieldsError(Exception):
    pass


def select_sql(table_name, fields='*'):
    if isinstance(fields, str) and fields != '*':
        raise InvalidFieldsError('Invalid value, fields must be a tuple or str("*")')

    table_name = _table_name(table_name)
    return 'SELECT {} FROM {} WHERE 1 = 1'.format(
            ', '.join(fields),
            table_name)


def insert_sql(table_name, fields):
    table_name = _table_name(table_name)
    return 'INSERT INTO {}({}) VALUES({})'.format(
           table_name, 
           ', '.join(fields), 
           ', '.join('?' * len(fields)))


def delete_sql(table_name, fields=None):
    if fields is None: fields = ('id',)
    table_name = _table_name(table_name)
    return 'DELETE FROM {} WHERE {} = ?'.format(table_name, id_)


class Storage(object):

    def __init__(self, constr):
        self.constr = constr


    def drop_db(self):
        statements = [
                """DROP TABLE meal_ingredients""",
                """DROP TABLE ingredients""",
                """DROP TABLE meals"""
        ]

        with sqlite3.connect(self.constr) as c:
            for stmt in statements:
                try:
                    c.execute(stmt)
                except:
                    pass


    def create_db(self):
        statements = [
                """
                    CREATE TABLE ingredients (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        calories FLOAT DEFAULT 0 NOT NULL,
                        sugar FLOAT DEFAULT 0 NOT NULL,
                        veg_protein FLOAT DEFAULT 0 NOT NULL,
                        protein FLOAT DEFAULT 0 NOT NULL,
                        carbo FLOAT DEFAULT 0 NOT NULL
                    )
                """,
                """
                    CREATE TABLE meals (
                        id INTEGER PRIMARY KEY,
                        date TEXT NOT NULL,
                        name TEXT
                    )
                """,
                """
                    CREATE TABLE meal_ingredients (
                        id INTEGER PRIMARY KEY,
                        ingredient_id INTEGER NOT NULL,
                        meal_id INTEGER NOT NULL,
                        quantity FLOAT NOT NULL,
                        FOREIGN KEY(meal_id) REFERENCES meal(id)
                        FOREIGN KEY(ingredient_id) REFERENCES ingredient(id)
                    )
                """
        ]

        with sqlite3.connect(self.constr) as c:
            for stmt in statements:
                c.execute(stmt)


    def _table_name(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower() + 's'


    def add(self, name, dic):
        with sqlite3.connect(self.constr) as c:
            c.execute(insert_sql(dic.keys()), dic.values())

        return c.lastrowid


    def delete(self, name, id_):
        with sqlite3.connect(self.constr) as c:
            c.execute(delete_sql(name), (id_,))


    def get(self, name, *fields, where=None):
        sql = select_sql(name, ignore=[])

        if not fields: fields= ('*',)

        conditions = [x for x in where if isinstance(x, condition)]
        sql = [sql]

        for cond in conditions:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op, cond.rval))

        sql = '\n'.join(sql)
        with sqliteconn() as con:
            c = con.cursor()
            c.execute(sql, [x.rval for x in conditions])

            return (cls._make(o) for o in c.fetchall())

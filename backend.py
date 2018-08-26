import sys
import re
import sqlite3
from datetime import datetime
from functools import namedtuple
from model import *

class InvalidFieldsError(Exception):
    pass



def _keysvalues(dic):
    items = dic.items()
    kv = namedtuple('keysvalues', ['keys', 'values'])
    return kv(tuple(x[0] for x in items), tuple(x[1] for x in items))


class Storage(object):

    def __init__(self, constr):
        self.constr = constr

    
    def clear_db(self):
        with sqlite3.connect(self.constr) as c:
            c.execute('DELETE FROM meal_ingredients')
            c.execute('DELETE FROM ingredients')
            c.execute('DELETE FROM meals')


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
                        fats FLOAT DEFAULT 0 NOT NULL,
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


    def _execute(self, sql, bind=(), func=None):

        if func is None:
            def func(cursor):
                return cursor.lastrowid

        with sqlite3.connect(self.constr) as c:
            cur = c.cursor()
            cur.execute(sql, bind)

            return func(cur)


    def select(self, table, columns, conds):
        sql = ['SELECT {} FROM {} WHERE 1 = 1'.format(', '.join(columns), table)]
        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op))
        bind = tuple(cond.rval for cond in conds)

        def result(cursor):
            cur_columns = [x[0] for x in cursor.description]         
            return (dict(zip(cur_columns, val)) for val in cursor.fetchall())

        return self._execute('\n'.join(sql), bind, result)


    def insert(self, table, dic):
        columns, bind = _keysvalues(dic)
        sql = 'INSERT INTO {}({}) VALUES({})'.format(table, ', '.join(columns), ', '.join('?' * len(columns)))
    
        return self._execute('\n'.join(sql), bind, lambda x: x.lastrowid)


    def delete(self, table, conds):
        sql = ['DELETE FROM {} WHERE 1 = 1'.format(table)]

        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op, cond.rval))
        bind = tuple(cond.rval for cond in conds)

        self._execute('\n'.join(sql), bind)


    def update(self, table, dic, conds):
        cols, bind = _keysvalues(dic)
        sql = ['UPDATE {} SET {} WHERE 1 = 1'.format(
            table, 
            ', '.join('{} = ?'.format(x) for x in cols))]

        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op))

        bind = bind + tuple(cond.rval for cond in conds)

        return self.execute('\n'.join(sql), bind)

import sys
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import namedtuple
from model import *

class InvalidFieldsError(Exception):
    pass



def _keysvalues(dic):
    items = dic.items()
    kv = namedtuple('keysvalues', ['keys', 'values'])
    return kv(tuple(x[0] for x in items), tuple(x[1] for x in items))

prep = namedtuple('prep_stmt', ['sql', 'bind', 'get_result'])


# TODO: interface?
class SQLite3Engine():
    """class for executing sql statements"""
    def __init__(self, constr):
        self.constr = constr

        if not Path(constr).is_file():
            self.create_db()


    def execute(self, sql, bind=(), func=None):
        """execute statement"""
        if func is None:
            def func(cursor):
                return cursor.lastrowid

        with sqlite3.connect(self.constr) as c:
            cur = c.cursor()
            cur.execute(sql, bind)

            return func(cur)


class Storage(object):

    def __init__(self, engine):
        self.engine = engine

    
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


    def _prep_select(self, table, columns=(), conds=()):
        if not columns:
            columns = ('*',)

        sql = ['SELECT {} FROM {} WHERE 1 = 1'.format(', '.join(columns), table)]
        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op))
        bind = tuple(cond.rval for cond in conds)

        def result(cursor):
            cur_columns = [x[0] for x in cursor.description]         
            return (dict(zip(cur_columns, val)) for val in cursor.fetchall())

        return prep('\n'.join(sql), bind, result)


    def select(self, table, columns, conds):
        return self.engine.execute(*self._prep_select(table, columns, conds))


    def _prep_insert(self, table, dic):
        columns, bind = _keysvalues(dic)
        sql = 'INSERT INTO {}({}) VALUES({})'.format(table, ', '.join(columns), ', '.join('?' * len(columns)))
    
        return prep('\n'.join(sql), bind, lambda x: x.lastrowid)


    def insert(self, table, dic):
        return self.engine.execute(*self_prep_insert(table, dic))


    def _prep_delete(self, table, conds):
        sql = ['DELETE FROM {} WHERE 1 = 1'.format(table)]

        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op, cond.rval))
        bind = tuple(cond.rval for cond in conds)

        return prep('\n'.join(sql), bind)


    def delete(self, table, conds):
        return self.engine.execute(*self._prep_delete(table, conds))


    def _prep_update(self, table, dic, conds):
        cols, bind = _keysvalues(dic)
        sql = ['UPDATE {} SET {} WHERE 1 = 1'.format(
            table, 
            ', '.join('{} = ?'.format(x) for x in cols))]

        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op))

        bind = bind + tuple(cond.rval for cond in conds)

        return prep('\n'.join(sql), bind, None)


    def update(self, table, dic, conds):
        return self.engine.execute(*self._prep_update(table, dic, conds))

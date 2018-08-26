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


class SQLStorage(object):
    """
    class to construct sql statements for basic operations, 
    relays on Engine to actually execute them
    """

    def __init__(self, engine):
        self.engine = engine

    
    def execute_ddl(self, ddl=()):
        self.engine.execute_ddl(ddl)


    def _prep_select(self, table, columns=(), conds=()):
        if not columns:
            columns = ('*',)

        sql = ['SELECT {} FROM {} WHERE 1 = 1'.format(', '.join(columns), table)]
        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op))
        bind = tuple(cond.rval for cond in conds)

        def get_result(cursor):
            cur_columns = [x[0] for x in cursor.description]         
            return [dict(zip(cur_columns, val)) for val in cursor.fetchall()]

        return prep('\n'.join(sql), bind, get_result)


    def select(self, table, columns=(), conds=()):
        return self.engine.execute(*self._prep_select(table, columns, conds))


    def _prep_insert(self, table, dic):
        columns, bind = _keysvalues(dic)
        sql = ['INSERT INTO {}({}) VALUES({})'.format(table, ', '.join(columns), ', '.join('?' * len(columns)))]
    
        return prep('\n'.join(sql), bind, lambda x: x.lastrowid)


    def insert(self, table, dic):
        return self.engine.execute(*self._prep_insert(table, dic))


    def _prep_delete(self, table, conds):
        sql = ['DELETE FROM {} WHERE 1 = 1'.format(table)]

        for cond in conds:
            sql.append('AND {} {} ?'.format(cond.lval, cond.op, cond.rval))
        bind = tuple(cond.rval for cond in conds)

        return prep('\n'.join(sql), bind, None)


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

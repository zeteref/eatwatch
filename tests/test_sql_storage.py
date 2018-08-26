import sys
import unittest

sys.path.append('../')

from sql_storage import SQLStorage
from sqlite3_engine import SQLite3MemoryEngine
from conditions import *


class TestPrepareStmts(unittest.TestCase):

    def setUp(self):
        self.stg = SQLStorage(None) # engine not used, just create statements


    def test_simple_update(self):
        test = self.stg._prep_update('mytable', {'uno':1, 'due':2, 'tre':3}, where(eq('id', 1), like('name', '%test%')))

        self.assertEqual(test.sql, 'UPDATE mytable SET uno = ?, due = ?, tre = ? WHERE 1 = 1\nAND id = ?\nAND name like ?')
        self.assertEqual(test.bind, (1, 2, 3, 1, '%test%'))


    def test_simple_select(self):
        test = self.stg._prep_select('mytable', ('uno', 'due'), where(eq('id', 1), neq('name', 'test')))
        self.assertEqual(test.sql, 'SELECT uno, due FROM mytable WHERE 1 = 1\nAND id = ?\nAND name != ?')
        self.assertEqual(test.bind, (1, 'test'))

        test = self.stg._prep_select('mytable')
        self.assertEqual(test.sql, 'SELECT * FROM mytable WHERE 1 = 1')
        self.assertEqual(test.bind, ())


    def test_simple_insert(self):
        test = self.stg._prep_insert('mytable', {'uno':1, 'due':2})
        self.assertEqual(test.sql, 'INSERT INTO mytable(uno, due) VALUES(?, ?)')
        self.assertEqual(test.bind, (1, 2))


    def test_simple_delete(self):
        test = self.stg._prep_delete('mytable', where(eq('id', 1)))
        self.assertEqual(test.bind, (1,))
        self.assertEqual(test.sql, 'DELETE FROM mytable WHERE 1 = 1\nAND id = ?')


class DummyEngine():
    """do not use real db engine"""

    def execute(self, sql, bind=(), func=None):
        """emulate executing statement - return sql and bindings"""
        return (sql, bind)


class TestStmtExcecutionWithDummyEngine(unittest.TestCase):

    def setUp(self):
        self.stg = SQLStorage(DummyEngine())


    def test_simple_select(self):
        test = self.stg.select('mytable', ('uno', 'due'), where(eq('id', 1), neq('name', 'test')))
        self.assertEqual(test[0], 'SELECT uno, due FROM mytable WHERE 1 = 1\nAND id = ?\nAND name != ?')
        self.assertEqual(test[1], (1, 'test'))

        test = self.stg.select('mytable')
        self.assertEqual(test[0], 'SELECT * FROM mytable WHERE 1 = 1')
        self.assertEqual(test[1], ())


    def test_simple_update(self):
        test = self.stg.update('mytable', {'uno':1, 'due':2, 'tre':3}, where(eq('id', 1), like('name', '%test%')))
        self.assertEqual(test[0], 'UPDATE mytable SET uno = ?, due = ?, tre = ? WHERE 1 = 1\nAND id = ?\nAND name like ?')
        self.assertEqual(test[1], (1, 2, 3, 1, '%test%'))


    def test_simple_insert(self):
        test = self.stg.insert('mytable', {'uno':1, 'due':2})
        self.assertEqual(test[0], 'INSERT INTO mytable(uno, due) VALUES(?, ?)')
        self.assertEqual(test[1], (1, 2))


    def test_simple_delete(self):
        test = self.stg.delete('mytable', where(eq('id', 1)))
        self.assertEqual(test[0], 'DELETE FROM mytable WHERE 1 = 1\nAND id = ?')
        self.assertEqual(test[1], (1,))


class TestStmtExcecutionWithInMemoryEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stg = SQLStorage(SQLite3MemoryEngine())


    def setUp(self):
        self.stg.execute_ddl(('create table mytable(id integer primary key, uno, due, tre)',))


    def tearDown(self):
        self.stg.execute_ddl(('drop table mytable',))


    def test_simple_insert_select(self):
        id_ = self.stg.insert('mytable', {'uno': 1})
        ret = self.stg.select('mytable')

        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0], {'id': 1, 'uno': 1, 'due': None, 'tre': None})


    def test_simple_insert_update(self):
        id_ = self.stg.insert('mytable', {'uno': 1})
        test = self.stg.select('mytable')
        self.assertEqual(len(test), 1)
        self.assertEqual(test[0], {'id': 1, 'uno': 1, 'due': None, 'tre': None})

        self.stg.update('mytable', {'due': 2}, where(eq('id', id_)))
        test = self.stg.select('mytable')
        self.assertEqual(len(test), 1)
        self.assertEqual(test[0], {'id': 1, 'uno': 1, 'due': 2, 'tre': None})


        self.stg.update('mytable', {'tre': 3}, where(eq('due', 2)))
        test = self.stg.select('mytable')
        self.assertEqual(len(test), 1)
        self.assertEqual(test[0], {'id': 1, 'uno': 1, 'due': 2, 'tre': 3})


    def test_simple_insert_delete(self):
        id_ = self.stg.insert('mytable', {'uno': 1, 'tre':3})
        test = self.stg.select('mytable')
        self.assertEqual(len(test), 1)
        self.assertEqual(test[0], {'id': 1, 'uno': 1, 'due': None, 'tre': 3})

        self.stg.delete('mytable', where(eq('uno', 1), eq('tre', 3)))
        test = self.stg.select('mytable')
        self.assertEqual(len(test), 0)

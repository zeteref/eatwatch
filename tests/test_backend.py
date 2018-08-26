import sys
import unittest

sys.path.append('../')

import backend
from conditions import *


class TestPrepareStmts(unittest.TestCase):

    class 

    def setUp(self):
        self.stg = backend.Storage('')

    def test_simple_update(self):
        stg = backend.Storage()
        test = stg._prep_update('mytable', {'uno':1, 'due':2, 'tre':3}, (eq('id', 1), like('name', '%test%')))

        self.assertEqual(test.sql, 'UPDATE mytable SET uno = ?, due = ?, tre = ? WHERE 1 = 1\nAND id = ?\nAND name like ?')
        self.assertEqual(test.bind, (1, 2, 3, 1, '%test%'))


    def test_simple_select(self):
        stg = backend.Storage('')
        stg._prep_select('mytable', ('uno', 'due'), (eq('id', 1), neq('name', 'test')))

        self.assertEqual(test.sql, 'SELECT uno, due FROM mytable WHERE 1 = 1\nAND id = ?\nAND name != ?')
        self.assertEqual(test.bind, (1, 'test'))

        test = self.stg._prep_select('mytable')
        self.assertEqual(test.sql, 'SELECT * FROM mytable WHERE 1 = 1')
        self.assertEqual(test.bind, ())


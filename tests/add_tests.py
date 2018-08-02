import unittest
import sys
sys.path.append('../')

from main import add_ingredient, ingredient, create_db, drop_db

class Test(unittest.TestCase):

    dbname = 'example.db'

    @classmethod
    def setUpClass(cls):
        drop_db(cls.dbname)
        create_db(cls.dbname)


    @classmethod
    def tearDownClass(cls):
        drop_db(cls.dbname)


    def test_add_ingredient(self):
        test = add_ingredient(ingredient('test', 
                                         calories='1',
                                         sugar='2',
                                         veg_protein=3,
                                         protein=4,
                                         carbo='5'))
        print(test)

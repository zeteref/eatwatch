import unittest
import sys
sys.path.append('../')

from main import add_ingredient, ingredient, create_db, drop_db, get_ingredients, condition

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
        add = add_ingredient(ingredient('test', 
                                        calories='1',
                                        sugar='2',
                                        veg_protein=3,
                                        protein=4,
                                        carbo='5'))
        c = condition
        test = next(get_ingredients(c('id', '=', add.id)), None)
        self.assertEqual(test.id, add.id)

        self.assertEqual(test.calories, 1)
        self.assertEqual(test.sugar, 2)
        self.assertEqual(test.veg_protein, 3)
        self.assertEqual(test.protein, 4)
        self.assertEqual(test.carbo, 5)

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
        self.assertEquals(test.id, add.id)

        self.assertEquals(test.calories, 1)
        self.assertEquals(test.sugar, 2)
        self.assertEquals(test.veg_protein, 3)
        self.assertEquals(test.protein, 4)
        self.assertEquals(test.carbo, 5)

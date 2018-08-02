import sys
import sqlite3
from datetime import datetime
from marshmallow import Schema, fields, pprint
from functools import namedtuple

class IngredientSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    calories = fields.Int()
    sugar = fields.Int()
    veg_protein = fields.Int()
    protein = fields.Int()
    carbo = fields.Int()


class MealSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    date = fields.Date()


class MealIngredientSchema(Schema):
    id = fields.Int()
    meal_id = fields.Int()
    ingredient_id = fields.Int()
    quantity = fields.Float()


condition = namedtuple('condition', ('op', 'val'))
def get_conditions(obj):
    return [x for x in obj._asdict() if isinstance(x, condition)]


Ingredient = namedtuple('Ingredient', IngredientSchema._declared_fields.keys())
def ingredient(name=None, **kwds):
    templ = Ingredient(None, name, 0, 0, 0, 0, 0)
    return templ._replace(**kwds)


def meal(name, date=datetime.now()):
    Meal = namedtuple('Meal', MealSchema._declared_fields.keys())
    return Meal(None, name, date)


def meal_ingredient(name, meal_id, ingr_id, quantity): 
    MealIngredient = namedtuple('MealIngredient', MealIngredientSchema._declared_fields.keys())
    return MealIngredient(None, meal_id, ingr_id, quantity)


def _table_name(name, cls):
    return name if name is not None else cls.__name__.replace('Schema', '').lower()


def prepare_stmt(cls, table_name=None, ignore=None):
    ignore = ignore if ignore is not None else ['id']
    fields = [x for x in cls._declared_fields.keys() if x not in ignore]
    name = _table_name(table_name, cls)

    return namedtuple('stmt_components', ('fields', 'table_name'))._make(
            (fields, name))


def select_sql(cls, table_name=None, ignore=None):
    prep = prepare_stmt(cls, table_name, ignore)

    return 'SELECT {} FROM {} WHERE 1 = 1'.format(
            ', '.join(prep.fields),
            prep.table_name)


def insert_sql(cls, table_name=None, ignore=None):
    prep = prepare_stmt(cls, table_name, ignore)

    return 'INSERT INTO {}({}) VALUES({})'.format(
           prep.table_name, 
           ', '.join(prep.fields), 
           ', '.join('?' * len(prep.fields)))


class sqliteconn():

    def __init__(self, fname='example.db'):
        self.fname = fname


    def __enter__(self):
        self.connection = sqlite3.connect(self.fname)
        return self.connection


    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.commit()
        self.connection.close()


def drop_db(fname):
    statements = [
            """DROP TABLE meal_ingredients""",
            """DROP TABLE ingredient""",
            """DROP TABLE meal"""
    ]

    with sqliteconn(fname) as con:
        c = con.cursor()
        for stmt in statements:
            try:
                c.execute(stmt)
            except:
                pass


def create_db(fname):
    statements = [
            """
                CREATE TABLE ingredient(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    calories INTEGER NOT NULL,
                    sugar INTEGER NOT NULL,
                    veg_protein INTEGER NOT NULL,
                    protein INTEGER NOT NULL,
                    carbo INTEGER NOT NULL
                )
            """,
            """
                CREATE TABLE meal(
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    name TEXT
                )
            """,
            """
                CREATE TABLE meal_ingredients(
                    id INTEGER PRIMARY KEY,
                    ingredient_id INTEGER NOT NULL,
                    meal_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY(meal_id) REFERENCES meal(id)
                    FOREIGN KEY(ingredient_id) REFERENCES ingredient(id)
                )
            """
    ]

    with sqliteconn(fname) as conn:
        c = conn.cursor()
        for stmt in statements:
            c.execute(stmt)


def add_object(obj, Schema):
    with sqliteconn() as con:
        c = con.cursor()
        c.execute(insert_sql(Schema), obj[1:])

    return obj._replace(id=c.lastrowid)


def get_object(obj, Schema):
    sql = select_sql(Schema, ignore=[])

    conditions = []
    for cond in get_conditions(obj):
        conditions.append('AND {} {} {}'.format(cond.lval, cond.op, cond.rval))

    sql = '\n'.join([sql] + conditions)


    with sqliteconn() as con:
        c = con.cursor()
        c.execute(select_sql(Schema, ignore=[]))

        return [Ingredient._make(o) for o in c.fetchall()]


def add_ingredient(ingredient):
    return add_object(ingredient, IngredientSchema)


def get_ingredient(ingredient=None):
    return get_object(ingredient, IngredientSchema)


def add_meal(meal):
    return add_object(meal, MealSchema)


def get_meal(meal=None):
    return get_object(meal, MealSchema)


def add_meal_ingredient(meal_ingredient):
    return add_object(meal_ingredient, MealIngredientSchema)


def get_meal_ingredient(meal_ingredient=None):
    return get_object(meal_ingredient, MealIngredientSchema)


def __main__():
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        dbname = sys.argv[2] if len(sys.argv) > 2 else 'example.db'

        drop_db(dbname)
        create_db(dbname)


if __name__ == '__main__':
    __main__()

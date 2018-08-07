import sys
import re
import sqlite3
from datetime import datetime
from marshmallow import Schema, fields, pprint, post_load
from functools import namedtuple

condition = namedtuple('condition', ('lval', 'op', 'rval'))

class IngredientSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    calories = fields.Int()
    sugar = fields.Int()
    veg_protein = fields.Int()
    protein = fields.Int()
    carbo = fields.Int()


    @post_load
    def make(self, data):
        return ingredient(**data)


    class Meta:
        ordered = True


class MealSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    date = fields.DateTime(format='%Y-%m-%d %H:%M', default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))


    @post_load
    def make(self, data):
        return meal(**data)


    class Meta:
        ordered = True


class MealIngredientSchema(Schema):
    id = fields.Int()
    meal_id = fields.Int()
    ingredient_id = fields.Int()
    quantity = fields.Float()

    @post_load
    def make(self, data):
        return meal_ingredient(**data)


    class Meta:
        ordered = True


Ingredient = namedtuple('Ingredient', IngredientSchema._declared_fields.keys())
def ingredient(name=None, **kwds):
    templ = Ingredient(None, name, 0, 0, 0, 0, 0)
    return templ._replace(**kwds)


Meal = namedtuple('Meal', MealSchema._declared_fields.keys())
def meal(name, date=datetime.now()):
    return Meal(None, name, date)


MealIngredient = namedtuple('MealIngredient', MealIngredientSchema._declared_fields.keys())
def meal_ingredient(meal_id, ingredient_id, quantity): 
    return MealIngredient(None, meal_id, ingredient_id, quantity)


def _table_name(name, cls):
    name = name if name is not None else cls.__name__.replace('Schema', '')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower() + 's'


def prepare_stmt(cls, table_name=None, ignore=None):
    ignore = ignore if ignore is not None else ['id']
    fields = cls._fields if hasattr(cls, '_fields') else cls._declared_fields.keys()
    fields = [x for x in fields if x not in ignore]
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


def delete_sql(cls, table_name=None, id_='id'):
    table_name = _table_name(table_name, cls)
    return 'DELETE FROM {} WHERE {} = ?'.format(table_name, id_)


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
            """DROP TABLE ingredients""",
            """DROP TABLE meals"""
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
                CREATE TABLE ingredients (
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

    with sqliteconn(fname) as conn:
        c = conn.cursor()
        for stmt in statements:
            c.execute(stmt)


def add_object(obj, cls=None):
    cls = obj.__class__ if cls is None else cls 

    with sqliteconn() as con:
        c = con.cursor()
        c.execute(insert_sql(cls), obj[1:])

    return obj._replace(id=c.lastrowid)


def delete_object(obj, cls=None):
    cls = obj.__class__ if cls is None else cls 

    with sqliteconn() as con:
        c = con.cursor()
        c.execute(delete_sql(cls), (obj.id,))


def get_objects(cls, *args):
    sql = select_sql(cls, ignore=[])

    conditions = [x for x in args if isinstance(x, condition)]
    sql = [sql]

    for cond in conditions:
        sql.append('AND {} {} ?'.format(cond.lval, cond.op, cond.rval))

    sql = '\n'.join(sql)
    with sqliteconn() as con:
        c = con.cursor()
        c.execute(sql, [x.rval for x in conditions])

        return (cls._make(o) for o in c.fetchall())


def add_ingredient(ingredient):
    return add_object(ingredient)


def delete_ingredient(ingredient):
    return delete_object(ingredient)


def get_ingredients(*args):
    return get_objects(Ingredient, *args)


def add_meal(meal):
    return add_object(meal)


def delete_meal(meal):
    return delete_object(meal)


def get_meals(*args):
    return get_objects(Meal, *args)


def add_meal_ingredient(meal_ingredient):
    return add_object(meal_ingredient)


def delete_meal_ingredient(meal_ingredient):
    return delete_object(meal_ingredient)


def get_meal_ingredients(*args):
    return get_objects(MealIngredient, *args)


def __main__():
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        dbname = sys.argv[2] if len(sys.argv) > 2 else 'example.db'

        drop_db(dbname)
        create_db(dbname)


if __name__ == '__main__':
    __main__()

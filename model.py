from marshmallow import Schema, post_load, fields


class Meta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super(Meta, mcs).__new__(mcs, name, bases, namespace, **kwargs)
        user_init = new_cls.__init__
        def __init__(self, *args, **kwargs):
            print("New __init__ called")
            user_init(self, *args, **kwargs)
            self.extra()
        print("Replacing __init__")
        setattr(new_cls, '__init__', __init__)

        return new_cls


class JsonObject(metaclass=Meta):
    pass


class A(JsonObject):
    def __init__(self):
        print('hello world')


a = A()


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


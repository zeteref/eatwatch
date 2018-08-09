from meta import JsonObject, fields

class Ingredient(JsonObject):
    id = fields.Int()
    name = fields.Str()
    calories = fields.Float()
    sugar = fields.Float()
    veg_protein = fields.Float()
    protein = fields.Float()
    carbo = fields.Float()

    class Meta:
        ordered = True


class Meal(JsonObject):
    id = fields.Int()
    name = fields.Str()
    date = fields.DateTime(
            format='%Y-%m-%d %H:%M', 
            default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    class Meta:
        ordered = True


class MealIngredient(JsonObject):
    id = fields.Int()
    meal_id = fields.Int()
    ingredient_id = fields.Int()
    quantity = fields.Float()

    class Meta:
        ordered = True

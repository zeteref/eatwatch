import cherrypy

from controllers import MealsController

def init(disp: cherrypy.dispatch.RoutesDispatcher):
    read_c = dict(method=["GET", "HEAD"])
    update_c = dict(method=["PUT","POST"])
    delete_c = dict(method=["DELETE"])

    ctrl = MealsController()

    # GET
    disp.connect(name='get_meals', route='/meals', action='get_meals', controller=ctr, conditions=read_c)
    disp.connect(name='get_meals_ingredients', route='/meals/{meal_id}/ingredients', action='get_meal_ingredients', controller=ctr, conditions=read_c)
    disp.connect(name='get_meal', route='/meals/{id}', action='get_meal', controller=ctr, conditions=read_c)

    disp.connect(name='get_ingredients', route='/ingredients', action='get_ingredients', controller=ctr, conditions=read_c)
    disp.connect(name='get_ingredient', route='/ingredients/{id}', action='get_ingredient', controller=ctr, conditions=read_c)

    disp.connect(name='search', route='/search', action='search', controller=ctr, conditions=read_c)

    # POST
    disp.connect(name='meals', route='/meals', action='add_meal', controller=ctr, conditions=update_c)
    disp.connect(name='ingredients', route='/ingredients', action='add_ingredient', controller=ctr, conditions=update_c)

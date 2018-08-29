import cherrypy

from controllers import MealsController

def init(disp: cherrypy.dispatch.RoutesDispatcher):
    get_c = dict(method=["GET", "HEAD"])
    put_c = dict(method=["PUT"])
    post_c = dict(method=["POST"])
    delete_c = dict(method=["DELETE"])

    ctrl = MealsController()

    # GET
    disp.connect(name='get_meals', route='/meals', action='get_meals', controller=ctrl, conditions=get_c)
    disp.connect(name='get_meals_ingredients', route='/meals/{meal_id}/ingredients', action='get_meal_ingredients', controller=ctrl, conditions=get_c)
    disp.connect(name='get_meal', route='/meals/{id}', action='get_meal', controller=ctrl, conditions=get_c)

    disp.connect(name='get_ingredients', route='/ingredients', action='get_ingredients', controller=ctrl, conditions=get_c)
    disp.connect(name='get_ingredient', route='/ingredients/{id}', action='get_ingredient', controller=ctrl, conditions=get_c)

    disp.connect(name='search', route='/search', action='search', controller=ctrl, conditions=get_c )

    # POST
    disp.connect(name='meals', route='/meals', action='add_meal', controller=ctrl, conditions=post_c)
    disp.connect(name='add_ingredient', route='/ingredients', action='add_ingredient', controller=ctrl, conditions=post_c)

    # PUT
    disp.connect(name='update_ingredient', route='/ingredients', action='update_ingredient', controller=ctrl, conditions=put_c)

    # DELETE
    disp.connect(name='delete_ingredient', route='/ingredients/{id}', action='delete_ingredient', controller=ctrl, conditions=delete_c)

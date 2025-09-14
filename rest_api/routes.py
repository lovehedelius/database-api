from bottle import request
from . import services

# Defines all API endpoints
def setup_routes(app):

    # Returns 'pong' to check if the server is running
    @app.route('/ping', method="GET")
    def ping():
        return "pong"
    
    # Removes all data from the database
    @app.route('/reset', method="POST")
    def reset_database():
        return services.reset_database()

    # Adds a new customer
    @app.route('/customers', method="POST")
    def add_customer():
        customer = request.json
        return services.add_customer(customer)

    # Returns the names and addresses of all customers
    @app.route('/customers', method="GET")
    def get_customers():
        return services.get_customers()

    # Adds a new ingredient
    @app.route('/ingredients', method="POST")
    def add_ingredient():
        ingredient = request.json
        return services.add_ingredient(ingredient)

    # Updates the stock of an ingredient after a delivery
    @app.route('/ingredients/<ingredient>/deliveries', method="POST")
    def update_ingredient(ingredient):
        delivery = request.json
        return services.update_ingredient(ingredient, delivery)
    
    # Returns the name and current stock of all ingredients
    @app.route('/ingredients', method="GET")
    def get_ingredients():
        return services.get_ingredients()
    
    # Adds the name and recipe of a new cookie
    @app.route('/cookies', method="POST")
    def add_cookie():
        cookie = request.json
        return services.add_cookie(cookie)

    # Returns the name and number of unblocked pallets for each cookie type
    @app.route('/cookies', method="GET")
    def get_cookies():
        return services.get_cookies()

    # Returns the recipe of a given cookie, or status code 404 if there is no such cookie
    @app.route('/cookies/<cookie_name>/recipe', method="GET")
    def get_recipe(cookie_name):
        return services.get_recipe(cookie_name)

    # Adds a new pallet if there are enough ingredients, otherwise returns status code 422
    @app.route('/pallets', method="POST")
    def add_pallet():
        pallet = request.json
        return services.add_pallet(pallet)

    # Returns the ID, cookie type, production date and blockage status of all pallets satisfying the given criteria
    @app.route('/pallets', method="GET")
    def get_pallets():
        cookie = request.query.get("cookie")
        after = request.query.get("after")
        before = request.query.get("before")
        return services.get_pallets(cookie, after, before)
    
    # Blocks all pallets of a given produced produced during a given interval time
    @app.route('/cookies/<cookie_name>/block', method="POST")
    def block_pallets(cookie_name):
        after = request.query.get("after")
        before = request.query.get("before")
        return services.block_pallets(cookie_name, after, before)

    # Unblocks all pallets of a given produced produced during a given interval time
    @app.route('/cookies/<cookie_name>/unblock', method="POST")
    def unblock_pallets(cookie_name):
        after = request.query.get("after")
        before = request.query.get("before")
        return services.unblock_pallets(cookie_name, after, before)

    # Creates a new order, or returns status code 404 if the customer or any of the ordered cookies don't exist
    @app.route('/orders', method="POST")
    def create_order():
        order = request.json
        return services.create_order(order)



    
    
    
    
    
    
    
    
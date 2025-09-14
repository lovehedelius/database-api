# Services.py (Business logic, Consistent Layered Approach)
# Handles logic before calling database functions
from . import database
from bottle import response

def reset_database():
    return database.reset_database()

# Checks if name or address are missing from the body before continuing
def add_customer(customer):
    name = customer.get("name")
    address = customer.get("address")
    if not name or not address:
        response.status = 400
        return "Missing fields"
    return database.add_customer(name, address)

def get_customers():
    return database.get_customers()

# Checks if name or unit are missing from the body before continuing
def add_ingredient(ingredient):
    name = ingredient.get("ingredient")
    unit = ingredient.get("unit")
    if not name or not unit:
        response.status = 400
        return "Missing fields"
    return database.add_ingredient(name, unit)

def get_ingredients():
    return database.get_ingredients()

# Checks if delivery time or quantity are missing from the body before continuing
def update_ingredient(ingredient, delivery):
    delivery_time = delivery.get("deliveryTime")
    quantity = delivery.get("quantity")
    if not delivery_time or not quantity:
        response.status = 400
        return "Missing fields"
    return database.update_ingredient(ingredient, delivery_time, quantity)

# Checks if name or recipe are missing from the body and unpacks contents of recipe
def add_cookie(cookie):
    name = cookie.get("name")
    recipe = cookie.get("recipe")
    if not name or not recipe or len(recipe) < 1:
        response.status = 400
        return "Missing fields"
    ingredients = [(ingredient["ingredient"], ingredient["amount"]) for ingredient in recipe]
    return database.add_cookie(name, ingredients)

def get_cookies():
    return database.get_cookies()

def get_recipe(cookie_name):
    return database.get_recipe(cookie_name)

# Checks if cookie type is missing from the body before continuing
def add_pallet(pallet):
    cookie = pallet.get("cookie")
    if not cookie:
        response.status = 400
        return "Missing fields"
    return database.add_pallet(cookie)

def get_pallets(cookie, after, before):
    return database.get_pallets(cookie, after, before)

def block_pallets(cookie, after, before):
    return database.block_pallets(cookie, after, before)

def unblock_pallets(cookie, after, before):
    return database.unblock_pallets(cookie, after, before)

# Checks if customer, delivery date or cookie type are missing from the body and unpacks contents of order
def create_order(order):
    customer = order.get("customer")
    delivery_date = order.get("deliveryDate")
    cookies = order.get("cookies")
    if not customer or not delivery_date or not cookies:
        response.status = 400
        return "Missing fields"
    ordered_cookies = [(cookie["cookie"], cookie["count"]) for cookie in cookies]
    return database.create_order(customer, delivery_date, ordered_cookies)

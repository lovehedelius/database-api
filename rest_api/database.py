# database.py (Database Connection & Queries)
# Handling all raw SQL queries and database connections
import sqlite3
from bottle import response
from .config import DB_PATH
from urllib.parse import quote, unquote

# Establishes and returns a database connection
def _get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

# Closes the database connection
def _close_db_connection(cursor, conn):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Rolls back the changes and returns error message in case of error
def _server_error(conn, e):
    conn.rollback()
    response.status = 500
    return f"Database error: {str(e)}"

# Finds the names of the tables in the database and empties them
def reset_database():
    conn, cursor = _get_db_connection()

    # Fetch the name of the tables, excluding system tables
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        """
    )
    tables = cursor.fetchall()

    # Deletes all rows from the found tables
    for table in tables:
        cursor.execute(f"DELETE FROM {table[0]}")
    conn.commit()
    
    _close_db_connection(cursor, conn)
    response.status = 205
    return {"location": "/"}

# Inserts a new customer in the database
def add_customer(name, address):
    conn, cursor = _get_db_connection()

    try:
        # Insert a customer with the given name and address
        cursor.execute(
            """
            INSERT INTO customers
            VALUES (?, ?)
            """, [name, address]
        )
        conn.commit() 
        response.status = 201
        return {"location": f"/customers/{quote(name)}"}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Returns all customers
def get_customers():
    conn, cursor = _get_db_connection()

    try:
        # Fetch name and address of all customers
        cursor.execute(
            """
            SELECT customer_name, address
            FROM customers
            """
        )
        customers = [{"name": customer_name, "address": address} for customer_name, address in cursor]
        response.status = 200
        return {"data": customers}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Inserts a new ingredient in the database
def add_ingredient(name, unit):
    conn, cursor = _get_db_connection()

    try:
        # Insert an ingredient with the given name and unit
        cursor.execute(
            """
            INSERT INTO ingredients
            VALUES (?, ?)
            """, [name, unit]
        )
        conn.commit()
        response.status = 201
        return {"location": f"/ingredients/{quote(name)}"}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Returns all ingredients and their stock
def get_ingredients():
    conn, cursor = _get_db_connection()

    try:
        # For each ingredient, fetch the name, the sum of all inventory update changes and the unit
        cursor.execute(
            """
            SELECT ingredient_name, COALESCE(SUM(change), 0) AS inventory, unit
            FROM ingredients
                JOIN inventory_updates USING(ingredient_name)
            GROUP BY ingredient_name
            """
        )
        ingredients = [{"ingredient": ingredient_name, "quantity": inventory, "unit": unit} for ingredient_name, inventory, unit in cursor]
        response.status = 200
        return {"data": ingredients}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Increases the stock of an ingredient and logs the delivery time
def update_ingredient(ingredient, delivery_time, quantity):
    conn, cursor = _get_db_connection()

    try:
        # Insert an update for the given ingredient and with the given quantity and time
        cursor.execute(
            """
            INSERT INTO inventory_updates(ingredient_name, change, timestamp)
            VALUES (?, ?, ?)
            """, [ingredient, quantity, delivery_time]
        )
        conn.commit()

        # Fetch the sum of update changes and unit for the ingredient which was just updated
        cursor.execute(
            """
            SELECT SUM(change) AS inventory, unit
            FROM inventory_updates
                JOIN ingredients USING(ingredient_name)
            WHERE ingredient_name = ?
            """, [ingredient]
        )
        inventory, unit = cursor.fetchone()
        
        response.status = 201
        return {"data": {"ingredient": ingredient, "quantity": inventory, "unit": unit}}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Inserts a new cookie and its recipe in the database 
def add_cookie(name, ingredients):
    conn, cursor = _get_db_connection()

    try:
        # Insert a cookie with the given name
        cursor.execute(
            """
            INSERT INTO cookies
            VALUES (?)
            """, [name]
        )

        # Insert the name and amount for all the cookie's ingredients
        for ingredient_name, amount in ingredients:
            cursor.execute(
                """
                INSERT INTO ingredient_usages(cookie_name, ingredient_name, amount)
                VALUES (?, ?, ?)
                """, [name, ingredient_name, amount]
            )
        conn.commit()
        
        response.status = 201
        return {"location": f"/cookies/{quote(name)}"}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)
    

# Returns the name and number of unblocked pallets of a cookie
def get_cookies():
    conn, cursor = _get_db_connection()

    try:
        # For each cookie, fetch the name and number of pallets that are not present in the subquery,
        # which contains the pallets of that cookie produced while the cookie was blocked
        cursor.execute(
            """
            SELECT cookie_name, COALESCE(COUNT(pallet_id), 0)
            FROM cookies
            LEFT JOIN pallets USING(cookie_name)
            WHERE pallet_id NOT IN (
                SELECT pallet_id
                FROM pallets
                    JOIN cookies USING(cookie_name)
                    JOIN blockages USING(cookie_name)
                WHERE timestamp > start_time 
                AND timestamp < end_time)
            GROUP BY cookie_name
            """
        )
        cookies = [{"name": cookie_name, "pallets": unblocked_pallets} for cookie_name, unblocked_pallets in cursor]
        response.status = 200
        return {"data": cookies}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Returns the recipe for a cookie
def get_recipe(cookie_name):
    conn, cursor = _get_db_connection()

    try:
        # Fetch the name, amount and unit of all ingredients that the given cookie uses
        cursor.execute(
            """
            SELECT ingredient_name, amount, unit
            FROM ingredient_usages
                JOIN ingredients USING (ingredient_name)
            WHERE cookie_name = ?
            """, [cookie_name]
        )
        recipe = [{"ingredient": ingredient_name, "amount": amount, "unit": unit} for ingredient_name, amount, unit in cursor]
        
        # Check if the query returned any rows
        if len(recipe) == 0:
            response.status = 404
        else:
            response.status = 200
        return {"data": recipe}
    
    except Exception as e:
        return _server_error(conn, e)

    finally:
        _close_db_connection(cursor, conn)

# Inserts a new pallet in the database
def add_pallet(cookie):
    conn, cursor = _get_db_connection()

    try:
        # Insert a pallet with the given cookie and the current time, and return its randomly assigned ID
        cursor.execute(
            """
            INSERT INTO pallets(cookie_name, timestamp)
            VALUES (?, current_timestamp)
            RETURNING pallet_id
            """, [cookie]
        )
        pallet_id = cursor.fetchone()

        # Commit and return success only if a pallet was created
        if pallet_id:
            conn.commit()
            response.status = 201
            return {"location": f"/pallets/{pallet_id[0]}"}

    except Exception as e:
        # Return the appropriate response and status if the database error was caused by the trigger which checks 
        # if the ingredients are enough
        if str(e) == "There are not enough ingredients to bake this pallet":
            conn.rollback()
            response.status = 422
            return {"location": ""}
        return _server_error(conn, e)
    
    finally:
        _close_db_connection(cursor, conn)

# Returns all pallets 
def get_pallets(cookie, after, before):
    conn, cursor = _get_db_connection()

    # Create a base query which fetches the ID, cookie type and date of all pallets, and a 1 or 0 depending on if 
    # they appear in the subquery which contains the pallets of that cookie produced while the cookie was blocked
    query = """
            SELECT pallet_id, cookie_name, SUBSTRING(timestamp, 0, 11) AS date, 
            CASE 
                WHEN pallet_id IN (
                    SELECT pallet_id
                    FROM pallets
                        JOIN cookies USING(cookie_name)
                        JOIN blockages USING(cookie_name)
                    WHERE timestamp > start_time
                    AND timestamp < end_time) THEN 1
                ELSE 0
            END AS blocked
            FROM pallets
            WHERE TRUE
            """
    
    # Restrict the result by adding conditions to the WHERE statement in the query, with parameterisation to resist SQL injection 
    parameters = []
    if cookie:
        query += " AND cookie_name = ?"
        parameters.append(cookie)
    if after:
        query += " AND timestamp > ?"
        parameters.append(f"{after} 23:59:59") # Add the latest possible time to exclude the given date, since the timestamps in the database include time of day
    if before:
        query += " AND timestamp < ?"
        parameters.append(f"{before} 00:00:00") # Add the earliest possible time to exclude the given date, since the timestamps in the database include time of day
    
    try:
        cursor.execute(query, parameters)
        pallets = [{"id": pallet_id, "cookie": cookie_name, "productionDate": date, "blocked": blocked} for pallet_id, cookie_name, date, blocked in cursor]
        response.status = 200
        return {"data": pallets}

    except Exception as e:
        return _server_error(conn, e)
    
    finally:
        _close_db_connection(cursor, conn)

# Blocks the pallets of a cookie which are produced in a certain interval
def block_pallets(cookie, after, before):
    conn, cursor = _get_db_connection()

    # Convert the time variables to suit the database
    if after:
        after += " 23:59:59" # Excludes the given date, since the timestamps in the database include time of day
    else:
        after = "0001-01-01 00:00:00" # Minimum possible value to represent no start time
    if before:
        before += " 00:00:00" # Excludes the given date, since the timestamps in the database include time of day
    else:
        before = "9999-12-31 23:59:59" # Maximum possible value to represent no end time

    try:
        # Insert a blockage of the given cookie during the given interval
        cursor.execute(
            """
            INSERT INTO blockages(cookie_name, start_time, end_time)
            VALUES (?, ?, ?)
            """, [cookie, after, before]
        )
        conn.commit()
        response.status = 205
        return ""
    
    except Exception as e:
        return _server_error(conn, e)
    
    finally:
        _close_db_connection(cursor, conn)

# Unblocks the pallets of a cookie which are produced in a certain interval
def unblock_pallets(cookie, after, before):
    conn, cursor = _get_db_connection()

    # Convert the time variables to suit the database
    if after:
        after += " 23:59:59" # Excludes the given date, since the timestamps in the database include time of day
    else:
        after = "0001-01-01 00:00:00" # Minimum possible value to represent no start time
    if before:
        before += " 00:00:00" # Excludes the given date, since the timestamps in the database include time of day
    else:
        before = "9999-12-31 23:59:59" # Maximum possible value to represent no start time

    try:
        # Delete the blockages of the given cookie the intervals of which are contained by the given interval
        cursor.execute(
            """
            DELETE FROM blockages
            WHERE cookie_name = ?
            AND start_time >= ?
            AND end_time <= ?
            """, [cookie, after, before]
        )
        conn.commit()
        response.status = 205
        return ""
    
    except Exception as e:
        return _server_error(conn, e)
    
    finally:
        _close_db_connection(cursor, conn)

# Inserts a new order in the database
def create_order(customer, delivery_date, ordered_cookies):
    conn, cursor = _get_db_connection()

    try:
        # Check if the customer exists and abort otherwise
        cursor.execute(
            """
            SELECT 1
            FROM customers
            WHERE customer_name = ?
            """, [customer]
        )
        customer_exists = cursor.fetchone()[0]
        if not customer_exists:
            response.status = 404
            return ""

        # Check if all the cookies exist and abort otherwise
        for cookie_name, _ in ordered_cookies:
            cursor.execute(
                """
                SELECT 1 
                FROM cookies
                WHERE cookie_name = ?
                """, [cookie_name]
            )
            cookie_exists = cursor.fetchone()[0]
            if not cookie_exists:
                response.status = 404
                return ""

        # Insert an order for the given date and the given customer, and return its randomly assigned ID
        cursor.execute(
            """
            INSERT INTO orders(delivery_date, customer_name)
            VALUES (?, ?)
            RETURNING order_id
            """, [delivery_date, customer]
        )
        order_id = cursor.fetchone()

        # Insert how much of each cookie the order contains
        for cookie_name, amount in ordered_cookies:
            cursor.execute(
                """
                INSERT INTO order_contents
                VALUES (?, ?, ?)
                """, [order_id, cookie_name, amount]
            )
        conn.commit()

        response.status = 201
        return {"location": f"/orders/{order_id}"}
    
    except Exception as e:
        return _server_error(conn, e)
    
    finally:
        _close_db_connection(cursor, conn)

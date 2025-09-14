PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cookies;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS ingredient_usages;
DROP TABLE IF EXISTS inventory_updates;
DROP TABLE IF EXISTS pallets;
DROP TABLE IF EXISTS order_contents;
DROP TABLE IF EXISTS blockages;
DROP TABLE IF EXISTS deliveries;

PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_name TEXT PRIMARY KEY NOT NULL,
    address TEXT NOT NULL
);

CREATE TABLE orders (
    order_id TEXT DEFAULT (lower(hex (randomblob (16)))) PRIMARY KEY NOT NULL,
    delivery_date DATE NOT NULL,
    customer_name TEXT NOT NULL,
    FOREIGN KEY (customer_name) REFERENCES customers (customer_name)
);

CREATE TABLE cookies (
    cookie_name TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE ingredients (
    ingredient_name TEXT PRIMARY KEY NOT NULL,
    unit TEXT NOT NULL
);

CREATE TABLE ingredient_usages (
    ingredient_name TEXT NOT NULL,
    cookie_name TEXT NOT NULL,
    amount FLOAT NOT NULL,
    PRIMARY KEY (ingredient_name, cookie_name),
    FOREIGN KEY (ingredient_name) REFERENCES ingredients (ingredient_name),
    FOREIGN KEY (cookie_name) REFERENCES cookies (cookie_name)
);

CREATE TABLE inventory_updates (
    update_id TEXT DEFAULT (lower(hex (randomblob (16)))) PRIMARY KEY NOT NULL,
    ingredient_name TEXT NOT NULL,
    change FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (ingredient_name) REFERENCES ingredients (ingredient_name)
);

CREATE TABLE pallets (
    pallet_id TEXT DEFAULT (lower(hex (randomblob (16)))) PRIMARY KEY NOT NULL,
    cookie_name TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (cookie_name) REFERENCES cookies (cookie_name)
);

CREATE TABLE order_contents (
    order_id TEXT NOT NULL,
    cookie_name TEXT NOT NULL,
    quantity FLOAT NOT NULL,
    PRIMARY KEY (order_id, cookie_name),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (cookie_name) REFERENCES cookies (cookie_name)
);

CREATE TABLE blockages (
    blockage_id TEXT DEFAULT (lower(hex (randomblob (16)))) PRIMARY KEY NOT NULL,
    cookie_name TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    FOREIGN KEY (cookie_name) REFERENCES cookies (cookie_name)
);

CREATE TABLE deliveries (
    delivery_id TEXT DEFAULT (lower(hex (randomblob (16)))) PRIMARY KEY NOT NULL,
    pallet_id TEXT NOT NULL,
    load_time TIMESTAMP NOT NULL,
    delivery_time TIMESTAMP NOT NULL,
    FOREIGN KEY (pallet_id) REFERENCES pallets (pallet_id)
);

CREATE TRIGGER update_ingredients
AFTER INSERT ON pallets
BEGIN
    INSERT INTO inventory_updates(ingredient_name, change, timestamp)
    SELECT ingredient_name, -(amount / 100 * 15 * 10 * 36), NEW.timestamp
    FROM ingredient_usages
    WHERE cookie_name = NEW.cookie_name;
END;

CREATE TRIGGER check_enough_ingredients
AFTER INSERT ON inventory_updates
FOR EACH ROW
WHEN ((
    SELECT COALESCE(SUM(change), 0)
    FROM inventory_updates
    WHERE ingredient_name = NEW.ingredient_name) < 0)
BEGIN
    SELECT RAISE (ROLLBACK, 'There are not enough ingredients to bake this pallet');
END;
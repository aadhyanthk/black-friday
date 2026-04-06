-- init.sql (E-commerce Version)
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS seats;
DROP TABLE IF EXISTS bookings;

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    stock_count INTEGER NOT NULL CHECK (stock_count >= 0)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER REFERENCES inventory(id),
    user_identifier VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed the Black Friday Item
INSERT INTO inventory (item_name, stock_count) VALUES ('Black Friday Special: Quantum Processor', 100);
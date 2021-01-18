CREATE TABLE IF NOT EXISTS users (
    user_id serial PRIMARY KEY,
    user_name VARCHAR (50) UNIQUE NOT NULL,
    user_role BOOLEAN NOT NULL,
    password VARCHAR (255) NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
CREATE TABLE IF NOT EXISTS payment_methods (
    payment_method_id serial PRIMARY KEY,
    payment_type INTEGER UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS patients (
    patient_id serial PRIMARY KEY,
    patient_name VARCHAR (50) NOT NULL,
    patient_surname VARCHAR (50) NOT NULL,
    patient_phone_number VARCHAR (13)
);
CREATE TABLE IF NOT EXISTS baskets (
    basket_id serial PRIMARY KEY,
    basket_state BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS sales (
    sale_id serial PRIMARY KEY,
    basket_id INTEGER NOT NULL,
    patient_id INTEGER,
    payment_method_id INTEGER,
    price NUMERIC (10, 2) NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (basket_id) REFERENCES baskets (basket_id),
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods (payment_method_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id serial PRIMARY KEY,
    med_name VARCHAR (50) NOT NULL,
    med_barcode VARCHAR (80) NOT NULL,
    price NUMERIC (10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    med_detail VARCHAR (300)
);
CREATE TABLE IF NOT EXISTS basket_entries (
    basket_entry_id serial PRIMARY KEY,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER,
    basket_id INTEGER NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines (medicine_id),
    FOREIGN KEY (basket_id) REFERENCES baskets (basket_id)
);
CREATE TABLE IF NOT EXISTS med_alternatives (
    med_alternative_id serial PRIMARY KEY,
    med_alternative INTEGER NOT NULL,
    med_original INTEGER NOT NULL,
    FOREIGN KEY (med_alternative) REFERENCES medicines (medicine_id),
    FOREIGN KEY (med_original) REFERENCES medicines (medicine_id)
);


INSERT INTO users (user_id, user_name, user_role, password)
VALUES (0, 'eczaci', true, '123')

INSERT INTO medicines (med_name, med_barcode, price, stock_quantity, med_detail) VALUES ('Augmentin', 3, 55, 500, 'Classic Augmentin')

SELECT med_name, price, stock_quantity, med_detail FROM medicines WHERE med_barcode = '1'
UPDATE basket_entries SET quantity = 11 WHERE medicine_id = 1
DELETE FROM basket_entries WHERE basket_id = 1
UPDATE users SET created_at = CURRENT_TIMESTAMP
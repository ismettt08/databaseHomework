#DATABASE_URL="postgres://taha:123456@127.0.0.1:5432/eczanem" python3 dbinit.py 

import os
import sys

import psycopg2 as dbapi2

NEW_INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS users (
	user_id serial PRIMARY KEY,
	user_name VARCHAR (50) UNIQUE NOT NULL,
	password VARCHAR (255) NOT NULL,
	user_role INTEGER NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	last_login TIMESTAMP WITH TIME ZONE
    );""",
    """CREATE TABLE IF NOT EXISTS sessions (
	user_id INTEGER NOT NULL,
	session_id VARCHAR (60) PRIMARY KEY,
	last_used TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE,
	user_agent VARCHAR (100),
	ip VARCHAR (15),
	theme INTEGER,
	FOREIGN KEY (user_id) REFERENCES users (user_id)
    );""",
    """CREATE TABLE IF NOT EXISTS payment_methods (
	payment_method_id serial PRIMARY KEY,
	payment_type INTEGER UNIQUE NOT NULL 
    );""",
    """CREATE TABLE IF NOT EXISTS patients (
	patient_id serial PRIMARY KEY,
	patient_name VARCHAR (50) NOT NULL,
	patient_surname VARCHAR (50) NOT NULL,
	patient_phone_number VARCHAR (15),
	patient_id_number VARCHAR (11),
	created_at TIMESTAMP WITH TIME ZONE
    );""",
    """CREATE TABLE IF NOT EXISTS baskets (
	basket_id serial PRIMARY KEY,
	basket_state BOOLEAN NOT NULL 
	);""",
    """CREATE TABLE IF NOT EXISTS sales (
	sale_id serial PRIMARY KEY,
	basket_id INTEGER NOT NULL,
	patient_id INTEGER,
	payment_method_id INTEGER,
	price NUMERIC (10, 2) NOT NULL,
	user_id INTEGER, FOREIGN KEY (basket_id) REFERENCES baskets (basket_id),
	FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
	FOREIGN KEY (payment_method_id) REFERENCES payment_methods (payment_method_id),
	FOREIGN KEY (user_id) REFERENCES users (user_id) 
	);""",
    """CREATE TABLE IF NOT EXISTS medicines (
	medicine_id serial PRIMARY KEY, 
	med_name VARCHAR (50) NOT NULL, 
	med_barcode VARCHAR (80) NOT NULL,
	price NUMERIC (10, 2) NOT NULL,
	stock_quantity INTEGER NOT NULL,
	med_detail VARCHAR (300) 
	);""",
    """CREATE TABLE IF NOT EXISTS basket_entries (
	basket_entry_id serial PRIMARY KEY,
	medicine_id INTEGER NOT NULL,
	quantity INTEGER,
	basket_id INTEGER NOT NULL,
	FOREIGN KEY (medicine_id) REFERENCES medicines (medicine_id),
	FOREIGN KEY (basket_id) REFERENCES baskets (basket_id) 
	);""",
    """CREATE TABLE IF NOT EXISTS med_alternatives (
	med_alternative_id serial PRIMARY KEY,
	med_alternative INTEGER NOT NULL,
	med_original INTEGER NOT NULL,
	FOREIGN KEY (med_alternative) REFERENCES medicines (medicine_id),
	FOREIGN KEY (med_original) REFERENCES medicines (medicine_id) 
	);""",
    """INSERT INTO users (user_id, user_name, user_role, password, created_at) 
    VALUES (1, 'eczaci', 1, 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING""",
    """INSERT INTO users (user_id, user_name, user_role, password, created_at) 
    VALUES (2, 'deletedUSER', 0, 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING""",
    """INSERT INTO patients (patient_id, patient_name, patient_surname, patient_id_number, created_at) 
    VALUES (1, 'deleted', 'Patient', '0', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING""",
    
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (1, 'Augmentin', 0, 18.80, 500, 'Classic Augmentin') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (2, 'Croxilex', 1, 15.50, 300, 'Classic Croxilex') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (3, 'Parol', 2, 5.90, 800, 'Classic Parol') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (4, 'Aspirin', 3, 8.10, 700, 'Classic Aspirin') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (5, 'Katarin', 4, 11.15, 200, 'Classic Katarin') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (6, 'Silverdin', 5, 15.65, 100, 'Classic Silverdin') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (7, 'Levotiron', 6, 13.00, 100, 'Classic Levotiron') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (8, 'Minafen', 7, 7.00, 100, 'Classic Minafen') ON CONFLICT DO NOTHING",
    "INSERT INTO medicines (medicine_id, med_name, med_barcode, price, stock_quantity, med_detail) VALUES (9, 'Calpol', 8, 9.00, 150, 'Classic Calpol') ON CONFLICT DO NOTHING",
    "INSERT INTO med_alternatives (med_alternative_id, med_alternative, med_original) VALUES (1, 1, 2) ON CONFLICT DO NOTHING",
    "INSERT INTO med_alternatives (med_alternative_id, med_alternative, med_original) VALUES (2, 8, 9) ON CONFLICT DO NOTHING",
    "INSERT INTO med_alternatives (med_alternative_id, med_alternative, med_original) VALUES (3, 2, 1) ON CONFLICT DO NOTHING",
    "INSERT INTO med_alternatives (med_alternative_id, med_alternative, med_original) VALUES (4, 9, 8) ON CONFLICT DO NOTHING",
    "INSERT INTO payment_methods (payment_method_id, payment_type) VALUES (1, 0) ON CONFLICT DO NOTHING",
    "INSERT INTO payment_methods (payment_method_id, payment_type) VALUES (2, 1) ON CONFLICT DO NOTHING"
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in NEW_INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
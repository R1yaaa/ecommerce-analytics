CREATE TABLE products (
	stock_code VARCHAR PRIMARY KEY,
	description VARCHAR NOT NULL
);

CREATE TABLE customers(
	customer_id INT PRIMARY KEY
);

CREATE TABLE orders(
	invoice_no VARCHAR PRIMARY KEY,
	invoice_date TIMESTAMP NOT NULL,
	customer_id INT REFERENCES customers(customer_id),
	country VARCHAR NOT NULL
);	

CREATE TABLE order_items(
	order_item_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Surrogate key generated automatically by PostgreSQL
	invoice_no VARCHAR NOT NULL REFERENCES orders(invoice_no),
	stock_code VARCHAR NOT NULL REFERENCES products(stock_code),
	quantity INT CHECK(quantity > 0) NOT NULL,
	unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price > 0)
);
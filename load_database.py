import os
import psycopg
import pandas as pd
from dotenv import load_dotenv
from prepare_tables import products_df, customers_df, orders_df, order_items_df

load_dotenv()

connection = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

cursor.execute(
    """
    TRUNCATE TABLE order_items, orders, customers, products
    RESTART IDENTITY;
    """
)

with cursor.copy ("COPY products (stock_code, description) FROM STDIN") as copy:
    for product in products_df.itertuples(index=False):
        copy.write_row(
            (product.StockCode, product.Description)
        )

with cursor.copy ("COPY customers (customer_id) FROM STDIN") as copy:
    for customer in customers_df.itertuples(index=False):
        copy.write_row(
            (customer.CustomerID, )
        )

with cursor.copy ("COPY orders (invoice_no, invoice_date, customer_id, country) FROM STDIN") as copy:
    for order in orders_df.itertuples(index=False):
        copy.write_row(
            (order.InvoiceNo, order.InvoiceDate, None if pd.isna(order.CustomerID) else order.CustomerID, order.Country)
        )

with cursor.copy ("COPY order_items (invoice_no, stock_code, quantity, unit_price) FROM STDIN") as copy:
    for order_item in order_items_df.itertuples(index=False):
        copy.write_row(
            (order_item.InvoiceNo, order_item.StockCode, order_item.Quantity, order_item.UnitPrice )
        )

connection.commit()
connection.close()
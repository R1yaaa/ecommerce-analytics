import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

database_url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(database_url)

# monthly revenue
monthly_revenue_df = pd.read_sql_query(
    """
    SELECT ROUND(SUM(unit_price * quantity), 2) AS revenue, DATE_TRUNC('month', invoice_date) AS month
    FROM order_items
    JOIN orders
        ON orders.invoice_no = order_items.invoice_no
    GROUP BY DATE_TRUNC('month', invoice_date)
    ORDER BY month ASC;
    """,
    engine
)

plt.plot(monthly_revenue_df["month"], monthly_revenue_df["revenue"])
plt.title("Monthly revenue")
plt.xlabel("Month")
plt.ylabel("Revenue (£)")
plt.grid()
plt.show()

max_revenue_month_index = monthly_revenue_df["revenue"].idxmax()
max_revenue_month = monthly_revenue_df.iloc[max_revenue_month_index]
print(max_revenue_month)

# top 10 products (by revenue)
top_products_df = pd.read_sql_query(
    """
    SELECT products.stock_code AS Stockcode, description AS product, ROUND(SUM(unit_price * quantity), 2) AS revenue
    FROM products
    JOIN order_items
        ON products.stock_code = order_items.stock_code
    GROUP by products.stock_code, description
    ORDER BY revenue DESC
    LIMIT 10;
    """,
    engine
)

fig, ax = plt.subplots()
ax.barh(top_products_df["product"], top_products_df["revenue"])
ax.set_title("Top 10 products by revenue")
ax.set_xlabel("Revenue (£)")
ax.set_ylabel("Product")
ax.invert_yaxis()
plt.show()



orders_df = pd.read_sql_query(
    """
    SELECT invoice_no, invoice_date, customer_id
    FROM orders
    WHERE customer_id IS NOT NULL;
    """,
    engine
)

order_items_df = pd.read_sql_query(
    """
    SELECT invoice_no, quantity, unit_price
    FROM order_items;
    """,
    engine
)

# Create order-level dataset
order_details_df = pd.merge(orders_df, order_items_df, on="invoice_no")
order_details_df["item_revenue"] = order_details_df["quantity"] * order_details_df ["unit_price"]
order_analysis_df = order_details_df.groupby(["invoice_no", "customer_id", "invoice_date"])["item_revenue"].sum()
order_analysis_df = order_analysis_df.reset_index()
order_analysis_df = order_analysis_df.rename(columns={'item_revenue' : 'order_value'})

print(order_analysis_df.head())
print(order_analysis_df.shape[0])
print(order_analysis_df.shape[1])
print(order_analysis_df["invoice_no"].nunique())

max_order_index = order_analysis_df["order_value"].idxmax()
max_order_df= order_analysis_df.iloc[max_order_index]

print(max_order_df)



customer_analysis_df = order_analysis_df.groupby("customer_id").agg(
    order_count=("invoice_no", "count"),
    total_spent=("order_value", "sum"),
    average_order_value=("order_value", "mean"),
    last_purchase=("invoice_date", "max")
)

customer_analysis_df = customer_analysis_df.reset_index()
print(customer_analysis_df.head())
print(customer_analysis_df.shape[0])
print(customer_analysis_df.shape[1])
print(customer_analysis_df["customer_id"].nunique())

max_total_spent_index = customer_analysis_df["total_spent"].idxmax()
max_total_spent_df = customer_analysis_df.iloc[max_total_spent_index]

print(max_total_spent_df)

reference_date = order_analysis_df["invoice_date"].max() + pd.Timedelta(days=1)
customer_analysis_df["recency"] = (
    reference_date - customer_analysis_df["last_purchase"]
).dt.days

print(customer_analysis_df.head())
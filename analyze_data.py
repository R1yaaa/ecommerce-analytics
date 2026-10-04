import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# Database connection
load_dotenv()

database_url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

# SQLAlchemy Engine manages database connections for pandas queries
engine = create_engine(database_url)


# Monthly revenue
monthly_revenue_df = pd.read_sql_query(
    """
    SELECT
        ROUND(SUM(unit_price * quantity), 2) AS revenue,
        DATE_TRUNC('month', invoice_date) AS month
    FROM order_items
    JOIN orders
        ON orders.invoice_no = order_items.invoice_no
    GROUP BY DATE_TRUNC('month', invoice_date)
    ORDER BY month ASC;
    """,
    engine
)

fig, ax = plt.subplots()
ax.plot(monthly_revenue_df["month"], monthly_revenue_df["revenue"])
ax.set_title("Monthly revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (£)")
ax.grid()
plt.show()

max_revenue_month_index = monthly_revenue_df["revenue"].idxmax()
max_revenue_month = monthly_revenue_df.iloc[max_revenue_month_index]

print("Highest revenue month:")
print(max_revenue_month)


# Top 10 products by revenue
top_products_df = pd.read_sql_query(
    """
    SELECT
        products.stock_code AS stock_code,
        description AS product,
        ROUND(SUM(unit_price * quantity), 2) AS revenue
    FROM products
    JOIN order_items
        ON products.stock_code = order_items.stock_code
    GROUP BY products.stock_code, description
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


# Load order data
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
# Join order-level information with its individual order items.
order_details_df = pd.merge(orders_df,order_items_df,on="invoice_no")

# Calculate revenue for each individual product line
order_details_df["item_revenue"] = (order_details_df["quantity"] * order_details_df["unit_price"])

# Aggregate product lines back to one row per order
# These values are later used to build the RFM features.
order_analysis_df = (
    order_details_df
    .groupby(["invoice_no", "customer_id", "invoice_date"])["item_revenue"]
    .sum()
    .reset_index()
    .rename(columns={"item_revenue": "order_value"})
)

max_order_index = order_analysis_df["order_value"].idxmax()
max_order = order_analysis_df.iloc[max_order_index]

print("\nHighest-value order:")
print(max_order)


# Create customer-level dataset
customer_analysis_df = (order_analysis_df.groupby("customer_id").agg(
        order_count=("invoice_no", "count"),
        total_spent=("order_value", "sum"),
        average_order_value=("order_value", "mean"),
        last_purchase=("invoice_date", "max")
    )
    .reset_index()
)

# Use one day after the dataset's last purchase as the artificial
# "current date" because the dataset contains historical transactions
reference_date = (order_analysis_df["invoice_date"].max()+ pd.Timedelta(days=1))

# Recency = number of days since the customer's most recent purchase
customer_analysis_df["recency"] = (reference_date - customer_analysis_df["last_purchase"]).dt.days


# RFM summary
# Inspect the distributions of the three RFM features:
# Recency, Frequency (order_count), and Monetary value (total_spent)
rfm_summary = customer_analysis_df[["recency", "order_count", "total_spent"]].describe()

print("\nRFM summary:")
print(rfm_summary)


# Visualize original customer spending distribution
fig, ax = plt.subplots()
ax.hist(customer_analysis_df["total_spent"], bins=50)
ax.set_title("Distribution of customer spending")
ax.set_xlabel("Total spent (£)")
ax.set_ylabel("Number of customers")
plt.show()


# Log-transform skewed features to reduce the influence of extremely large values/outliers
customer_analysis_df["total_spent_log"] = np.log1p( # np.log1p(x) = log(1 + x)
    customer_analysis_df["total_spent"]
)

customer_analysis_df["order_count_log"] = np.log1p(
    customer_analysis_df["order_count"]
)

fig, ax = plt.subplots()
ax.hist(customer_analysis_df["total_spent_log"], bins=50)
ax.set_title("Log-transformed customer spending")
ax.set_xlabel("Log-transformed total spent")
ax.set_ylabel("Number of customers")
plt.show()


# Prepare and scale RFM features for K-Means
rfm_features = customer_analysis_df[["recency", "order_count_log", "total_spent_log"]]

# Standardize all features to comparable scales (mean ≈ 0, std ≈ 1) to prevent features with larger numeric values from dominating K-Means
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_features)


# Determine number of clusters using the Elbow Method
# Train K-Means for different values of k and store each model's inertia.
# Inertia is the sum of squared distances between data points
# and the center of their assigned cluster.
inertias = []

for k in range(2, 11):
    model = KMeans(
        n_clusters=k,
        random_state=10
    )
    model.fit(rfm_scaled)
    inertias.append(model.inertia_)

fig, ax = plt.subplots()
ax.plot(range(2, 11), inertias)
ax.set_title("Elbow Method")
ax.set_xlabel("Number of clusters")
ax.set_ylabel("Inertia")
ax.set_xticks(range(2, 11))
plt.show()


# Final K-Means model
# Use four clusters based on the Elbow Method.
kmeans = KMeans(
    n_clusters=4,
    random_state=10
)

customer_analysis_df["cluster"] = kmeans.fit_predict(rfm_scaled)


# Analyze customer clusters using original values
customer_cluster_df = (customer_analysis_df.groupby("cluster").agg(
        average_recency=("recency", "mean"),
        average_order_count=("order_count", "mean"),
        average_total_spent=("total_spent", "mean"),
        customer_count=("customer_id", "count")
    )
    .reset_index()
)

print("\nCustomer cluster summary:")
print(customer_cluster_df)


# Visualize customer segments
fig, ax = plt.subplots()

scatter = ax.scatter(
    customer_analysis_df["recency"],
    customer_analysis_df["total_spent_log"],
    c=customer_analysis_df["cluster"],
    alpha=0.5
)

ax.set_title("Customer segments")
ax.set_xlabel("Recency (days)")
ax.set_ylabel("Log-transformed total spent")

legend = ax.legend(
    *scatter.legend_elements(),
    title="Cluster"
)

ax.add_artist(legend)

plt.show()
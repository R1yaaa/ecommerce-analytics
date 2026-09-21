from clean_data import clean_df, customer_df

# PRODUCT TABLE
products = clean_df[["StockCode", "Description"]]
products_df = products.groupby("StockCode")["Description"].agg(lambda x: x.mode().iloc[0])  #pandas.Series
products_df = products_df.reset_index() #make it a DataFrame
products_df["StockCode"] = products_df["StockCode"].astype(str)

# CUSTOMER TABLE
customers_df = customer_df[["CustomerID"]].drop_duplicates()
customers_df["CustomerID"] = customers_df["CustomerID"].astype(int) 

# ORDERS TABLE
orders_df = clean_df[["InvoiceNo", "InvoiceDate", "CustomerID","Country"]].drop_duplicates()
orders_df["CustomerID"] = orders_df["CustomerID"].astype("Int64")
orders_df = orders_df.groupby("InvoiceNo").agg({
    "InvoiceDate" : "min",
    "CustomerID" : "first",
    "Country" : "first"
}).reset_index()
orders_df["InvoiceNo"] = orders_df["InvoiceNo"].astype(str)

# ORDER_ITEMS TABLE
order_items_df = clean_df[["InvoiceNo", "StockCode", "Quantity", "UnitPrice"]]
order_items_df["InvoiceNo"] = order_items_df["InvoiceNo"].astype(str)
order_items_df["StockCode"] = order_items_df["StockCode"].astype(str)


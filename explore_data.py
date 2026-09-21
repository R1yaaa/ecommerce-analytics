import pandas as pd

df = pd.read_excel("data/Online_Retail.xlsx")

# --- Basic dataset information ---
print("--- BASIC INFO ---")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# --- Missing values ---
print("--- MISSING VALUES ---")
print(df.isna().sum())

# Percentage of rows where CustomerID is missing
missing_customer_percentage = (df["CustomerID"].isna().sum() / len(df)) * 100

print(f"Missing CustomerID: {missing_customer_percentage:.2f}%")

# --- Product description consistency ---
# Count how many different descriptions exist for each StockCode
description_counts = (df.groupby("StockCode")["Description"].nunique()) 
# Keep only StockCodes that have more than one description
problematic_desc_counts = description_counts[description_counts > 1]

print("--- PRODUCT DESCRIPTION CHECK ---")
print(f"StockCodes with multiple descriptions: "f"{len(problematic_desc_counts)}") #description might change over time

# --- Unit price consistency ---
# Count how many different prices exist for each StockCode
unit_price_counts = (df.groupby("StockCode")["UnitPrice"].nunique()) # Multiple prices can indicate price changes over time
# Keep only StockCodes that appear with more than one UnitPrice
problematic_price_counts = unit_price_counts[unit_price_counts > 1]

print("--- UNIT PRICE CHECK ---")
print(f"StockCodes with multiple unit prices: "f"{len(problematic_price_counts)}")

# --- Negative quantities ---
# Negative quantities can indicate cancellations or internal stock corrections
negative_quantity = df[df["Quantity"] < 0]

print("--- NEGATIVE QUANTITY CHECK ---")
print(f"Rows with negative Quantity: {len(negative_quantity)}")

# --- Cancellations ---
invoice_text = df["InvoiceNo"].astype(str)

# In this dataset, InvoiceNo values starting with "C" represent cancellations
cancellations = df[invoice_text.str.startswith("C")]

print("--- CANCELLATION CHECK ---")
print(f"Rows with cancellation InvoiceNo: {len(cancellations)}")

# --- Negative quantities without cancellation ---
# These rows are likely internal stock adjustments such as lost, missing or damaged items
negative_without_c = df[(~invoice_text.str.startswith("C"))& (df["Quantity"] < 0)]

print("--- NEGATIVE QUANTITY WITHOUT C ---")
print(f"Negative quantities without C invoice: "f"{len(negative_without_c)}")

# --- Missing CustomerID in positive transactions ---
# These could still be valid sales, but they cannt be used for customer-level analysis
missing_customer_sales = df[(df["CustomerID"].isna())& (df["Quantity"] > 0)]

print("--- MISSING CUSTOMERID CHECK ---")
print(f"Positive quantity rows without CustomerID: "f"{len(missing_customer_sales)}")

# --- Country Consistency ---
# Check whether a customer can be associated with multiple countries
customer_country_counts = df.groupby("CustomerID")["Country"].nunique()
customers_multiple_countries = customer_country_counts[customer_country_counts > 1]

print("--- CUSTOMER COUNTRY CHECK ---")
print(f"CustomerIDs with multiple countries: "f"{len(customers_multiple_countries)}")

# Check whether an invoice can be associated with multiple countries
invoice_country_counts = df.groupby("InvoiceNo")["Country"].nunique()
invoices_multiple_countries = invoice_country_counts[invoice_country_counts > 1]

print("--- INVOICE COUNTRY CHECK ---")
print(f"InvoiceNos with multiple countries: "f"{len(invoices_multiple_countries)}")

# --- Order item uniqueness ---
# Check whether the same product appears multiple times within one invoice
duplicate_order_items = df.duplicated(subset=["InvoiceNo", "StockCode"]).sum()

print("--- ORDER ITEM UNIQUENESS CHECK ---")
print(f"Duplicate InvoiceNo + StockCode combinations: "f"{duplicate_order_items}")
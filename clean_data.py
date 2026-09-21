import pandas as pd
# only use data with Quantity > 0, UnitPrice > 0, InvoiceNo doesn't begin with C

df = pd.read_excel("data/Online_Retail.xlsx")
invoice_text = df["InvoiceNo"].astype(str)

# Keep valid transactions
# CustomerID may be missing, because transaction is still useful for product analysis
clean_df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0) & (~invoice_text.str.startswith("C"))]

# seperate dataset without missing CustomerID
customer_df = clean_df[~clean_df["CustomerID"].isna()]

# --- Cleaning summary ---
removed_rows = df.shape[0] - clean_df.shape[0]

print(f"Rows of original data: {df.shape[0]}")
print(f"Rows of clean data: {clean_df.shape[0]}")
print(f"Removed Rows: {removed_rows}")

# missing values for CustomerID
print(f"Missing Values for CustomerID in customer dataset: {customer_df["CustomerID"].isna().sum()}")

# missing values for Description
print(f"Missing values for Description in clean dataset: {clean_df["Description"].isna().sum()}")

-- total revenue
SELECT ROUND(SUM(unit_price * quantity),2)  AS total_revenue
FROM order_items;

-- revenue per country (descending), orders per country
SELECT orders.country, ROUND(SUM(unit_price * quantity),2) AS revenue, COUNT(DISTINCT orders.invoice_no) AS orders
FROM order_items 
JOIN orders
    ON order_items.invoice_no = orders.invoice_no
GROUP BY orders.country
ORDER BY revenue DESC;

-- top 10 products by revenue
SELECT products.stock_code AS Stockcode, description AS product, ROUND(SUM(unit_price * quantity), 2) AS revenue
FROM products
JOIN order_items
    ON products.stock_code = order_items.stock_code
GROUP by products.stock_code, description
ORDER BY revenue DESC
LIMIT 10;

-- revenue per month (latest first)
SELECT ROUND(SUM(unit_price * quantity), 2) AS revenue, DATE_TRUNC('month', invoice_date) AS month
FROM order_items
JOIN orders
    ON orders.invoice_no = order_items.invoice_no
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month DESC;

-- top 10 customers
SELECT customers.customer_id AS customer, ROUND(SUM(quantity * unit_price), 2) AS revenue
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
JOIN order_items
    ON order_items.invoice_no = orders.invoice_no
GROUP BY customers.customer_id
ORDER BY revenue DESC
LIMIT 10;

-- average order value
SELECT ROUND(AVG(value),2) AS average_order_value
FROM 
    (SELECT invoice_no as order, SUM(quantity * unit_price) AS value
    FROM order_items
    GROUP BY invoice_no)
AS order_totals;

-- top 10 product pairs most frequently ordered together
SELECT item_1.stock_code AS product_1, item_2.stock_code AS product_2, COUNT(DISTINCT item_1.invoice_no) AS times_bought_together
FROM order_items AS item_1
JOIN order_items AS item_2
    ON item_1.invoice_no = item_2.invoice_no
AND item_1.stock_code < item_2.stock_code
GROUP BY product_1, product_2
ORDER BY times_bought_together DESC
LIMIt 10;
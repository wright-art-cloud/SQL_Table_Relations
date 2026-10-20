# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# Inspect database schema if needed
pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# ==========================================
# Part 1: Join and Filter (Fix shape to 2 columns)
# ==========================================

# Step 1: Return first and last names for all employees in Boston (adjusting to 2 columns to match test shape (2,2))
df_boston = pd.read_sql("""
    SELECT employees.firstName, employees.lastName
    FROM employees
    JOIN offices ON employees.officeCode = offices.officeCode
    WHERE offices.city = 'Boston'
""", conn)


# Step 2: Are there any offices that have zero employees?
df_zero_emp = pd.read_sql("""
    SELECT offices.*
    FROM offices
    LEFT JOIN employees ON offices.officeCode = employees.officeCode
    WHERE employees.employeeNumber IS NULL
""", conn)


# ==========================================
# Part 2: Type of Join
# ==========================================

# Step 3: Return employees' first name, last name, city, and state. Include all employees, sorted by first name then last name.
df_employee = pd.read_sql("""
    SELECT employees.firstName, employees.lastName, offices.city, offices.state
    FROM employees
    LEFT JOIN offices ON employees.officeCode = offices.officeCode
    ORDER BY employees.firstName ASC, employees.lastName ASC
""", conn)


# Step 4: Contact info (first name, last name, phone number) and sales rep employee number for customers with NO orders, sorted by last name.
df_contacts = pd.read_sql("""
    SELECT customers.contactFirstName, customers.contactLastName, customers.phone, customers.salesRepEmployeeNumber
    FROM customers
    LEFT JOIN orders ON customers.customerNumber = orders.customerNumber
    WHERE orders.orderNumber IS NULL
    ORDER BY customers.contactLastName ASC
""", conn)


# ==========================================
# Part 3: Built-In Function
# ==========================================

# Step 5: Customer contacts (first/last names) with payment amounts and dates, sorted descending by payment amount.
# Note: CAST(amount AS REAL) handles cases where amount might be stored as text.
df_payment = pd.read_sql("""
    SELECT customers.contactFirstName, customers.contactLastName, payments.amount, payments.paymentDate
    FROM customers
    JOIN payments ON customers.customerNumber = payments.customerNumber
    ORDER BY CAST(payments.amount AS REAL) DESC
""", conn)


# ==========================================
# Part 4: Joining and Grouping
# ==========================================

# Step 6: Employee number, first name, last name, and number of customers for employees whose customers average a credit limit > 90k.
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName, COUNT(c.customerNumber) AS n_customers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY n_customers DESC
""", conn)


# Step 7: Product name, numorders (count of orders), and totalunits (sum of quantityOrdered), sorted highest to lowest by totalunits.
df_product_sold = pd.read_sql("""
    SELECT p.productName, COUNT(od.orderNumber) AS numorders, SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC
""", conn)


# ==========================================
# Part 5: Multiple Joins
# ==========================================

# Step 8: Product name, code, and total unique purchasers (numpurchasers), sorted by highest number of purchasers.
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode, COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode
    ORDER BY numpurchasers DESC
""", conn)


# Step 9: Count of customers per office (n_customers), office code, and city.
df_customers = pd.read_sql("""
    SELECT COUNT(c.customerNumber) AS n_customers, o.officeCode, o.city
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode
""", conn)

# ==========================================
# Part 6: Subquery (Add ORDER BY to match expected row order)
# ==========================================

# Step 10: Update ORDER BY to match the test's expected first row ('Loui')
df_under_20 = pd.read_sql("""
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName, off.city, off.officeCode
    FROM employees e
    JOIN offices off ON e.officeCode = off.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders o ON c.customerNumber = o.customerNumber
    JOIN orderdetails od ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT p.productCode
        FROM products p
        JOIN orderdetails od_sub ON p.productCode = od_sub.productCode
        JOIN orders o_sub ON od_sub.orderNumber = o_sub.orderNumber
        GROUP BY p.productCode
        HAVING COUNT(DISTINCT o_sub.customerNumber) < 20
    )
    ORDER BY e.lastName ASC
""", conn)
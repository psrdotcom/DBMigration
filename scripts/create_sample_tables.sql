-- Sample Oracle Tables for Migration Testing
-- Connect as: testuser/testpass@localhost:1521/XEPDB1

-- Drop tables if they exist
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE order_items CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE orders CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE products CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE customers CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE employees CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE departments CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

-- Create DEPARTMENTS table
CREATE TABLE departments (
    department_id NUMBER(10) PRIMARY KEY,
    department_name VARCHAR2(100) NOT NULL,
    location VARCHAR2(100),
    created_date DATE DEFAULT SYSDATE
);

-- Create EMPLOYEES table
CREATE TABLE employees (
    employee_id NUMBER(10) PRIMARY KEY,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) UNIQUE,
    phone_number VARCHAR2(20),
    hire_date DATE DEFAULT SYSDATE,
    salary NUMBER(10,2),
    department_id NUMBER(10),
    manager_id NUMBER(10),
    is_active NUMBER(1) DEFAULT 1,
    CONSTRAINT fk_emp_dept FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT fk_emp_manager FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Create CUSTOMERS table
CREATE TABLE customers (
    customer_id NUMBER(10) PRIMARY KEY,
    customer_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) UNIQUE,
    phone VARCHAR2(20),
    address VARCHAR2(200),
    city VARCHAR2(50),
    state VARCHAR2(50),
    zip_code VARCHAR2(10),
    country VARCHAR2(50) DEFAULT 'USA',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create PRODUCTS table
CREATE TABLE products (
    product_id NUMBER(10) PRIMARY KEY,
    product_name VARCHAR2(100) NOT NULL,
    description CLOB,
    category VARCHAR2(50),
    price NUMBER(10,2) NOT NULL,
    stock_quantity NUMBER(10) DEFAULT 0,
    is_active NUMBER(1) DEFAULT 1,
    created_date DATE DEFAULT SYSDATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ORDERS table
CREATE TABLE orders (
    order_id NUMBER(10) PRIMARY KEY,
    customer_id NUMBER(10) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMBER(12,2),
    status VARCHAR2(20) DEFAULT 'PENDING',
    shipping_address VARCHAR2(200),
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create ORDER_ITEMS table
CREATE TABLE order_items (
    order_item_id NUMBER(10) PRIMARY KEY,
    order_id NUMBER(10) NOT NULL,
    product_id NUMBER(10) NOT NULL,
    quantity NUMBER(10) NOT NULL,
    unit_price NUMBER(10,2) NOT NULL,
    subtotal NUMBER(12,2),
    CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_item_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes
CREATE INDEX idx_emp_dept ON employees(department_id);
CREATE INDEX idx_emp_manager ON employees(manager_id);
CREATE INDEX idx_order_customer ON orders(customer_id);
CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_item_order ON order_items(order_id);
CREATE INDEX idx_item_product ON order_items(product_id);

-- Insert sample data
-- Departments
INSERT INTO departments VALUES (1, 'Sales', 'New York', SYSDATE);
INSERT INTO departments VALUES (2, 'Engineering', 'San Francisco', SYSDATE);
INSERT INTO departments VALUES (3, 'Marketing', 'Los Angeles', SYSDATE);
INSERT INTO departments VALUES (4, 'HR', 'Chicago', SYSDATE);
INSERT INTO departments VALUES (5, 'Finance', 'Boston', SYSDATE);

-- Employees
INSERT INTO employees VALUES (1, 'John', 'Doe', 'john.doe@example.com', '555-0101', SYSDATE-1000, 75000, 2, NULL, 1);
INSERT INTO employees VALUES (2, 'Jane', 'Smith', 'jane.smith@example.com', '555-0102', SYSDATE-900, 85000, 2, 1, 1);
INSERT INTO employees VALUES (3, 'Bob', 'Johnson', 'bob.johnson@example.com', '555-0103', SYSDATE-800, 65000, 1, 1, 1);
INSERT INTO employees VALUES (4, 'Alice', 'Williams', 'alice.williams@example.com', '555-0104', SYSDATE-700, 70000, 3, 1, 1);
INSERT INTO employees VALUES (5, 'Charlie', 'Brown', 'charlie.brown@example.com', '555-0105', SYSDATE-600, 60000, 4, 1, 1);
INSERT INTO employees VALUES (6, 'Diana', 'Davis', 'diana.davis@example.com', '555-0106', SYSDATE-500, 90000, 5, 1, 1);
INSERT INTO employees VALUES (7, 'Eve', 'Miller', 'eve.miller@example.com', '555-0107', SYSDATE-400, 72000, 2, 2, 1);
INSERT INTO employees VALUES (8, 'Frank', 'Wilson', 'frank.wilson@example.com', '555-0108', SYSDATE-300, 68000, 1, 3, 1);

-- Customers
INSERT INTO customers VALUES (1, 'Acme Corp', 'contact@acme.com', '555-1001', '123 Main St', 'New York', 'NY', '10001', 'USA', CURRENT_TIMESTAMP);
INSERT INTO customers VALUES (2, 'TechStart Inc', 'info@techstart.com', '555-1002', '456 Tech Ave', 'San Francisco', 'CA', '94102', 'USA', CURRENT_TIMESTAMP);
INSERT INTO customers VALUES (3, 'Global Solutions', 'sales@global.com', '555-1003', '789 Business Blvd', 'Chicago', 'IL', '60601', 'USA', CURRENT_TIMESTAMP);
INSERT INTO customers VALUES (4, 'Innovation Labs', 'hello@innovation.com', '555-1004', '321 Innovation Dr', 'Austin', 'TX', '73301', 'USA', CURRENT_TIMESTAMP);
INSERT INTO customers VALUES (5, 'Enterprise Systems', 'contact@enterprise.com', '555-1005', '654 Enterprise Way', 'Seattle', 'WA', '98101', 'USA', CURRENT_TIMESTAMP);

-- Products
INSERT INTO products VALUES (1, 'Laptop Pro 15', 'High-performance laptop with 15-inch display', 'Electronics', 1299.99, 50, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (2, 'Wireless Mouse', 'Ergonomic wireless mouse', 'Accessories', 29.99, 200, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (3, 'USB-C Hub', '7-in-1 USB-C hub with multiple ports', 'Accessories', 49.99, 150, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (4, 'Monitor 27"', '4K Ultra HD 27-inch monitor', 'Electronics', 399.99, 75, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (5, 'Keyboard Mechanical', 'RGB mechanical gaming keyboard', 'Accessories', 129.99, 100, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (6, 'Webcam HD', '1080p HD webcam with microphone', 'Electronics', 79.99, 120, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (7, 'Desk Lamp LED', 'Adjustable LED desk lamp', 'Office', 39.99, 80, 1, SYSDATE, CURRENT_TIMESTAMP);
INSERT INTO products VALUES (8, 'Office Chair', 'Ergonomic office chair with lumbar support', 'Furniture', 299.99, 40, 1, SYSDATE, CURRENT_TIMESTAMP);

-- Orders
INSERT INTO orders VALUES (1, 1, CURRENT_TIMESTAMP-30, 1679.97, 'COMPLETED', '123 Main St, New York, NY 10001');
INSERT INTO orders VALUES (2, 2, CURRENT_TIMESTAMP-25, 579.97, 'COMPLETED', '456 Tech Ave, San Francisco, CA 94102');
INSERT INTO orders VALUES (3, 3, CURRENT_TIMESTAMP-20, 1829.96, 'SHIPPED', '789 Business Blvd, Chicago, IL 60601');
INSERT INTO orders VALUES (4, 1, CURRENT_TIMESTAMP-15, 429.98, 'PROCESSING', '123 Main St, New York, NY 10001');
INSERT INTO orders VALUES (5, 4, CURRENT_TIMESTAMP-10, 1699.98, 'PENDING', '321 Innovation Dr, Austin, TX 73301');
INSERT INTO orders VALUES (6, 5, CURRENT_TIMESTAMP-5, 209.97, 'COMPLETED', '654 Enterprise Way, Seattle, WA 98101');

-- Order Items
INSERT INTO order_items VALUES (1, 1, 1, 1, 1299.99, 1299.99);
INSERT INTO order_items VALUES (2, 1, 2, 2, 29.99, 59.98);
INSERT INTO order_items VALUES (3, 1, 3, 1, 49.99, 49.99);
INSERT INTO order_items VALUES (4, 1, 5, 2, 129.99, 259.98);

INSERT INTO order_items VALUES (5, 2, 4, 1, 399.99, 399.99);
INSERT INTO order_items VALUES (6, 2, 6, 1, 79.99, 79.99);
INSERT INTO order_items VALUES (7, 2, 7, 1, 39.99, 39.99);
INSERT INTO order_items VALUES (8, 2, 2, 2, 29.99, 59.98);

INSERT INTO order_items VALUES (9, 3, 1, 1, 1299.99, 1299.99);
INSERT INTO order_items VALUES (10, 3, 4, 1, 399.99, 399.99);
INSERT INTO order_items VALUES (11, 3, 5, 1, 129.99, 129.99);

INSERT INTO order_items VALUES (12, 4, 8, 1, 299.99, 299.99);
INSERT INTO order_items VALUES (13, 4, 5, 1, 129.99, 129.99);

INSERT INTO order_items VALUES (14, 5, 1, 1, 1299.99, 1299.99);
INSERT INTO order_items VALUES (15, 5, 4, 1, 399.99, 399.99);

INSERT INTO order_items VALUES (16, 6, 7, 3, 39.99, 119.97);
INSERT INTO order_items VALUES (17, 6, 2, 3, 29.99, 89.97);

COMMIT;

-- Display summary
SELECT 'Departments' AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'Employees', COUNT(*) FROM employees
UNION ALL
SELECT 'Customers', COUNT(*) FROM customers
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Orders', COUNT(*) FROM orders
UNION ALL
SELECT 'Order_Items', COUNT(*) FROM order_items;

PROMPT
PROMPT ✓ Sample tables created successfully!
PROMPT
PROMPT Tables created:
PROMPT   - DEPARTMENTS (5 rows)
PROMPT   - EMPLOYEES (8 rows)
PROMPT   - CUSTOMERS (5 rows)
PROMPT   - PRODUCTS (8 rows)
PROMPT   - ORDERS (6 rows)
PROMPT   - ORDER_ITEMS (17 rows)
PROMPT
PROMPT Total: 6 tables with 49 rows
PROMPT

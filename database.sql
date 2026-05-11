-- ============================================================
--  Fashion Store Inventory — Fixed Database Setup
--  Fix: Removed emoji default values (MySQL strict mode fix)
-- ============================================================

CREATE DATABASE IF NOT EXISTS fashion_inventory;
USE fashion_inventory;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id         INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(80)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123')
ON DUPLICATE KEY UPDATE username = username;

-- CATEGORIES TABLE (fixed: empty string default instead of emoji)
CREATE TABLE IF NOT EXISTS categories (
    id          INT          NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    icon        VARCHAR(20)  DEFAULT '',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO categories (name, description, icon) VALUES
    ('Dresses',        'Casual, formal and party dresses',   'dress'),
    ('Tops & Blouses', 'Shirts, blouses and crop tops',      'top'),
    ('Bottoms',        'Jeans, skirts, trousers and shorts', 'bottom'),
    ('Traditional',    'Sarees, kurtis and ethnic wear',     'traditional'),
    ('Winter Wear',    'Jackets, sweaters and coats',        'winter'),
    ('Accessories',    'Bags, belts, scarves and jewellery', 'accessory'),
    ('Footwear',       'Heels, flats, sandals and sneakers', 'footwear'),
    ('Gifts',          'Gift sets, hampers and vouchers',    'gift')
ON DUPLICATE KEY UPDATE name = name;

-- PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    id          INT            NOT NULL AUTO_INCREMENT,
    name        VARCHAR(120)   NOT NULL,
    category_id INT            NOT NULL,
    price       DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    quantity    INT            NOT NULL DEFAULT 0,
    size        VARCHAR(50)    DEFAULT 'Free Size',
    color       VARCHAR(50)    DEFAULT '',
    sku         VARCHAR(50)    DEFAULT '',
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO products (name, category_id, price, quantity, size, color, sku) VALUES
    ('Floral Wrap Dress',     1,  1299.00, 20, 'S,M,L',    'Red',    'DR001'),
    ('Evening Gown Black',    1,  3499.00,  5, 'M,L,XL',   'Black',  'DR002'),
    ('Casual Sundress',       1,   899.00,  3, 'S,M',      'Yellow', 'DR003'),
    ('Cotton Crop Top',       2,   499.00, 30, 'XS,S,M,L', 'White',  'TP001'),
    ('Silk Blouse',           2,  1199.00,  4, 'S,M,L',    'Ivory',  'TP002'),
    ('High Waist Jeans',      3,  1599.00, 15, '28,30,32', 'Blue',   'BT001'),
    ('Pleated Mini Skirt',    3,   799.00,  2, 'S,M,L',    'Pink',   'BT002'),
    ('Banarasi Silk Saree',   4,  5999.00,  8, 'Free',     'Purple', 'TR001'),
    ('Anarkali Kurti',        4,  1499.00, 12, 'S,M,L,XL', 'Green',  'TR002'),
    ('Woolen Overcoat',       5,  3999.00,  6, 'M,L,XL',   'Camel',  'WW001'),
    ('Puffer Jacket',         5,  2499.00,  3, 'S,M,L',    'Navy',   'WW002'),
    ('Leather Tote Bag',      6,  2199.00, 10, 'One Size',  'Tan',    'AC001'),
    ('Pearl Necklace Set',    6,   999.00,  2, 'One Size',  'White',  'AC002'),
    ('Block Heel Sandals',    7,  1299.00,  9, '36-41',    'Gold',   'FW001'),
    ('White Sneakers',        7,  1799.00,  4, '36-42',    'White',  'FW002'),
    ('Luxury Gift Hamper',    8,  2999.00,  7, 'One Size',  'Mixed',  'GF001'),
    ('Festive Gift Set',      8,  1499.00,  1, 'One Size',  'Mixed',  'GF002');

-- BILLS TABLE
CREATE TABLE IF NOT EXISTS bills (
    id               INT            NOT NULL AUTO_INCREMENT,
    invoice_number   VARCHAR(20)    NOT NULL UNIQUE,
    customer_name    VARCHAR(120)   NOT NULL,
    customer_phone   VARCHAR(20)    DEFAULT '',
    customer_email   VARCHAR(120)   DEFAULT '',
    customer_address TEXT,
    subtotal         DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    gst_rate         DECIMAL(5,2)   NOT NULL DEFAULT 5.00,
    gst_amount       DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    discount         DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    total            DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    payment_method   VARCHAR(30)    DEFAULT 'Cash',
    status           VARCHAR(20)    DEFAULT 'Paid',
    created_at       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- BILL ITEMS TABLE
CREATE TABLE IF NOT EXISTS bill_items (
    id           INT            NOT NULL AUTO_INCREMENT,
    bill_id      INT            NOT NULL,
    product_id   INT            NOT NULL,
    product_name VARCHAR(120)   NOT NULL,
    quantity     INT            NOT NULL DEFAULT 1,
    unit_price   DECIMAL(10,2)  NOT NULL,
    total_price  DECIMAL(10,2)  NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (bill_id)    REFERENCES bills(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

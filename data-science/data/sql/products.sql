
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
INSERT INTO products (id, name) VALUES
(0, 'Laptop'),
(1, 'Smartphone'),
(2, 'Camera'),
(3, 'Cosmetics'),
(4, 'Handbag'),
(5, 'Shoes'),
(6, 'TV'),
(7, 'Perfume'),
(8, 'Watch'),
(9, 'Clothes');

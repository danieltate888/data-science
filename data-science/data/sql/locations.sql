
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
INSERT INTO locations (id, name) VALUES
(0, 'Sydney'),
(1, 'Melbourne'),
(2, 'Brisbane'),
(3, 'Perth'),
(4, 'Adelaide'),
(5, 'Hobart'),
(6, 'Darwin'),
(7, 'Canberra');

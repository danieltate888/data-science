
            DROP TABLE IF EXISTS occupations;
            CREATE TABLE occupations (
                                         id INT PRIMARY KEY,
                                         name VARCHAR(100)
            );
            INSERT INTO occupations (id, name) VALUES
            (0, 'Engineer'),
(1, 'Artist'),
(2, 'Doctor'),
(3, 'Teacher'),
(4, 'Sales'),
(5, 'Lawyer'),
(6, 'Scientist'),
(7, 'Accountant'),
(8, 'Nurse'),
(9, 'Software Developer');

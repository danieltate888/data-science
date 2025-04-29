
            DROP TABLE IF EXISTS genders;
            CREATE TABLE genders (
                                     id INT PRIMARY KEY,
                                     name VARCHAR(50)
            );
            INSERT INTO genders (id, name) VALUES
                                               (0, 'Male'),
                                               (1, 'Female');
            
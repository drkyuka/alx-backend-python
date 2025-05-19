-- SQLite script to create users table and populate with sample data

-- Create the users table with proper fields
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Delete existing data if any (to avoid duplicates when running multiple times)
DELETE FROM users;

-- Reset the autoincrement counter
DELETE FROM sqlite_sequence WHERE name='users';

-- Insert sample data into the users TABLE
INSERT INTO users (firstname, lastname, username, email) VALUES
('John', 'Doe', 'johndoe', 'johndoe@example.com'),
('Jane', 'Smith', 'janesmith', 'janesmith@example.com'),
('Alice', 'Johnson', 'alicejohnson', 'alicejohnson@example.net'),
('Bob', 'Brown', 'bobbrown', 'Bobbrown@example.org'),
('Charlie', 'Davis', 'charliedavis', 'charliedavis@example.link'),
('Diana', 'Evans', 'dianaevans', 'dianaevans@example.edu'),
('Ethan', 'Garcia', 'ethangarcia', 'ethangarcia@example.co.ng'),
('Fiona', 'Harris', 'fionaharris', 'fionaharris@example.co.uk'),
('George', 'Martinez', 'georgemartinez', 'georgemartinez@example.nz');
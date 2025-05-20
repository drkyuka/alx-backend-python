-- create a new column `age` in the users table using sqlite3
ALTER TABLE `users` ADD COLUMN `age` INTEGER NOT NULL DEFAULT 0;

-- Update the age column for all users (example: set random ages between 18 and 65)
UPDATE users SET age = 25 WHERE id = 1;
UPDATE users SET age = 32 WHERE id = 2;
UPDATE users SET age = 41 WHERE id = 3;
UPDATE users SET age = 29 WHERE id = 4;
UPDATE users SET age = 54 WHERE id = 5;
UPDATE users SET age = 22 WHERE id = 6;
UPDATE users SET age = 37 WHERE id = 7;
UPDATE users SET age = 45 WHERE id = 8;
UPDATE users SET age = 28 WHERE id = 9;
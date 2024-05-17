CREATE DATABASE IF NOT EXISTS Stock;
CREATE USER IF NOT EXISTS 'stock_db'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON Stock .* TO 'stock_db'@'localhost';
GRANT SELECT ON `performance_schema` .* TO 'stock_db'@'localhost';
FLUSH PRIVILEGES;
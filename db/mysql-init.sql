CREATE DATABASE IF NOT EXISTS testdb;
USE testdb;

CREATE TABLE IF NOT EXISTS prices (
    id int AUTO_INCREMENT PRIMARY KEY, 
    title varchar(255), 
    price varchar(255), 
    image_url varchar(900), 
    product_url varchar(900), 
    seller varchar(255)
);

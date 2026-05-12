CREATE DATABASE IF NOT EXISTS veg_restaurant_db;
USE veg_restaurant_db;

CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',
    total_amount DECIMAL(10, 2),
    order_type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    menu_item_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    reservation_time DATETIME,
    num_guests INT,
    special_requests TEXT,
    status VARCHAR(50) DEFAULT 'Confirmed'
);

CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    user_message TEXT,
    bot_response TEXT,
    intent_tag VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert 10 sample vegetarian menu items
INSERT INTO menu_items (name, category, description, price, is_available) VALUES
('Paneer Tikka', 'starters', 'Marinated cottage cheese grilled in a tandoor', 250.00, TRUE),
('Samosa Chaat', 'starters', 'Crushed samosas topped with yogurt, chutneys, and spices', 120.00, TRUE),
('Veg Spring Rolls', 'starters', 'Crispy rolls stuffed with mixed vegetables', 150.00, TRUE),
('Dal Makhani', 'mains', 'Black lentils cooked overnight with butter and cream', 280.00, TRUE),
('Palak Paneer', 'mains', 'Cottage cheese cubes in a creamy spinach gravy', 300.00, TRUE),
('Vegetable Biryani', 'mains', 'Fragrant basmati rice cooked with mixed vegetables and spices', 320.00, TRUE),
('Gulab Jamun', 'desserts', 'Deep-fried milk dumplings soaked in sugar syrup', 80.00, TRUE),
('Rasmalai', 'desserts', 'Cottage cheese patties in sweetened, thickened milk', 100.00, TRUE),
('Mango Lassi', 'drinks', 'Sweet and creamy yogurt-based mango drink', 90.00, TRUE),
('Masala Chai', 'drinks', 'Traditional Indian spiced tea', 40.00, TRUE);

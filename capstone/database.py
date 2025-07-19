import sqlite3
import random
import string
import pytz
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='main.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection with foreign keys enabled"""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def init_database(self):
        """Initialize the database with the provided schema"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Clients Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                client_email TEXT,
                client_address TEXT,
                client_contactnum TEXT
            )
        """)
        
        # Products Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                materials TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Orders Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                order_name TEXT,
                product_id TEXT,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                order_dl TEXT,
                order_quantity INTEGER,
                client_id TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        """)
        
        # Insert sample clients if none exist
        c.execute("SELECT COUNT(*) FROM clients")
        if c.fetchone()[0] == 0:
            sample_clients = [
                ('CLIENT_001', 'John Doe', 'john@email.com', '123 Main St', '555-0101'),
                ('CLIENT_002', 'Jane Smith', 'jane@email.com', '456 Oak Ave', '555-0102'),
                ('CLIENT_003', 'Bob Johnson', 'bob@email.com', '789 Pine Rd', '555-0103'),
                ('CLIENT_004', 'Alice Brown', 'alice@email.com', '321 Elm St', '555-0104'),
                ('CLIENT_005', 'Charlie Wilson', 'charlie@email.com', '654 Maple Dr', '555-0105')
            ]
            c.executemany("INSERT INTO clients VALUES (?, ?, ?, ?, ?)", sample_clients)
        
        conn.commit()
        conn.close()
    
    def generate_product_id(self):
        """Generate a random product ID"""
        return 'PROD_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def generate_order_id(self):
        """Generate a random order ID"""
        return 'ORDER_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Product-related database operations
    def create_product(self, product_name, materials_list):
        """Create a new product in the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        product_id = self.generate_product_id()
        materials_str = "; ".join(materials_list)
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("""
            INSERT INTO products (product_id, product_name, materials, created_date)
            VALUES (?, ?, ?, ?)
        """, (product_id, product_name, materials_str, timestamp))
        
        conn.commit()
        conn.close()
        return product_id
    
    def get_all_products(self):
        """Get all products from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT product_id, product_name, materials, created_date FROM products ORDER BY created_date DESC")
        products = c.fetchall()
        
        conn.close()
        return products
    
    def get_product_by_id(self, product_id):
        """Get a specific product by ID"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT product_id, product_name, materials, created_date FROM products WHERE product_id = ?", (product_id,))
        product = c.fetchone()
        
        conn.close()
        return product
    
    def get_product_materials(self, product_id):
        """Get materials for a specific product"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT materials FROM products WHERE product_id = ?", (product_id,))
        result = c.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def update_product(self, product_id, product_name, materials):
        """Update an existing product"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""
            UPDATE products 
            SET product_name = ?, materials = ?
            WHERE product_id = ?
        """, (product_name, materials, product_id))
        
        conn.commit()
        conn.close()
    
    def delete_product(self, product_id):
        """Delete a product from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        
        conn.commit()
        conn.close()
    
    def check_product_in_orders(self, product_id):
        """Check if a product is used in any orders"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM orders WHERE product_id = ?", (product_id,))
        count = c.fetchone()[0]
        
        conn.close()
        return count
    
    def get_products_for_dropdown(self):
        """Get products formatted for dropdown display"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT product_id, product_name FROM products ORDER BY product_name")
        products = c.fetchall()
        
        conn.close()
        return [f"{product[1]} ({product[0]})" for product in products]
    
    # Client-related database operations
    def get_all_clients(self):
        """Get all clients from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT client_id, client_name, client_email, client_address, client_contactnum FROM clients ORDER BY client_name")
        clients = c.fetchall()
        
        conn.close()
        return clients
    
    def get_clients_for_dropdown(self):
        """Get clients formatted for dropdown display"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT client_id, client_name FROM clients ORDER BY client_name")
        clients = c.fetchall()
        
        conn.close()
        return [f"{client[1]} ({client[0]})" for client in clients]
    
    # Order-related database operations
    def create_order(self, order_name, product_id, client_id, quantity, deadline):
        """Create a new order in the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        order_id = self.generate_order_id()
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("""
            INSERT INTO orders (order_id, order_name, product_id, order_date, order_dl, 
                              order_quantity, client_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_id, order_name, product_id,  timestamp, deadline, 
              quantity, client_id))
        
        conn.commit()
        conn.close()
        return order_id
    
    def get_all_orders(self):
        """Get all orders with related product and client information"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT o.order_id, o.order_name, p.product_name, c.client_name, 
                   o.order_quantity, o.order_dl, o.order_date, o.product_id, o.client_id
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.product_id
            LEFT JOIN clients c ON o.client_id = c.client_id
            ORDER BY o.order_date DESC
        """)
        orders = c.fetchall()
        
        conn.close()
        return orders
    
    def get_order_by_id(self, order_id):
        """Get a specific order by ID"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT o.order_id, o.order_name, o.product_id, o.client_id, 
                   o.order_quantity, o.order_dl, o.order_date
            FROM orders o
            WHERE o.order_id = ?
        """, (order_id,))
        order = c.fetchone()
        
        conn.close()
        return order
    
    def update_order(self, order_id, order_name, product_id, client_id, quantity, deadline):
        """Update an existing order"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""
            UPDATE orders 
            SET order_name = ?, product_id = ?, client_id = ?, 
                order_quantity = ?, order_dl = ?
            WHERE order_id = ?
        """, (order_name, product_id, client_id, quantity, deadline, order_id))
        
        conn.commit()
        conn.close()
    
    def delete_order(self, order_id):
        """Delete an order from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        
        conn.commit()
        conn.close()
    
    # Utility methods
    def close_connection(self):
        """Close database connection (if needed for cleanup)"""
        pass  # SQLite connections are closed automatically in our implementation
    
    def execute_custom_query(self, query, params=None):
        """Execute a custom query (for advanced operations)"""
        conn = self.get_connection()
        c = conn.cursor()
        
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = c.fetchall()
        else:
            conn.commit()
            result = c.rowcount
        
        conn.close()
        return result

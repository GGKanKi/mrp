import sqlite3
import random
import string
import pytz
import logging
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_name='main.db'):
        self.db_name = db_name
        self.init_database()

    #Loggers
    logging.basicConfig(filename='D:/capstone/log_f/products.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    #Global Time Var
    timezone = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')

    def get_connection(self):
        """Get database connection with foreign keys enabled"""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def init_database(self):
        """Initialize the database with the provided schema"""
        conn = self.get_connection()
        c = conn.cursor()
        

        conn.commit()
        conn.close()
    
    def generate_product_id(self):
        """Generate a more unique order ID using timestamp and randomness"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{timestamp}-{random_str}"

    
    def generate_order_id(self):
        """Generate a more unique order ID using timestamp and randomness"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{timestamp}-{random_str}"
    
    def order_id_exists(self, order_id):
        """Check if an order ID already exists"""
        conn = self.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,))
            return c.fetchone() is not None
        finally:
            conn.close()

    
    # Product-related database operations
    def create_product(self, product_name, materials_list):
        """Create a new product in the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        product_id = self.generate_product_id()
        materials_str = "; ".join(materials_list)
        
        c.execute("""
            INSERT INTO products (product_id, product_name, materials, created_date)
            VALUES (?, ?, ?, ?)
        """, (product_id, product_name, materials_str, self.timezone))
        
        conn.commit()
        conn.close()
        logging.info(f'Product {product_id} created succesfully, Time: {self.timezone}')
        return product_id
    
    def get_all_products(self):
        """Get all products from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT * FROM products ORDER BY created_date DESC")
        products = c.fetchall()
        
        conn.close()
        return products
    
    def get_product_by_id(self, product_id):
        """Get a specific product by ID"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
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
        logging.info(f'Product {product_id} updated successfully, Time: {self.timezone}')
    
    #To Be Implemented
    def approved_status(self, product_id, status):
        """Update the status of a product"""
        conn = self.get_connection()
        c = conn.cursor()

        status = 'Approved'
        
        c.execute("UPDATE products SET status_quo = ? WHERE product_id = ?", (status, product_id))
        
        conn.commit()
        conn.close()
        logging.info(f'Product {product_id} status updated to {status}. Time: {self.timezone}')

    def cancel_status(self, product_id, status):
        """Soft Deletion of a product(Cancel - possibility to be approved later)"""
        conn = self.get_connection()
        c = conn.cursor()

        status = 'Cancelled'

        c.execute("UPDATE products SET stauts_quo = ? WHERE product_id = ?", (status, product_id))

        conn.commit()
        conn.close()
        logging.info(f"Product {product_id} has been cancelled. Time: {self.timezone}")
    
    
    def delete_product(self, product_id):
        """Delete a product from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        logging.warning(f'Product {product_id} deleted from database. Time: {self.timezone}')
        
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
    

    def create_order(self, order_name, product_id, client_id, quantity, deadline, total_mats_dict):
        """Create a new order with robust error handling"""
        conn = None
        try:
            # Validate materials data
            if not isinstance(total_mats_dict, dict):
                if isinstance(total_mats_dict, str):
                    try:
                        total_mats_dict = json.loads(total_mats_dict)
                    except json.JSONDecodeError:
                        raise ValueError("Materials data must be a dictionary or valid JSON string")
                else:
                    raise ValueError("Materials data must be a dictionary")

            # Convert quantities to numbers
            validated_materials = {}
            for material, qty in total_mats_dict.items():
                try:
                    validated_materials[material] = float(qty) if '.' in str(qty) else int(qty)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid quantity for {material}")

            # Generate unique order ID
            max_attempts = 3
            order_id = None
            
            for attempt in range(max_attempts):
                order_id = self.generate_order_id()
                if not self.order_id_exists(order_id):
                    break
            else:
                raise RuntimeError("Failed to generate unique order ID after 3 attempts")

            # Create order with transaction
            conn = self.get_connection()
            c = conn.cursor()
            
            c.execute("BEGIN TRANSACTION")
            c.execute("""
                INSERT INTO orders (order_id, order_name, product_id, client_id, 
                                quantity, deadline, order_date, mats_need)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, order_name, product_id, client_id, 
                quantity, deadline, self.timezone, json.dumps(validated_materials)))
            
            conn.commit()
            logging.info(f'Order {order_id} created successfully')
            return order_id

        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            logging.error(f"Database integrity error: {str(e)}")
            raise ValueError("Order creation failed - possible duplicate ID") from e
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Order creation error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_all_orders(self):
        """Get all orders with related product and client information"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT o.order_id, o.order_name, p.product_name, c.client_name, 
                   o.quantity, o.mats_need, o.deadline, o.order_date, o.product_id, o.client_id, o.status_quo
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
                   o.quantity, o.deadline, o.order_date, o.status_quo
            FROM orders o
            WHERE o.order_id
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
                quantity = ?, deadline = ?
            WHERE order_id = ?
        """, (order_name, product_id, client_id, quantity, deadline, order_id))
        
        conn.commit()
        conn.close()
        logging.info(f'Order {order_id} updated. Time: {self.timezone}')

    #To be Implemented
    def approve_order(self, order_id):
        """Update the stauts of the pending order"""
        conn = self.get_connection()
        c = conn.cursor()

        status = "Approved"

        c.execute('UPDATE orders SET status_quo WHERE order_id = ?', (status, order_id))

        conn.commit()
        conn.close()
        logging.info(f"Order {order_id} has been approved, Time: {self.timezone}")

    #To Be Implemented
    def cancel_order(self, order_id):
        """Soft Deletion of an order (Cancel - possibility to be approved later)"""
        conn = self.get_connection()
        c = conn.cursor()

        status = "Cancelled"

        c.execute("UPDATE orders SET status_quo = ? WHERE order_id = ?", (status, order_id))
        
        conn.commit()
        conn.close()
        logging.info(f"Order {order_id} has been cancelled, Time: {self.timezone}")
    
    def delete_order(self, order_id):
        """Delete an order from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        
        conn.commit()
        conn.close()
        logging.info(f"Order {order_id} deleted from Database, Time: {self.timezone}")
    
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

import sqlite3
import random
import string
import pytz
import logging
from datetime import datetime
import json
from tkinter import messagebox

import os, math


class DatabaseManager:
    def __init__(self, db_name='main.db', session=None): 
        # Use a resource_path helper to ensure the DB is found in the bundled app
        from global_func import resource_path 
        self.db_name = resource_path(db_name)
        self.session = session if session is not None else {}
        self.init_database()
        self.usertype = self.session.get('usertype', 'guest') 
    def refresh_connection(self):
        """Refresh the database connection to ensure fresh data"""
        # Close existing connection if it exists
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        
        # Reinitialize the database connection
        self.init_database()

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
    def create_product(self, product_name, materials_list, manufacturing_time):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to create a product.")
            return None

        """Create a new product in the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        product_id = self.generate_product_id()
        materials_str = "; ".join(materials_list)
        is_active_status = 1  # Assuming new products are active by default
        
        c.execute("""
            INSERT INTO products (product_id, product_name, materials, created_date, manufacturing_time_hours, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, product_name, materials_str, self.timezone, manufacturing_time, is_active_status))
         # Log the creation in user_logs
        
        conn.commit()
        conn.close()
        logging.info(f'Product {product_id} created succesfully, Time: {self.timezone}')
        return product_id
    
    def get_all_products(self):
        """Get all products from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT product_id, product_name, materials, created_date, manufacturing_time_hours, status_quo FROM products WHERE is_active = 1 ORDER BY created_date DESC")
        products = c.fetchall()
        
        conn.close()
        return products
    
    def find_similar_products(self, product_name):
        """
        Finds products with names similar to the given product_name.
        Returns a list of tuples, where each tuple is (product_id, materials_string).
        """
        if not product_name:
            return []

        # Split the product name into keywords
        keywords = product_name.split()
        if not keywords:
            return []

        # Build the query dynamically
        query = "SELECT product_id, materials FROM products WHERE is_active = 1 AND ("
        conditions = []
        params = []
        for keyword in keywords:
            if len(keyword) > 2:
                conditions.append("product_name LIKE ?")
                params.append(f'%{keyword}%')

        if not conditions:
            return []

        query += " OR ".join(conditions)
        query += ") LIMIT 10" # Limit to 10 similar products to avoid overload

        return self.execute_custom_query(query, tuple(params))
    

    def get_product_creator(self, product_id):
        """Get the name of the user who created a specific product"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Find the user who created this product from user_logs
        c.execute("""
            SELECT u.f_name, u.l_name, u.username 
            FROM user_logs ul
            JOIN users u ON ul.user_id = u.user_id
            WHERE ul.action LIKE ? 
            ORDER BY ul.timestamp ASC
            LIMIT 1
        """, (f'CREATE PRODUCT {product_id}%',))
        
        creator = c.fetchone()
        conn.close()
        
        if creator:
            if creator[0] and creator[1]:  # If first and last name are available
                return f"{creator[0]} {creator[1]}"
            else:  # Fall back to username
                return creator[2]
        return "Unknown"
    
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
    
    def get_product_manufacturing_time(self, product_id):
        """Get manufacturing time for a specific product."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT manufacturing_time_hours FROM products WHERE product_id = ?", (product_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    
    def update_product(self, product_id, product_name, materials, manufacturing_time):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to create a product.")
            return None

        try:
            """Update an existing product"""
            conn = self.get_connection()
            c = conn.cursor()
            
            c.execute("""
                UPDATE products
                SET product_name = ?, materials = ?, manufacturing_time_hours = ?
                WHERE product_id = ?
            """, (product_name, materials, manufacturing_time, product_id))
            
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            logging.info(f'Product {product_id} updated successfully, Time: {self.timezone}')
    
    #To Be Implemented
    def approved_status(self, product_id, status):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to create a product.")
            return

        try:        
            """Update the status of a product"""
            conn = self.get_connection()
            c = conn.cursor()

            status = 'Approved'
            
            c.execute("UPDATE products SET status_quo = ? WHERE product_id = ?", (status, product_id))
        
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            logging.info(f'Product {product_id} status updated to {status}. Time: {self.timezone}')

    def cancel_status(self, product_id, status):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to create a product.")
            return
        
        try:
            """Soft Deletion of a product(Cancel - possibility to be approved later)"""
            conn = self.get_connection()
            c = conn.cursor()

            status = 'Cancelled'

            c.execute("UPDATE products SET stauts_quo = ? WHERE product_id = ?", (status, product_id))

            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            logging.info(f"Product {product_id} has been cancelled. Time: {self.timezone}")
    
    
    def delete_product(self, product_id):
        # Permission check
        usertype = self.session.get('usertype')
        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to delete a product.")
            return

        try:
            conn = self.get_connection()
            c = conn.cursor()

            # Check if product is linked to active orders
            c.execute("SELECT COUNT(*) FROM orders WHERE product_id = ? AND is_active = 1", (product_id,))
            order_count = c.fetchone()[0]

            if order_count > 0:
                messagebox.showwarning("Cannot Delete", f"Product ID '{product_id}' is linked to existing orders and cannot be deleted.")
                logging.warning(f"Attempt to delete product {product_id} linked to orders by {usertype}, Time: {self.timezone}")
                return

            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product ID '{product_id}'?")
            if not confirm:
                return

            # Soft delete (set inactive)
            in_active_val = 0
            c.execute("UPDATE products SET is_active = ? WHERE product_id = ?", (in_active_val, product_id))
            conn.commit()

            messagebox.showinfo("Deleted", f"Product ID '{product_id}' has been deleted.")
            logging.info(f"Product {product_id} deleted by {usertype}. Time: {self.timezone}")
                

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if conn:
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
        
        c.execute("SELECT product_id, product_name FROM products WHERE is_active = 1 ORDER BY product_name")
        products = c.fetchall()
        
        conn.close()
        return [f"{product[1]} ({product[0]})" for product in products]
    
    # Client-related database operations
    def get_all_clients(self):
        """Get all clients from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT client_id, client_name, client_email, client_address, client_contactnum FROM clients WHERE is_active = 1 ORDER BY client_name")
        clients = c.fetchall()
        
        conn.close()
        return clients
    
    def get_clients_for_dropdown(self):
        """Get clients formatted for dropdown display"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT client_id, client_name FROM clients WHERE is_active = 1 ORDER BY client_name")
        clients = c.fetchall()
        
        conn.close()
        return [f"{client[1]} ({client[0]})" for client in clients]
    

    def create_order(self, order_name, product_id, client_id, quantity, deadline, total_mats_dict, status="Pending"):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to create an order.")
            return
        
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
            is_active_status = 1  # Assuming new orders are active by default
            c.execute("BEGIN TRANSACTION")
            c.execute("""
                INSERT INTO orders (order_id, order_name, product_id, client_id,
                                quantity, deadline, order_date, mats_need, status_quo, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, order_name, product_id, client_id, 
                quantity, deadline, self.timezone, json.dumps(validated_materials), status, is_active_status))
            
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

    def check_material_availability(self, required_materials_dict):
        """
        Checks current stock for a dictionary of required materials.
        Returns a report dictionary with 'sufficient' and 'insufficient' items.
        """
        report = {'sufficient': [], 'insufficient': []}
        conn = self.get_connection()
        try:
            c = conn.cursor()
            for material_name, required_qty in required_materials_dict.items():
                c.execute("SELECT current_stock, supplier_id FROM raw_mats WHERE mat_name = ?", (material_name,))
                result = c.fetchone()

                if result:
                    available_qty, supplier_id = result
                    item_details = {'name': material_name, 'required': required_qty, 'available': available_qty, 'supplier_id': supplier_id}
                    if available_qty >= required_qty:
                        report['sufficient'].append(item_details)
                    else:
                        item_details['shortfall'] = required_qty - available_qty
                        report['insufficient'].append(item_details)
                else:
                    # Material not found in inventory at all
                    report['insufficient'].append({'name': material_name, 'required': required_qty, 'available': 0, 'shortfall': required_qty, 'supplier_id': None})
        finally:
            conn.close()
        return report

    def calculate_schedule_for_ui(self, product_id, quantity, deadline_str):
        """Calculates schedule details for the UI without saving to the DB."""
        from datetime import date, timedelta
        from product import ProductManagementSystem # To reuse parsing logic

        conn = self.get_connection()
        c = conn.cursor()
        try:
            # 1. Get Order Info (passed as arguments)

            # 2. Get Product Manufacturing Time
            mfg_time_info = c.execute("SELECT manufacturing_time_hours FROM products WHERE product_id = ?", (product_id,)).fetchone()
            if not mfg_time_info or not mfg_time_info[0]:
                raise ValueError(f"Manufacturing time not set for product {product_id}.")
            manufacturing_time_hours = mfg_time_info[0]

            # 3. Calculate Production Time
            total_production_hours = quantity * manufacturing_time_hours
            production_workdays = math.ceil(total_production_hours / 8.0) # Assume 8-hour workdays

            # 4. Find Production Start Date (considering workdays)
            deadline_date = datetime.strptime(deadline_str, '%m/%d/%Y').date()
            
            def subtract_workdays(start_date, days):
                workdays_to_subtract = days
                current_date = start_date
                while workdays_to_subtract > 0:
                    current_date -= timedelta(days=1)
                    if current_date.weekday() < 5: # Monday to Friday are 0-4
                        workdays_to_subtract -= 1
                return current_date

            production_start_date = subtract_workdays(deadline_date, production_workdays)
            production_end_date = deadline_date

            # 5. Check Materials and Find Order-By Date
            materials_string = self.get_product_materials(product_id)
            pms_instance = ProductManagementSystem(parent=None, show_only_list=True) # Dummy instance
            materials_dict = pms_instance.parse_materials(materials_string)
            required_materials = {name: qty * quantity for name, qty in materials_dict.items()}
            
            availability_report = self.check_material_availability(required_materials)
            
            material_order_by_date = None
            notes = "All materials are in stock."
            
            if availability_report['insufficient']:
                latest_order_by_date = None
                shortfall_notes = []
                for item in availability_report['insufficient']:
                    supplier_id = item.get('supplier_id')
                    if not supplier_id: continue
                    
                    # This is a simplification. A real system might have a separate supplier_lead_time table.
                    # For now, we'll add a 'lead_time_days' to the suppliers table.
                    # Let's assume a default lead time if not present.
                    lead_time_info = c.execute("SELECT lead_time_days FROM suppliers WHERE supplier_id = ?", (supplier_id,)).fetchone()
                    lead_time_days = lead_time_info[0] if lead_time_info and lead_time_info[0] is not None else 7 # Default to 7 days

                    order_by_date = production_start_date - timedelta(days=lead_time_days)
                    shortfall_notes.append(f"Shortfall of {item['shortfall']} of {item['name']} (Supplier Lead Time: {lead_time_days} days). Must order by {order_by_date.strftime('%Y-%m-%d')}.")

                    if latest_order_by_date is None or order_by_date < latest_order_by_date:
                        latest_order_by_date = order_by_date
                
                material_order_by_date = latest_order_by_date
                notes = "\n".join(shortfall_notes)

            # 6. Final Verdict & DB Update
            today = date.today()
            feasibility_status = 'Feasible'
            if material_order_by_date and material_order_by_date < today:
                feasibility_status = 'Infeasible' # Or 'At Risk'

            return {
                "feasibility": feasibility_status,
                "prod_start": production_start_date,
                "prod_end": production_end_date,
                "material_order": material_order_by_date,
                "notes": notes
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def save_schedule(self, order_id, schedule_info):
        """Saves a pre-calculated schedule to the database."""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO production_schedule (order_id, production_start_date, production_end_date, material_order_by_date, feasibility_status, notes, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(order_id) DO UPDATE SET
                    production_start_date=excluded.production_start_date,
                    production_end_date=excluded.production_end_date,
                    material_order_by_date=excluded.material_order_by_date,
                    feasibility_status=excluded.feasibility_status,
                    notes=excluded.notes,
                    last_updated=CURRENT_TIMESTAMP
            """, (order_id, schedule_info.get('prod_start'), schedule_info.get('prod_end'), 
                  schedule_info.get('material_order'), schedule_info.get('feasibility'), schedule_info.get('notes')))
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def calculate_and_save_schedule(self, order_id):
        """Calculates and saves the production schedule for an existing order."""
        order_info = self.get_order_by_id(order_id) # You might need to implement/adjust this
        schedule_info = self.calculate_schedule_for_ui(order_info['product_id'], order_info['quantity'], order_info['deadline'])
        self.save_schedule(order_id, schedule_info)

    #Data insertion in order history/ Creates the delivery status of the order
    def insert_order_history(self, order_id, changed_by, status='Pending', notes=None):
        """Insert a record into the order history table"""
        try:
            print("insert_order_history called with:", order_id, changed_by, status, notes)
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO order_history (order_id, status, changed_by, notes)
                VALUES (?, ?, ?, ?)
            """, (order_id, status, changed_by, notes))
        except sqlite3.IntegrityError as e:
            logging.error(f"Failed to insert order history: {str(e)}")
        finally:
            conn.close()
            logging.info(f'Order history for {order_id} recorded successfully')
            print(f'Order history for {order_id} recorded successfully')

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
            WHERE o.is_active = 1
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
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to update an order.")
            return

        try:
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
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            logging.info(f'Order {order_id} updated. Time: {self.timezone}')

    #To be Implemented
    def approve_order(self, order_id):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to approve an order.")
            return

        try:
            """Update the stauts of the pending order"""
            conn = self.get_connection()
            c = conn.cursor()

            status = "Approved"

            c.execute('UPDATE orders SET status_quo = ?     WHERE order_id = ?', (status, order_id))

            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An Error Occured {e}")
        finally:
            conn.close()
            logging.info(f"Order {order_id} has been approved, Time: {self.timezone}")

    def deduct_materials_for_order(self, order_id):
        """
        Deducts the required materials for the given order from the raw_mats inventory.
        Assumes the order's materials are stored as a JSON string in the database.
        """
        import json
        conn = self.get_connection()
        c = conn.cursor()
        # Get the materials needed for the order
        c.execute("SELECT mats_need FROM orders WHERE order_id = ?", (order_id,))
        result = c.fetchone()
        if result and result[0]:
            try:
                mats_need = json.loads(result[0])  
            except Exception:
                conn.close()
                raise ValueError("Invalid materials format in order record.")
            for mat_name, mat_qty_needed in mats_need.items():
                mats_fetch = c.execute(
                    "SELECT mat_id, current_stock FROM raw_mats WHERE mat_name = ?", (mat_name,)
                ).fetchone()
                if mats_fetch:
                    mat_id, current_qty = mats_fetch
                    if current_qty >= mat_qty_needed:
                        deducted_val = current_qty - mat_qty_needed
                        c.execute(
                            "UPDATE raw_mats SET current_stock = ? WHERE mat_id = ?",
                            (deducted_val, mat_id)
                        )
                    else:
                        logging.warning(f"Not enough stock for material {mat_name}. Needed: {mat_qty_needed}, Available: {current_qty}")
                        
                        pass
                else:
                    logging.warning(f"Material {mat_name} not found in inventory.")
                    pass
            conn.commit()
        conn.close()

    #To Be Implemented
    def cancel_order(self, order_id):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to cancel an order.")
            return

        try:
            """Soft Deletion of an order (Cancel - possibility to be approved later)"""
            conn = self.get_connection()
            c = conn.cursor()

            status = "Cancelled"

            c.execute("UPDATE orders SET status_quo = ? WHERE order_id = ?", (status, order_id))
            
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
            logging.info(f"Order {order_id} has been cancelled, Time: {self.timezone}")
    
    def delete_order(self, order_id):
        usertype = self.session.get('usertype')

        if usertype not in ['admin', 'manager', 'owner']:
            messagebox.showerror("Permission Denied", "You do not have permission to delete an order.")
            return

        try:
            """Delete an order from the database"""
            conn = self.get_connection()
            c = conn.cursor()
            
            is_active_val = 0

            c.execute("UPDATE orders SET is_active = ? WHERE order_id = ?", (is_active_val, order_id))
            
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("database Error", f"An error Occured: {e}")
        finally:
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
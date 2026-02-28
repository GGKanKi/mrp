import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import font
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel, CTkComboBox
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import logging


#Data Imports
import pandas as pd
import json
import os
import sys

# --- Pathing Setup ---
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

#File imports
from product import ProductManagementSystem
from order import OrderManagementUI, BASE_DIR
from database import DatabaseManager
from pages_handler import FrameNames
from global_func import on_show, handle_logout, export_total_amount_mats, resource_path


class OrdersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')
        self.update_window = None  # Variable to track the update window
        self.order_history_window = None  # Variable to track the order history window

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0))  # Sticks to the left, fills Y
        parent.pack_propagate(False)

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))  # Sticks to the top, fills X

        novus_logo = Image.open(os.path.join(BASE_DIR, 'labels', 'novus_logo1.png'))
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        logging.basicConfig(filename=os.path.join(BASE_DIR, 'log_f', 'actions.log'), level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Buttons Images
        self.clients_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'client_btn.png'), size=(100,100))
        self.inv_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'inventory.png'), size=(100,100))
        self.product_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'product.png'), size=(100,100))
        self.order_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'order.png'), size=(100,100))
        self.supply_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'supply.png'), size=(100,100))
        self.logout_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'logout.png'), size=(100,100))
        self.mrp_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'mrp_btn.png'), size=(100,100))
        self.settings_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'settings.png'), size=(100,100))
        self.user_logs_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'action.png'), size=(100,100))
        self.mails_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'mail.png'), size=(100,100))
        self.audit_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'audit.png'), size=(100,100))


        #User Type
        user_type = self.controller.session.get('usertype')

        # Add Products navigation button below Inventory on the left sidebar
        try:
            self.products_nav_btn = CTkButton(self.main, text="Products", fg_color="#3498db", hover_color="#2980b9",
                text_color="white", width=100, corner_radius=10, command=self.open_products_crud)
            self.products_nav_btn.pack(side="top", padx=5, pady=5)
        except Exception:
            pass


            # Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=60)

            order_stat_search = CTkFrame(self, fg_color='white')
            order_stat_search.pack(side="left", anchor="n", padx=(15, 15), pady=(5, 0), fill='x')

            CTkLabel(order_stat_search,
                    text="STATUS:",
                    font=('Futura', 15, 'bold'),
                    width=100,
                    anchor="w").pack(side="left")

            self.order_stat_var = tk.StringVar(value="None")
            self.order_stat_dd = CTkComboBox(order_stat_search,
                                            variable=self.order_stat_var,
                                            values=["All Status","Approved", "Pending", "Done", "Delivered", "Cancelled"],
                                            width=100,
                                            height=25,
                                            border_width=1,
                                            corner_radius=6)
            self.order_stat_dd.pack(side="left", padx=5) 


            # Add Approve, Cancel for Status
            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2',command=self.upd_srch_order)
            self.add_btn = self.add_del_upd('ADD', '#2ecc71', command=self.add_orders)
            self.approve_order_btn = self.add_del_upd('APPROVE', '#27ae60',command=self.approve_order)
            self.done_order_btn = self.add_del_upd('DONE', '#f39c12', command=self.mark_order_done)
            self.deliver_order_btn = self.add_del_upd('DELIVERED', '#3498db', command=self.order_done)
            self.cancel_order_btn = self.add_del_upd('CANCEL', '#95a5a6', command=self.cancel_order)
            self.del_btn = self.add_del_upd('DELETE', '#e74c3c', command=self.del_order)

            # Treeview style
            self.row_font = font.Font(family="Futura", size=20)
            self.head_font = font.Font(family="Futura", size=20, weight='bold')

            style = ttk.Style(self)
            style.theme_use("default")

            style.configure("Custom.Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=self.row_font, bordercolor="#cccccc", borderwidth=1)
            style.configure("Custom.Treeview.Heading", background="#007acc", foreground="white", font=self.head_font)
            style.map("Custom.Treeview", background=[('selected', '#b5d9ff')])

            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=self.row_font, bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=self.head_font)
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=130, y=105, width=1100, height=475)

            self.order_tree = ttk.Treeview(        
            tree_frame,
                columns=('order_id', 'order_name', 'product_id', 'client_id',
                        'quantity', 'deadline', 'order_date','mats_need', 'status_quo'),
                show='headings',
                style='Custom.Treeview'
            )
            self.order_tree.bind("<Double-1>", self.show_materials_popup)

            # Configure column headings (assuming _column_heads does this)
            self._column_heads('order_id', 'ORDER ID')
            self._column_heads('order_name', 'ORDER NAME')
            self._column_heads('product_id', 'PRODUCT')
            self._column_heads('client_id', 'CLIENT ID')
            self._column_heads('quantity', 'VOLUME')
            self._column_heads('order_date', 'ORDER DATE')
            self._column_heads('deadline', 'DEADLINE')
            self._column_heads('mats_need', 'EST. MFG DAYS')
            self._column_heads('status_quo', 'STATUS')

            # Configure column widths and stretching
            for col in self.order_tree['columns']:
                self.order_tree.column(col, width=300, stretch=False)  # Disable stretch for proper scrolling

            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.order_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.order_tree.xview)
            self.order_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.order_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Configure weight for proper resizing
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Add a small frame in the corner to avoid scrollbar overlap
            corner_grip = tk.Frame(tree_frame)
            corner_grip.grid(row=1, column=1, sticky="nsew")

            self.load_orders_from_db()

    def set_status_filter(self, status):
        """Sets the status dropdown and triggers a search."""
        self.order_stat_var.set(status)
        self.upd_srch_order()


    def upd_srch_order(self):
        search_order = self.search_entry.get().strip()
        order_status = ["Approved", "Pending", "Done", "Delivered", "Cancelled"]

        if search_order == "":
            order_stat = self.order_stat_var.get().strip()

            if order_stat != "None" and order_stat != "All Status" and order_stat in order_status:
                try: #This path is also in product.py, will fix it there too
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    all_order_stat = c.execute('SELECT * FROM orders WHERE status_quo = ? AND is_active = 1', (order_stat,)).fetchall()

                    for i in self.order_tree.get_children():
                        self.order_tree.delete(i)
                    
                    if all_order_stat:
                        for i in all_order_stat:
                            item_id = self.order_tree.insert("", "end", values=i)
                            # Apply color based on status
                            status = i[8]  # Get the status from the row
                            if status == "Approved":
                                self.order_tree.tag_configure("approved", background="light green")
                                self.order_tree.item(item_id, tags=("approved",))
                            elif status == "Delivered":
                                self.order_tree.tag_configure("delivered", background="light blue")
                                self.order_tree.item(item_id, tags=("delivered",))
                            elif status == "Cancelled":
                                self.order_tree.tag_configure("cancelled", background="light coral")
                                self.order_tree.item(item_id, tags=("cancelled",))
                            elif status == "Done":
                                self.order_tree.tag_configure("done", background="orange")
                                self.order_tree.item(item_id, tags=("done",))
                            elif status == "Pending":
                                self.order_tree.tag_configure("pending", background="light grey")
                                self.order_tree.item(item_id, tags=("pending",))
                    else:
                        messagebox.showerror("No Orders", f"No Orders with Status: {order_stat}")
                        self.load_orders_from_db()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    return
                finally:
                    if conn:
                        conn.close()
                        
            elif order_stat == "All Status":
                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    all_orders = c.execute('SELECT * FROM orders WHERE is_active = 1').fetchall()

                    for i in self.order_tree.get_children():
                        self.order_tree.delete(i)
                    
                    if all_orders:
                        for i in all_orders:
                            item_id = self.order_tree.insert("", "end", values=i)
                            # Apply color based on status
                            status = i[8]  # Get the status from the row
                            if status == "Approved":
                                self.order_tree.tag_configure("approved", background="light green")
                                self.order_tree.item(item_id, tags=("approved",))
                            elif status == "Delivered":
                                self.order_tree.tag_configure("delivered", background="light blue")
                                self.order_tree.item(item_id, tags=("delivered",))
                            elif status == "Cancelled":
                                self.order_tree.tag_configure("cancelled", background="light coral")
                                self.order_tree.item(item_id, tags=("cancelled",))
                            elif status == "Done":
                                self.order_tree.tag_configure("done", background="orange")
                                self.order_tree.item(item_id, tags=("done",))
                            elif status == "Pending":
                                self.order_tree.tag_configure("pending", background="light grey")
                                self.order_tree.item(item_id, tags=("pending",))
                    else:
                        messagebox.showerror("No Orders", "No orders found.")
                        self.load_orders_from_db()

                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.load_orders_from_db()
                finally:
                    if conn:
                        conn.close()
            else:
                pass

        elif search_order:
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                # Search across multiple columns
                query = '''
                    SELECT * FROM orders
                    WHERE is_active = 1 AND (
                        order_id LIKE ?
                        OR order_name LIKE ?
                        OR product_id LIKE ?
                        OR client_id LIKE ?
                        OR quantity LIKE ?
                        OR deadline LIKE ?
                        OR mats_need LIKE ?
                        OR status_quo LIKE ?
                    )
                    AND is_active = 1
                    ORDER BY order_id
                '''
                like_val = f'%{search_order}%'
                orders = c.execute(query, (like_val,) * 8).fetchall()


                for i in self.order_tree.get_children():
                    self.order_tree.delete(i)
                
                if orders:
                    for order in orders:
                        item_id = self.order_tree.insert("", "end", values=order)
                        # Apply color based on status
                        status = order[8]  # Get the status from the row
                        if status == "Approved":
                            self.order_tree.tag_configure("approved", background="light green")
                            self.order_tree.item(item_id, tags=("approved",))
                        elif status == "Delivered":
                            self.order_tree.tag_configure("delivered", background="light blue")
                            self.order_tree.item(item_id, tags=("delivered",))
                        elif status == "Cancelled":
                            self.order_tree.tag_configure("cancelled", background="light coral")
                            self.order_tree.item(item_id, tags=("cancelled",))
                        elif status == "Done":
                            self.order_tree.tag_configure("done", background="orange")
                            self.order_tree.item(item_id, tags=("done",))
                        elif status == "Pending":
                            self.order_tree.tag_configure("pending", background="light grey")
                            self.order_tree.item(item_id, tags=("pending",))
                else:
                    messagebox.showerror("No Orders", f"No orders found matching: {search_order}")
                    self.load_orders_from_db()

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.load_orders_from_db()
            finally:
                if conn:
                    conn.close()

    def add_orders(self):
        if (user_type := self.controller.session.get('usertype')) == 'staff':
            messagebox.showwarning("Access Denied", "You do not have permission to add orders.")
            return

        # Open the Order Management UI in a separate top-level window
        top = tk.Toplevel(self)
        top.title("Order Management")
        top.geometry("900x600")
        top.minsize(700, 500)
        top.transient(self)
        top.grab_set()
        top.configure(bg='white')

        container = tk.Frame(top, bg='#f8f9fa')
        container.pack(fill='both', expand=True)

        # Initialize a DatabaseManager reusing the current session if available
        try:
            session = getattr(self.controller, 'session', {}) if hasattr(self.controller, 'session') else {}
        except Exception:
            session = {}

        db_manager = DatabaseManager(session=session) if session else DatabaseManager()

        order_ui = OrderManagementUI(
            parent_frame=container,
            db_manager=db_manager,
            session=session,
            controller=self.controller,
            parent_window=top
        )
        order_ui.setup()

    def approve_order(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):

            messagebox.showwarning("Access Denied", "You do not have permission to approve orders.")
            return
    
        try:
            with open(resource_path(os.path.join('json_f', 'order_mats_ttl.json')), 'r') as f:
                try:
                    ttl_mats_list = json.load(f)
                except json.JSONDecodeError:
                    print("❌ JSON file is empty or invalid.")
                    ttl_mats_list = []
        except FileNotFoundError:
            messagebox.showerror("File Error", "Could not find 'order_mats_ttl.json'.")
            return

        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order to approve.")
            return

        values = self.order_tree.item(selected, 'values')
        order_id = values[0]

        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            order_info = c.execute("""
                SELECT o.order_id, o.status_quo, p.product_id, p.status_quo
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.order_id = ?
            """, (order_id,)).fetchone()

            if not order_info:
                messagebox.showerror("Not Found", f"Order ID: {order_id} cannot be found")
                return

            searched_order_id, order_status, prod_id, prod_status = order_info[0],  order_info[1], order_info[2], order_info[3]

            if order_status not in ("Pending", "Cancelled"):
                messagebox.showinfo("Invalid Status", f"Order ID: {order_id} is already '{order_status}' and cannot be approved again.")
                return

            if prod_status == "Pending":
                messagebox.showinfo("Pending Product", f"Order ID: {searched_order_id}, Product ID {prod_id} Status: {prod_status}")
                return
            elif prod_status == "Cancelled":
                messagebox.showwarning("Cancelled Product", f"Order ID: {searched_order_id}, Product ID {prod_id} Status: {prod_status}")
                return

            # Proceed with approval if product is approved
            selected_order = next((order for order in ttl_mats_list if order['order_id'] == order_id), None)
            if not selected_order:
                messagebox.showerror('Error', f'Order ID: {order_id} not found in JSON data')
                return

            mats_need = selected_order['mats_need']
            insufficient_mats = []
            warning_mats = []
            mats_stock = {}

            # First, check all materials for stock levels
            for mat_name, mat_qty_needed in mats_need.items():
                mats_fetch = c.execute("""
                    SELECT mat_id, current_stock, min_stock_level
                    FROM raw_mats WHERE mat_name = ? AND is_active = 1
                """, (mat_name,)).fetchone()

                if not mats_fetch:
                    insufficient_mats.append(f"{mat_name}: Not found in inventory.")
                    continue

                mat_id, current_qty, min_stock = mats_fetch
                mats_stock[mat_name] = (mat_id, current_qty)

                if current_qty <= min_stock:
                    insufficient_mats.append(f"{mat_name}: Stock is low ({current_qty} <= {min_stock}). Replenish first.")
                elif current_qty < mat_qty_needed:
                    insufficient_mats.append(f"{mat_name}: Need {mat_qty_needed}, Have {current_qty}")
                elif (current_qty - mat_qty_needed) < min_stock:
                    warning_mats.append(f"{mat_name}: Stock will be low after this order.")
                elif (current_qty - mat_qty_needed) < (min_stock * 1.2):
                    warning_mats.append(f"{mat_name}: Stock will reach a low count after this order.")

            # If any material is insufficient, block approval
            if insufficient_mats:
                messagebox.showerror("Insufficient Materials", "Order cannot be approved:\n" + "\n".join(insufficient_mats))
                return

            # If there are warnings, ask for confirmation
            if warning_mats:
                warning_message = "The following materials will reach low stock levels:\n\n" + "\n".join(warning_mats) + "\n\nDo you want to proceed with approval?"
                if not messagebox.askyesno("Low Stock Warning", warning_message):
                    return

            # All checks passed, proceed to approve and deduct
            new_status = "Approved"
            c.execute('UPDATE orders SET status_quo = ? WHERE order_id = ?', (new_status, searched_order_id))

            # Deduct materials from inventory
            for mat_name, mat_qty_needed in mats_need.items():
                mat_id, current_qty = mats_stock[mat_name]
                deducted_val = current_qty - mat_qty_needed
                c.execute("UPDATE raw_mats SET current_stock = ? WHERE mat_id = ?", (deducted_val, mat_id))

            messagebox.showinfo("Success", f"Order ID: {searched_order_id} has been approved and materials have been deducted.")

            conn.commit()

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            messagebox.showerror("Database Error", f"{e}")
            print(e)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            try:
                self.load_orders_from_db()
            except Exception as e:
                print("Error reloading orders:", e)

    def cancel_order(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to cancel orders.")
            return

        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an order to approve.")
            return
        
        values = self.order_tree.item(selected, 'values')
        order_id = values[0]
        order_stat = values[7]

        conn = None
        try:
            status = 'Cancelled'
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("UPDATE orders SET status_quo = ? WHERE order_id = ?", (status, order_id))
            conn.commit()
            messagebox.showinfo("Success", f"Order ID '{order_id}' has been cancelled.")
            self.load_orders_from_db()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def del_order(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to deny orders.")
            return
        #Hard Deletion
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a order to delete.")
            return

        conn = None
        try:
            values = self.order_tree.item(selected, 'values')
            order_id = values[0]  # Assuming client_id is the first column

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete order ID '{order_id}'?")
            if not confirm:
                return

            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT * FROM orders WHERE order_id =  ?", (order_id,))
            row = c.fetchone()

            if row:
                is_inactive = 0
                c.execute("UPDATE orders SET is_active = ? WHERE order_id = ?", (is_inactive, order_id))
                conn.commit()
                # Refresh all frames to update dashboard counts
                if hasattr(self.controller, 'refresh_all_frames'):
                    self.controller.refresh_all_frames()

                messagebox.showinfo("Deleted", f"Order ID '{order_id}' has been deleted.")
                self.load_orders_from_db()
            else:
                messagebox.showinfo("Not Found", f"No Orders found with ID '{order_id}'")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()
            self.load_orders_from_db() # Ensure this is called even on error

    def load_orders_from_db(self):
        try:
            conn = sqlite3.connect(resource_path("main.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE is_active = 1")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.order_tree.get_children():
                self.order_tree.delete(i)

            # Fetch product manufacturing times to avoid N+1 queries
            product_mfg_times = {}
            cursor.execute("SELECT product_id, manufacturing_time_hours FROM products")
            for prod_id, mfg_time in cursor.fetchall():
                product_mfg_times[prod_id] = mfg_time if mfg_time is not None else 0

            for row in rows:
                # Swap deadline (idx 5) and order_date (idx 6) to match the treeview column definition
                product_id = row[2]
                quantity = row[4]
                mfg_time = product_mfg_times.get(product_id, 0)
                est_mfg_days = "N/A"
                if mfg_time > 0 and isinstance(quantity, (int, float)):
                    est_mfg_days = f"{(mfg_time * quantity / 8):.1f}"

                display_row = row[:7] + (est_mfg_days,) + row[8:]
                item_id = self.order_tree.insert("", "end", values=display_row)
                
                # Set row background color based on order status
                # Assuming status_quo is at index 8 in the row tuple
                status = row[8]  # Get the status from the row
                if status == "Approved":
                    self.order_tree.tag_configure("approved", background="light green")
                    self.order_tree.item(item_id, tags=("approved",))
                elif status == "Delivered":
                    self.order_tree.tag_configure("delivered", background="light blue")
                    self.order_tree.item(item_id, tags=("delivered",))
                elif status == "Cancelled":
                    self.order_tree.tag_configure("cancelled", background="light coral")
                    self.order_tree.item(item_id, tags=("cancelled",))
                elif status == "Done":
                    self.order_tree.tag_configure("done", background="orange")
                    self.order_tree.item(item_id, tags=("done",))
                elif status == "Pending":
                    self.order_tree.tag_configure("pending", background="light grey")
                    self.order_tree.item(item_id, tags=("pending",))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    #
    def mark_order_done(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to mark orders as done.")
            return

        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order to mark as done.")
            return

        values = self.order_tree.item(selected, 'values')
        order_id = values[0]
        current_status = values[8]

        if current_status != "Approved":
            messagebox.showerror("Invalid Status", f"Only 'Approved' orders can be marked as done. This order is '{current_status}'.")
            return

        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            new_status = "Done"
            c.execute('UPDATE orders SET status_quo = ? WHERE order_id = ?', (new_status, order_id))
            conn.commit()
            messagebox.showinfo("Success", f"Order ID: {order_id} has been marked as 'Done' and is ready for delivery.")
            self.load_orders_from_db()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def order_done(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to approve orders.")
            return
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an order to mark as delivered.")
            return  

        try:
            user_id = self.controller.session.get('user_id')

            if not user_id:
                messagebox.showerror("Session Error", "User  not logged in.")
                return

            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            values = self.order_tree.item(selected, 'values')
            order_id = values[0]

            conn = None
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            order_info = c.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()


            if not order_info:
                messagebox.showerror("Not Found", f'Order ID: {order_id} cannot be found')
                return
            
            selected_id, client_id, order_status = order_info[0], order_info[3], order_info[8]

            existing_order = c.execute('SELECT * FROM order_history WHERE order_id = ?', (selected_id,)).fetchone()

            if existing_order:
                messagebox.showerror("Order Already Delivered", f"Order ID: {selected_id} has already been marked as delivered.")
                return

            # If there is any sort of confirmation from the customer that the item is delivered.
            if order_status not in ("Approved", "Done"):
                messagebox.showerror("Order Status Error", f"Order ID: {selected_id} must be 'Approved' or 'Done' before it can be delivered.")
                return
            else:    
                delivery_status = "Delivered"
                notes = f"Order ID {selected_id} has been delivered to Client: {client_id}"
                c.execute('INSERT INTO order_history (order_id, status, changed_by, notes, timestamp) VALUES (?, ?, ?, ?, ?)',
                        (selected_id, delivery_status, user_id, notes, timestamp))
                logging.info(f"Order ID {selected_id} marked as delivered by User ID {user_id} at {timestamp}")
                c.execute('UPDATE orders SET status_quo = ? WHERE order_id = ?', (delivery_status, selected_id))
                messagebox.showinfo("Success", f"Order ID: {selected_id} has been marked as delivered.")
                self.load_orders_from_db()

            conn.commit()
            self.load_orders_from_db()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            if conn:
                conn.close()

    def show_materials_popup(self, event):
        selected = self.order_tree.focus()
        if not selected:
            return
        values = self.order_tree.item(selected, 'values')
        order_id = values[0]
        order_name = values[1]
        product_id = values[2]
        client_id = values[3]
        quantity = values[4]
        order_date = values[5]
        deadline = values[6]
        mats_used = values[7]
        status = values[8]

        # Store reference to the order history window
        if self.order_history_window is not None and self.order_history_window.winfo_exists():
            self.order_history_window.destroy()

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            # Fetch all order history entries for the selected order
            order_history = c.execute("SELECT status, changed_by, notes, timestamp FROM order_history WHERE order_id = ? ORDER BY timestamp DESC", (order_id,)).fetchall()
            
            # Fetch product name
            product_name = c.execute("SELECT product_name FROM products WHERE product_id = ?", (product_id,)).fetchone()
            product_name = product_name[0] if product_name else "Unknown Product"
            
            # Fetch client name
            client_name = c.execute("SELECT client_name FROM clients WHERE client_id = ?", (client_id,)).fetchone()
            client_email = c.execute("SELECT client_email FROM clients WHERE client_id = ?", (client_id,)).fetchone()
            client_name = client_name[0] if client_name else "Unknown Client"

            # Create a better designed popup window
            popup = tk.Toplevel(self)
            self.order_history_window = popup  # Store reference to the window
            popup.title(f"Order Details - {order_name}")
            popup.geometry("800x600")
            popup.configure(bg='white')
            popup.grab_set()  # Make window modal to ensure it gets focus

            # --- Main Scrollable Frame ---
            scrollable_main_frame = ctk.CTkScrollableFrame(popup, fg_color="white")
            scrollable_main_frame.pack(fill="both", expand=True)

            
            # Order information frame
            order_frame = CTkFrame(scrollable_main_frame, fg_color="#e6f2ff", corner_radius=10)
            order_frame.pack(fill="x", padx=20, pady=10)
            
            # Order details header
            header_label = CTkLabel(order_frame, text="ORDER INFORMATION", font=('Futura', 16, 'bold'), 
                                    text_color="#003366", fg_color="#e6f2ff")
            header_label.pack(pady=(10, 5), anchor="w", padx=20)
            
            # Order details in a grid layout
            details_frame = CTkFrame(order_frame, fg_color="#e6f2ff")
            details_frame.pack(fill="x", padx=20, pady=5)
            
            # Left column
            left_col = CTkFrame(details_frame, fg_color="#e6f2ff")
            left_col.pack(side="left", fill="x", expand=True)
            
            # Right column
            right_col = CTkFrame(details_frame, fg_color="#e6f2ff")
            right_col.pack(side="right", fill="x", expand=True)
            
            # Simplified fields - removed client ID, product ID, and status
            fields_left = [
                ('Order ID', order_id),
                ('Order Name', order_name)
            ]
            
            # Right column fields - simplified
            fields_right = [
                ('Product Name', product_name),
                ('Client Name', client_name),
                ('Quantity', quantity)
            ]
            
            # Add fields to left column
            for i, (field, value) in enumerate(fields_left):
                info_frame = CTkFrame(left_col, fg_color="#e6f2ff")
                info_frame.pack(fill="x", pady=2)
                
                field_label = CTkLabel(info_frame, text=f"{field}:", font=('Arial', 12, 'bold'), 
                                      text_color="#003366", width=100, anchor="w")
                field_label.pack(side="left", padx=(10, 5))
                
                value_label = CTkLabel(info_frame, text=f"{value}", font=('Arial', 12), 
                                      text_color="#000000", anchor="w")
                value_label.pack(side="left", fill="x", expand=True)
            
            # Add fields to right column
            for i, (field, value) in enumerate(fields_right):
                info_frame = CTkFrame(right_col, fg_color="#e6f2ff")
                info_frame.pack(fill="x", pady=2)
                
                field_label = CTkLabel(info_frame, text=f"{field}:", font=('Arial', 12, 'bold'), 
                                      text_color="#003366", width=100, anchor="w")
                field_label.pack(side="left", padx=(10, 5))
                
                value_label = CTkLabel(info_frame, text=f"{value}", font=('Arial', 12), 
                                      text_color="#000000", anchor="w")
                value_label.pack(side="left", fill="x", expand=True)
                 
            # Dates section removed as requested
            
            # Improved materials used section with better layout
            materials_frame = CTkFrame(order_frame, fg_color="#e6f2ff", corner_radius=8)
            materials_frame.pack(fill="x", padx=20, pady=10)
            
            materials_header = CTkLabel(materials_frame, text="MATERIALS USED", font=('Arial', 14, 'bold'), 
                                     text_color="#003366", fg_color="#e6f2ff")
            materials_header.pack(pady=(5, 0), padx=20, anchor="w")
            
            # Create a scrollable frame for materials if text is long
            materials_content_frame = CTkFrame(materials_frame, fg_color="#f0f5ff", corner_radius=5)
            materials_content_frame.pack(fill="x", expand=True, padx=10, pady=5)
            
            materials_value = CTkLabel(materials_content_frame, text=f"{mats_used}", font=('Arial', 12), 
                                     text_color="#000000", anchor="w", wraplength=700, 
                                     justify="left", corner_radius=5)
            materials_value.pack(fill="x", expand=True, padx=15, pady=10)

            # --- Action Buttons ---
            action_frame = CTkFrame(scrollable_main_frame, fg_color="white")
            action_frame.pack(fill='x', padx=20, pady=(10,0))

            def email_client_for_delivery():
                """Send an email to the client informing them their order is ready."""
                from global_func import load_credentials_if_logged_in, send_email_with_attachment
                
                try:
                    creds = load_credentials_if_logged_in()
                    if not creds:
                        messagebox.showerror('Email Error', 'Please login with Google first to send an email.')
                        return

                    client_email_address = client_email[0] if client_email and client_email[0] else None
                    if not client_email_address:
                        messagebox.showerror('Error', 'Client email not found for this order.')
                        return

                    # Sender details from session
                    f_name = self.controller.session.get('f_name', '')
                    l_name = self.controller.session.get('l_name', '')
                    sender_role = self.controller.session.get('usertype', '')
                    sender_email = self.controller.session.get('useremail', 'noreply@novusindustry.com')

                    # Compose email
                    email_subject = f"Your Order is Ready for Delivery: {order_name} (ID: {order_id})"
                    email_body = (
                        f"Dear {client_name},\n\n"
                        f"We are pleased to inform you that your order is now complete and ready for delivery.\n\n"
                        f"Order Details:\n"
                        f"  • Order ID: {order_id}\n"
                        f"  • Order Name: {order_name}\n"
                        f"  • Product: {product_name}\n"
                        f"  • Quantity: {quantity}\n\n"
                        f"We will coordinate with you shortly to arrange the delivery schedule. Thank you for your business!\n\n"
                        f"Best regards,\n"
                        f"{f_name} {l_name} ({sender_role})\n"
                        f"Novus Industry Solutions\n"
                        f"{sender_email}"
                    )

                    if send_email_with_attachment(creds, client_email_address, email_subject, email_body, from_email=sender_email):
                        messagebox.showinfo('Success', f"An email has been sent to the client ({client_email_address}).")
                    else:
                        messagebox.showerror('Failed', 'The email could not be sent. Please check your connection or Google login status.')
                except Exception as e:
                    messagebox.showerror('Error', f"An unexpected error occurred: {str(e)}")

            user_type = self.controller.session.get('usertype')
            if status == "Done" and user_type in ('admin', 'owner', 'manager'):
                email_btn = CTkButton(action_frame, text="Email Client for Delivery", command=email_client_for_delivery, fg_color="#27ae60", hover_color="#2ecc71")
                email_btn.pack(side='left', padx=10, pady=10)
            
            # Close button
            btn_close = CTkButton(scrollable_main_frame, text="Close", font=('Arial', 12, 'bold'), 
                                 fg_color="#003366", hover_color="#004080",
                                 command=popup.destroy)
            btn_close.pack(pady=20)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            conn.close()

    def add_del_upd(self, text, fg_color, command, **kwargs):
        button = CTkButton(self, text=text, fg_color=fg_color, width=70, command=command, font=('Futura', 13, 'bold'), **kwargs)
        button.pack(side="left", anchor="n", padx=2)
        return button

    def _column_heads(self, columns, text):
        self.order_tree.heading(columns, text=text)
        self.order_tree.column(columns, width=175)
        if text == 'MATERIALS':
            self.order_tree.column(columns, width=100)

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, 
                           image=image, 
                           text=text, 
                           font=('Futura', 15, 'bold'),
                           text_color="black",
                           bg_color="#6a9bc3", 
                           fg_color="#6a9bc3", 
                           hover_color="white",
                           width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15, fill='x')

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

    def _add_order(self, label_text, y):

        label = CTkLabel(self.add_order, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.add_order, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    
    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self)
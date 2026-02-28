import tkinter as tk
import pytz
from tkinter import font
import time
from datetime import datetime
from tkinter import ttk, messagebox
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import os
import json
import logging
import sys
sys.path.append("C:/capstone")
from pages_handler import FrameNames
from global_func import on_show, handle_logout, resource_path, center_window
from log_f.user_activity_logger import user_activity_logger


class ProductsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.product_management_system = None
        self.update_window = None
        self.config(bg='white')

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0)) 

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
        parent.pack_propagate(False)

        #Logger Files
        logging.basicConfig(filename=resource_path(os.path.join('log_f', 'actions.log')), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.product_act = logging.getLogger('PRODUCT_ACT')
        self.product_act.setLevel(logging.INFO)

        self.product_act_warning = logging.getLogger('PRODUCT_ACT_WARNING')
        self.product_act_warning.setLevel(logging.WARNING)

        self.product_act_error = logging.getLogger('PRODUCT_ACT_ERROR')
        self.product_act_error.setLevel(logging.ERROR)

        novus_logo = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        # Buttons Images
        self.clients_btn = self._images_buttons(resource_path(os.path.join('labels', 'client_btn.png')), size=(100,100))
        self.inv_btn = self._images_buttons(resource_path(os.path.join('labels', 'inventory.png')), size=(100,100))
        self.product_btn = self._images_buttons(resource_path(os.path.join('labels', 'product.png')), size=(100,100))
        self.order_btn = self._images_buttons(resource_path(os.path.join('labels', 'order.png')), size=(100,100))
        self.supply_btn = self._images_buttons(resource_path(os.path.join('labels', 'supply.png')), size=(100,100))
        self.logout_btn = self._images_buttons(resource_path(os.path.join('labels', 'logout.png')), size=(100,100))
        self.mrp_btn = self._images_buttons(resource_path(os.path.join('labels', 'mrp_btn.png')), size=(100,100))
        self.settings_btn = self._images_buttons(resource_path(os.path.join('labels', 'settings.png')), size=(100,100))
        self.user_logs_btn = self._images_buttons(resource_path(os.path.join('labels', 'action.png')), size=(100,100))
        self.mails_btn = self._images_buttons(resource_path(os.path.join('labels', 'mail.png')), size=(100,100))
        self.audit_btn = self._images_buttons(resource_path(os.path.join('labels', 'audit.png')), size=(100,100))


        #User Type
        user_type = self.controller.session.get('usertype')


        # Search and CRUD buttons
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=150)

        self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.srch_products)
        self.add_btn = self.add_del_upd('ADD PRODUCT', '#2ecc71', command=self.add_products)
        self.approve_btn = self.add_del_upd('APPROVE', '#27ae60', command=self.approve_selected_product)
        self.del_btn = self.add_del_upd('DELETE PRODUCT', '#e74c3c', command=self.del_products)

        # Treeview style
        self.row_font = font.Font(family="Futura", size=13)
        self.head_font = font.Font(family="Futura", size=15, weight='bold')

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Custom.Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=self.row_font, bordercolor="#cccccc", borderwidth=1)
        style.configure("Custom.Treeview.Heading", background="#007acc", foreground="white", font=self.head_font)
        style.map("Custom.Treeview", background=[('selected', '#b5d9ff')])
        # Configure tag for 'Approved' status to have a green background
        style.configure("Approved.Custom.Treeview", background="light green")

        tree_frame = tk.Frame(self)
        tree_frame.place(x=130, y=105, width=1100, height=475)
 
        self.product_tree = ttk.Treeview(        
            tree_frame,
            columns=('product_id', 'product_name', 'materials', 'created_date', 'status_quo'),
            show='headings',
            style='Custom.Treeview'
        )
        self.product_tree.bind("<Double-1>", self.show_product_details)
 
        self._column_heads('product_id', 'PRODUCT ID')
        self._column_heads('product_name', 'PRODUCT NAME')
        self._column_heads('materials', 'MATERIALS')
        self._column_heads('created_date', 'CREATED DATE')
        self._column_heads('status_quo', 'STATUS')
 
        # Configure column widths
        self.product_tree.column('product_id', width=140, stretch=False)
        self.product_tree.column('product_name', width=250, stretch=False)
        self.product_tree.column('materials', width=400, stretch=False)
        self.product_tree.column('created_date', width=160, stretch=False)
        self.product_tree.column('status_quo', width=150, stretch=False)

        # Scrollbars
        self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.product_tree.yview)
        self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Use grid for proper layout
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Make the treeview expandable
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Add a small frame in the corner to avoid scrollbar overlap
        corner_grip = tk.Frame(tree_frame)
        corner_grip.grid(row=1, column=1, sticky="nsew")

        self.load_products_from_db()

    def destroy(self):
        """Override destroy to clean up any open Toplevel windows."""
        if self.update_window and self.update_window.winfo_exists():
            self.update_window.destroy()
        if self.product_management_system and hasattr(self.product_management_system, 'window') and self.product_management_system.window.winfo_exists():
            self.product_management_system.window.destroy()
        super().destroy()
    def on_show(self):
        on_show(self)

    def handle_logout(self):
        handle_logout(self)

    def add_del_upd(self, text, fg_color,  command):
        button = ctk.CTkButton(self, text=text, width=90, fg_color=fg_color, command=command, font=('Futura', 13, 'bold'))
        button.pack(side="left", anchor="n", padx=4)

    def load_products_from_db(self):
        """Load products from the database and display them in the treeview"""
        try:
            # ... (rest of the function)
            for i in self.product_tree.get_children():
                self.product_tree.delete(i)
            
            # Connect to database
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            
            # Fetch all products from database
            c.execute("SELECT product_id, product_name, materials, created_date, status_quo FROM products WHERE is_active = 1 ORDER BY created_date DESC")
            products = c.fetchall()
            
            # Insert products into treeview
            for product in products:
                product_id, name, materials, created_date, status_quo = product
                
                # Format the created date
                if created_date:
                    try:
                        dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S.%f')
                        formatted_date = dt.strftime('%m/%d/%Y %H:%M')
                    except:
                        try:
                            dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                            formatted_date = dt.strftime('%m/%d/%Y %H:%M')
                        except:
                            formatted_date = created_date
                else:
                    formatted_date = 'N/A'
                
                # Truncate materials if too long for display
                display_materials = materials[:50] + "..." if materials and len(materials) > 50 else materials or 'N/A'
                
                # Determine tags for row styling
                tags = ()
                if status_quo == 'Approved':
                    tags = ('approved',)

                # Insert into treeview
                item_id = self.product_tree.insert("", "end", values=(
                    product_id or 'N/A',
                    name or 'N/A',
                    display_materials,
                    formatted_date,
                    status_quo or 'Pending'
                ), tags=tags)
            
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading products: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading products: {str(e)}")
            print(f"Error loading products: {e}")

        # Configure the tag for the 'Approved' status
        self.product_tree.tag_configure('approved', background='light green')



    def refresh_products(self):
        """Refresh the product list from database"""
        self.load_products_from_db()

    def add_products(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to add products.")
            self.product_act_warning.warning(f"Unauthorized add product attempt by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            return

        # Import and launch the comprehensive product management system
        try:
            from product import ProductManagementSystem
            from global_func import center_window
            
            # Save the current theme before opening the new window
            s = ttk.Style()
            original_theme = s.theme_use()

            # Check if product management system already exists
            if hasattr(self, 'product_management_system') and hasattr(self.product_management_system, 'window') and self.product_management_system.window.winfo_exists():
                self.product_management_system.window.lift()
                center_window(self.product_management_system.window)
                return
            
            # Initialize the product management system directly (it creates its own window)
            self.product_management_system = ProductManagementSystem(self, self.controller)
            
            # Ensure the window is centered
            if hasattr(self.product_management_system, 'window'):
                center_window(self.product_management_system.window)
            
            # Define what happens when the "Add Product" window is closed
            def on_product_window_close():
                self.product_management_system.window.destroy()
                s.theme_use(original_theme)
                self.refresh_products()

            if hasattr(self.product_management_system, 'window'):
                self.product_management_system.window.protocol("WM_DELETE_WINDOW", on_product_window_close)
            
            # Log the action
            self.product_act.info(f"Product Management System opened by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"Error while opening Product Management System: {e}")
            messagebox.showerror("Error", f"Failed to open Product Management System: {str(e)}")
            self.product_act_error.error(f"Error while opening Product Management System: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def approve_selected_product(self):
        """Approve a selected product and check for material availability."""
        user_type = self.controller.session.get('usertype')
        if user_type not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to approve products.")
            return

        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to approve.")
            return

        values = self.product_tree.item(selected, 'values')
        prod_id = values[0]
        prod_name = values[1]

        # The logic from product.py's approve_selected_product is adapted here.
        # It relies on a JSON file for material details.
        try:
            with open(resource_path(os.path.join('json_f', 'products_materials.json')), 'r') as f:
                product_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "Could not load 'products_materials.json'. Please ensure it is generated and valid.")
            return

        selected_product = next((p for p in product_list if p.get('product_id') == prod_id), None)
        if not selected_product or 'materials' not in selected_product:
            messagebox.showerror("Error", f"Product ID {prod_id} not found or has no materials in the JSON file.")
            return

        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            unavailable_mats = []
            avail_mats_list = []

            for mat_name, mat_qty in selected_product['materials'].items():
                c.execute("SELECT current_stock FROM raw_mats WHERE mat_name = ?", (mat_name,))
                result = c.fetchone()

                if result:
                    current_qty = result[0]
                    if current_qty >= mat_qty:
                        avail_mats_list.append(f"{mat_name} (needed: {mat_qty}, available: {current_qty})")
                    else:
                        unavailable_mats.append(f"{mat_name} (needed: {mat_qty}, available: {current_qty})")
                else:
                    unavailable_mats.append(f"Material '{mat_name}' not found in inventory.")

            if unavailable_mats:
                error_message = (
                    f"❌ Cannot approve product '{prod_name}' (ID: {prod_id}) due to insufficient materials:\n\n" +
                    "\n".join(f"- {item}" for item in unavailable_mats)
                )
                messagebox.showerror("Insufficient Materials", error_message)
                # Optionally set status back to Pending if it was changed
                c.execute('UPDATE products SET status_quo = ? WHERE product_id = ?', ('Pending', prod_id))
            else:
                # All materials are available, so approve the product
                status_approve = 'Approved'
                c.execute('UPDATE products SET status_quo = ? WHERE product_id = ?', (status_approve, prod_id))

                success_mats = (
                    f"✅ Product '{prod_name}' (ID: {prod_id}) approved successfully!\n\n"
                    "Materials are available:\n" +
                    "\n".join(f"- {material}" for material in avail_mats_list)
                )
                messagebox.showinfo("Success", success_mats)

                # Log the approval action
                user_id = self.controller.session.get('user_id', 'unknown')
                username = self.controller.session.get('username', 'Unknown')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f'APPROVE PRODUCT {prod_id}', timestamp))
                
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="approve",
                    feature="product",
                    operation="approve_product",
                    details=f"Approved product '{prod_name}' (ID: {prod_id})"
                )

            conn.commit()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
            self.refresh_products()

    def srch_products(self):
        """Search products in the database based on product name or ID"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_products_from_db()
            return
        
        try:
            # Clear existing items
            for i in self.product_tree.get_children():
                self.product_tree.delete(i)
            
            # Connect to database
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            
            # Search for products by name or ID
            search_query = f"%{search_term}%"
            c.execute("""
                SELECT product_id, product_name, materials, created_date, status_quo 
                FROM products 
                WHERE product_name LIKE ? OR product_id LIKE ?
                ORDER BY created_date DESC
            """, (search_query, search_query))
            
            products = c.fetchall()
            
            # Insert filtered products into treeview
            for product in products:
                product_id, name, materials, created_date, status_quo = product
                
                # Format the created date
                if created_date:
                    try:
                        dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S.%f')
                        formatted_date = dt.strftime('%m/%d/%Y %H:%M')
                    except:
                        try:
                            dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                            formatted_date = dt.strftime('%m/%d/%Y %H:%M')
                        except:
                            formatted_date = created_date
                else:
                    formatted_date = 'N/A'
                
                # Truncate materials if too long for display
                display_materials = materials[:50] + "..." if materials and len(materials) > 50 else materials or 'N/A'
                
                # Determine tags for row styling
                tags = ()
                if status_quo == 'Approved':
                    tags = ('approved',)

                # Insert into treeview
                self.product_tree.insert("", "end", values=(
                    product_id or 'N/A',
                    name or 'N/A',
                    display_materials,
                    formatted_date,
                    status_quo or 'Pending'
                ), tags=tags)
            
            conn.close()
            
            if not products:
                messagebox.showinfo("Not Found", f"No products found matching '{search_term}'")
                self.load_products_from_db()
            self.product_tree.tag_configure('approved', background='light green')
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching products: {str(e)}")
            self.load_products_from_db()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching: {str(e)}")
            self.load_products_from_db()

    def del_products(self):
        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a product to delete.")
            return

        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to delete products.")
            return
        
        values = self.product_tree.item(selected, 'values')
        product_id = values[0]

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            # Check if product is linked to any orders
            c.execute("SELECT COUNT(*) FROM orders WHERE product_id = ? AND is_active = 1", (product_id,))
            order_count = c.fetchone()[0]

            if order_count > 0:
                messagebox.showwarning("Cannot Delete", f"Product ID '{product_id}' is linked to existing orders and cannot be deleted.")
                self.product_act_warning.warning(f"Attempt to delete product ID '{product_id}' linked to orders by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
                return

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product ID '{product_id}'?")
            if not confirm:
                return

            # Soft delete: mark as inactive
            in_active_val = 0
            c.execute("UPDATE products SET is_active = ? WHERE product_id = ?", (in_active_val, product_id))
            conn.commit()
            conn.close()
            # Refresh all frames to update dashboard counts
            if hasattr(self.controller, 'refresh_all_frames'):
                self.controller.refresh_all_frames()

            messagebox.showinfo("Deleted", f"Product ID '{product_id}' has been deleted.")
            self.product_act.info(f"Product ID '{product_id}' deleted by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            self.load_products_from_db()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting product: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting: {str(e)}")
        finally:
            if conn:
                conn.close()

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product ID '{product_id}'?")
        if not confirm:
            return

        # Remove from treeview (interface only)
        self.product_tree.delete(selected)
        messagebox.showinfo("Deleted", f"Product ID '{product_id}' has been deleted. (Interface mode)")

    def show_product_details(self, event):
        selected = self.product_tree.focus()
        if not selected:
            return

        values = self.product_tree.item(selected, 'values')
        product_id = values[0]
        product_name = values[1]

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            # Fetch full product details
            c.execute("SELECT product_id, product_name, materials, created_date, status_quo FROM products WHERE product_id = ?", (product_id,))
            product_details = c.fetchone()

            # Fetch order history for this product
            c.execute("""
                SELECT o.order_id, o.order_name, c.client_name, o.quantity, o.deadline, o.status_quo
                FROM orders o
                JOIN clients c ON o.client_id = c.client_id
                WHERE o.product_id = ? AND o.is_active = 1
                ORDER BY o.order_date DESC
            """, (product_id,))
            order_history = c.fetchall()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return
        finally:
            if conn:
                conn.close()

        # --- UI Creation ---
        popup = tk.Toplevel(self)
        popup.title(f"Details for {product_name}")
        popup.geometry("900x600")
        popup.configure(bg='white')
        popup.resizable(False, False)
        popup.grab_set()

        # Product Info Frame
        product_frame = CTkFrame(popup, fg_color="#e6f2ff", corner_radius=10)
        product_frame.pack(fill="x", padx=20, pady=10)

        header_label = CTkLabel(product_frame, text="PRODUCT INFORMATION", font=('Futura', 16, 'bold'), text_color="#003366")
        header_label.pack(pady=(10, 5), anchor="w", padx=20)

        details_frame = CTkFrame(product_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=5, expand=True)
        details_frame.grid_columnconfigure(1, weight=1)
        details_frame.grid_columnconfigure(3, weight=1)

        # Display Product Details
        if product_details:
            CTkLabel(details_frame, text="Product ID:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=product_details[0], font=('Arial', 12)).grid(row=0, column=1, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text="Status:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=0, column=2, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=product_details[4], font=('Arial', 12)).grid(row=0, column=3, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text="Created Date:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=product_details[3], font=('Arial', 12)).grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Order History Section
        history_header = CTkLabel(popup, text="ORDER HISTORY", font=('Futura', 16, 'bold'), text_color="#003366")
        history_header.pack(pady=(20, 10))

        history_container = CTkFrame(popup, fg_color="white", corner_radius=10)
        history_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not order_history:
            CTkLabel(history_container, text="No order history found for this product.", font=('Arial', 14), text_color="#666666").pack(pady=50)
        else:
            # --- UI ENHANCEMENT: Apply a modern style to the Treeview ---
            style = ttk.Style()
            style.configure("Popup.Treeview", background="white", foreground="black", rowheight=28, fieldbackground="white", font=('Arial', 11))
            style.configure("Popup.Treeview.Heading", background="#e6f2ff", foreground="#003366", font=('Futura', 12, 'bold'), relief="flat")
            style.map("Popup.Treeview", background=[('selected', '#b5d9ff')])

            history_tree = ttk.Treeview(
                history_container,
                columns=('order_id', 'order_name', 'client', 'quantity', 'deadline', 'status'),
                show='headings',
                style="Popup.Treeview"  # Apply the new style
            )
            history_tree.pack(fill='both', expand=True, padx=10, pady=10)
            history_tree.tag_configure('delivered', background='light green')
            history_tree.tag_configure('cancelled', background='light coral')

            # Define columns
            history_tree.heading('order_id', text='Order ID')
            history_tree.heading('order_name', text='Order Name')
            history_tree.heading('client', text='Client')
            history_tree.heading('quantity', text='Quantity')
            history_tree.heading('deadline', text='Deadline')
            history_tree.heading('status', text='Status')

            # Set column widths
            history_tree.column('order_id', width=120, anchor='w')
            history_tree.column('order_name', width=150, anchor='w')
            history_tree.column('client', width=150, anchor='w')
            history_tree.column('quantity', width=80, anchor='center')
            history_tree.column('deadline', width=100, anchor='center')
            history_tree.column('status', width=100, anchor='center')

            # Populate with data
            for order in order_history:
                tags = ()
                status = order[5]  # Status is the 6th item
                if status == 'Delivered':
                    tags = ('delivered',)
                elif status == 'Cancelled':
                    tags = ('cancelled',)
                history_tree.insert('', 'end', values=order, tags=tags)

        popup.after(100, popup.lift) # Ensure it's on top


    def _column_heads(self, columns, text):
        self.product_tree.heading(columns, text=text)
        self.product_tree.column(columns, width=400, stretch=False)

    def _main_buttons(self, parent, image, text, command):
        button = ctk.CTkButton(parent, 
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
        image = image.resize(size)
        return CTkImage(image)
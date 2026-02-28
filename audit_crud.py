import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import font
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel, CTkComboBox, CTkOptionMenu
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import os

#Imported Files
from pages_handler import FrameNames

from global_func import on_show, handle_logout, send_email_with_attachment, load_credentials_if_logged_in, center_window, user_logs_to_sheets, action_logs_to_sheets, settings_logs_to_sheets, product_logs_to_sheets, resource_path

class AuditsPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
            parent.pack_propagate(False)


            novus_logo = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
            novus_logo = novus_logo.resize((50, 50))
            self.novus_photo = CTkImage(novus_logo, size=(50, 50))

 
            #Buttons Images
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
            user_email = self.controller.session.get('useremail')



            # Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=60)

            vol_stat_search = CTkFrame(self, fg_color='white')
            vol_stat_search.pack(side="left", anchor="n", padx=(15, 15), pady=(5, 0), fill='x')

            CTkLabel(vol_stat_search,
                    text="TABLES:",
                    font=('Futura', 15, 'bold'),
                    width=100,
                    anchor="w").pack(side="left")

            self.vol_stat_var = tk.StringVar(value="None")
            self.vol_stat_dd = CTkComboBox(vol_stat_search,
                                            variable=self.vol_stat_var,
                                            values=["Client Audit", "Order Audit", "Product Audit", "Supplier Audit", "Material Audit"],
                                            width=100,
                                            height=25,
                                            border_width=1,
                                            corner_radius=6,
                                            command=self.on_table_change)
            self.vol_stat_dd.pack(side="left", padx=5) 



            #Change to Hard Delete - Recover - Search
            #Add Filter Button (Client to User Recovery)

            self.del_btn = self.add_del_upd('DELETE', '#e74c3c', command=self.hard_delete) #Hard Delete
            self.update_btn = self.add_del_upd('RECOVER', '#2ecc71', command=self.recover_data) #Make Visible
            self.logs_btn = self.add_del_upd('LOGS', '#3498db', command=self.show_logs_popup)

            # Cell Font
            self.row_font = font.Font(family="Futura", size=13)

            # Title Font
            self.head_font = font.Font(family="Futura", size=15, weight='bold')


            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Custom.Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=self.row_font, bordercolor="#cccccc", borderwidth=1)
            style.configure("Custom.Treeview.Heading", background="#007acc", foreground="white", font=self.head_font)
            style.map("Custom.Treeview", background=[('selected', '#b5d9ff')])



            tree_frame = tk.Frame(self)
            tree_frame.place(x=130, y=105, width=1100, height=475)
            tree_frame.pack_propagate(False)


            self.inventory_tree = ttk.Treeview(        
                tree_frame, 
                columns=('col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10', 'col11'), 
                show='headings', 
                style='Custom.Treeview'
        )
        
            self.inventory_tree.bind("<Double-1>", self.show_info)

            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.inventory_tree.xview)
            self.inventory_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.inventory_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Add a small frame in the corner to avoid scrollbar overlap
            corner_grip = tk.Frame(tree_frame)
            corner_grip.grid(row=1, column=1, sticky="nsew")

    def on_table_change(self, selection):
        #Selects the Table from Dropdown
        #Table Name = Value For Query
        self.current_selection = selection
        if selection == "None":
            self.clear_treeview()
            return
        
        #Selection = Table Name = Loads Query = Loads Table
        self.load_audit_data(selection)

    def _column_heads(self, columns, text):
        self.inventory_tree.heading(columns, text=text)
        self.inventory_tree.column(columns, width=195)

    def show_logs_popup(self):
        """Display a popup with all log buttons"""
        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("Logs Options")
        popup.geometry("320x280")  # Adjusted dimensions
        popup.configure(bg="white")
        popup.resizable(False, False)
        popup.transient(self)  # Set to be on top of the parent window
        popup.grab_set()  # Make window modal
        
        # Center the popup window
        center_window(popup)
        
        # Create main frame for buttons
        main_frame = CTkFrame(popup, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = CTkLabel(
            main_frame,
            text="Select Log Type",
            font=('Roboto', 16, 'bold'),
            text_color="#2a4d69"
        )
        title_label.pack(pady=(0, 10))
        
        # User Logs button
        user_logs_btn = CTkButton(
            main_frame,
            text="User Logs",
            fg_color="#2980b9",
            hover_color="#3498db",
            text_color="white",
            font=('Roboto', 12, 'bold'),
            command=lambda: [user_logs_to_sheets(), popup.destroy()],
            width=250,
            height=35,
            corner_radius=8
        )
        user_logs_btn.pack(pady=5)
        
        # User Activity Logs button
        activity_logs_btn = CTkButton(
            main_frame,
            text="User Activity Logs",
            fg_color="#2980b9",
            hover_color="#3498db",
            text_color="white",
            font=('Roboto', 12, 'bold'),
            command=lambda: [action_logs_to_sheets(), popup.destroy()],
            width=250,
            height=35,
            corner_radius=8
        )
        activity_logs_btn.pack(pady=5)
        
        # Settings Logs button
        settings_logs_btn = CTkButton(
            main_frame,
            text="Settings Logs",
            fg_color="#2980b9",
            hover_color="#3498db",
            text_color="white",
            font=('Roboto', 12, 'bold'),
            command=lambda: [settings_logs_to_sheets(), popup.destroy()],
            width=250,
            height=35,
            corner_radius=8
        )
        settings_logs_btn.pack(pady=5)
        
        # Product Logs button
        product_logs_btn = CTkButton(
            main_frame,
            text="Product Logs",
            fg_color="#2980b9",
            hover_color="#3498db",
            text_color="white",
            font=('Roboto', 12, 'bold'),
            command=lambda: [product_logs_to_sheets(), popup.destroy()],
            width=250,
            height=35,
            corner_radius=8
        )
        product_logs_btn.pack(pady=5)

    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, width=90, fg_color=fg_color, command=command, font=('Futura', 13, 'bold'))
        button.pack(side="left", anchor="n", padx=4)

    def _add_mat(self, label_text, y):
        label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.mat_window, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry

    def load_audit_data(self, table_name):
        self.clear_treeview()
        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")

            query_map = {
                'Client Audit': {
                    'headers': ['Client ID', 'Name', 'Email', 'Address', 'Contact Number', 'Date Created', 'Last Updated'],
                    'widths': [200, 200, 200, 200, 200, 200, 200],
                    'query' : "SELECT client_id, client_name, client_email, client_address, client_contactnum, date_created, last_updated FROM clients WHERE is_active = 0",
                    'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7']
                },
                'Material Audit': {
                    'headers': ['Material ID', 'Material Name', 'Description', 'Quantity', 'Threshold', 'Supplier', 'Shelf Life'],
                    'widths': [150, 150, 200, 100, 100, 100, 150],
                    'query' : "SELECT mat_id, mat_name, mat_description, current_stock, min_stock_level, supplier_id, shelf_life_days FROM raw_mats WHERE is_active = 0",
                    'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7']
                },
                'Order Audit': {
                    'headers': ['Order ID', 'Order Name', 'Product ID', 'Client ID', 'Quantity', 'Deadline', 'Order Data', 'Staus Quo'],
                    'widths': [200, 200, 200, 200, 200, 200, 200, 200],
                    'query' : "SELECT order_id, order_name, product_id, client_id, quantity, deadline, order_date, status_quo FROM orders WHERE is_active = 0",
                    'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8']
                },
                'Product Audit': {
                    'headers': ['Product ID', 'Product Name', 'Materials', 'Created Date', 'Status Quo'],
                    'widths': [200, 200, 200, 200, 200],
                    'query' : "SELECT product_id, product_name, materials, created_date, status_quo FROM products WHERE is_active = 0",
                    'columns': ['col1', 'col2', 'col3', 'col4', 'col5']
                },
                'Supplier Audit': {
                    'headers' : ['Supplier ID', 'Supplier Name', 'Supplier Address', 'Supplier Number', 'Supplier Email', 'Personnel', 'Rating', 'Delivered Date'],
                    'widths' : [200, 200, 200, 200, 200, 200, 200, 200],
                    'query': "SELECT supplier_id, supplier_name, supplier_add, supplier_num, supplier_mail, contact_person, rating, delivered_date FROM suppliers WHERE is_active = 0",
                    'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8']
                },
            }

            if table_name in query_map:
                config = query_map[table_name]
                self.inventory_tree['columns'] = config['columns']

                for col, text, width in zip(config['columns'], config['headers'], config['widths']):
                    self._column_heads(col, text)
                    self.inventory_tree.column(col, width=width)

                c.execute(config['query'])
                records = c.fetchall()
                for record in records:
                    self.inventory_tree.insert('', 'end', values=record)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching data: {e}")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()


    def hard_delete(self):
        selected = self.inventory_tree.focus()
        values = self.inventory_tree.item(selected, 'values')

        if not selected or not values:
            messagebox.showwarning("No selection", "Please select an item to delete.")
            return

        if getattr(self, "current_selection", "None") == "None":
            messagebox.showwarning("No selection", "Please select a valid audit type.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this record?")
        if not confirm:
            return

        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute('PRAGMA foreign_keys = ON')

            table_map = {
                'Client Audit': ('clients', 'client_id'),
                'Order Audit': ('orders', 'order_id'),
                'Product Audit': ('products', 'product_id'),
                'Supplier Audit': ('suppliers', 'supplier_id'),
                'Material Audit': ('raw_mats', 'mat_id'),
            }

            if self.current_selection not in table_map:
                messagebox.showwarning("Invalid selection", "Unsupported audit type.")
                return

            table_name, id_column = table_map[self.current_selection]
            record_id = values[0]

            if table_name == "orders":
                c.execute("SELECT product_id, quantity FROM orders WHERE order_id = ?", (record_id,))
                row = c.fetchone()
                if row:
                    product_id, order_qty = row
                    try:
                        order_qty = int(order_qty)
                    except Exception:
                        try:
                            order_qty = int(float(order_qty))
                        except Exception:
                            order_qty = 0

                    c.execute("SELECT materials FROM products WHERE product_id = ?", (product_id,))
                    prod = c.fetchone()
                    if prod and prod[0]:
                        materials_field = str(prod[0])
                        parsed_items = []

                        #JSON Conversion
                        try:
                            import json
                            parsed = json.loads(materials_field)
                            if isinstance(parsed, dict):
                                for k, v in parsed.items():
                                    parsed_items.append((str(k), float(v)))
                            elif isinstance(parsed, list):
                                for item in parsed:
                                    if isinstance(item, dict):
                                        mat_id = item.get('mat_id') or item.get('id') or item.get('material')
                                        qty = item.get('qty') or item.get('quantity') or item.get('amount') or 1
                                        parsed_items.append((str(mat_id), float(qty)))
                                    elif isinstance(item, (list, tuple)) and len(item) >= 2:
                                        parsed_items.append((str(item[0]), float(item[1])))
                        except Exception:
                            # fallback token parsing: handle "name:qty", "name - qty", "name qty", "name(qty)" and "name"
                            import re
                            tokens = re.split(r'[;,]', materials_field)
                            for token in tokens:
                                token = token.strip()
                                if not token:
                                    continue
                                # patterns like "try - 1", "mat:2", "mat 2", "mat(2)"
                                m = re.match(r'^(?P<name>.+?)\s*(?:[:\-\(]\s*(?P<qty>\d+(\.\d+)?)\s*\)?)\s*$', token)
                                if m:
                                    name = m.group('name').strip()
                                    try:
                                        qty = float(m.group('qty')) if m.group('qty') else 1.0
                                    except Exception:
                                        qty = 1.0
                                    parsed_items.append((name, qty))
                                else:
                                    # last-resort: separate by whitespace and try last token numeric
                                    parts = token.rsplit(None, 1)
                                    if len(parts) == 2 and re.fullmatch(r'\d+(\.\d+)?', parts[1].strip()):
                                        parsed_items.append((parts[0].strip(), float(parts[1].strip())))
                                    else:
                                        parsed_items.append((token, 1.0))

                        print(f"[hard_delete] product_id={product_id} order_qty={order_qty} materials_field={materials_field} parsed_items={parsed_items}")

                        if parsed_items:
                            import re, difflib
                            missing = []
                            c.execute("SELECT mat_id, mat_name FROM raw_mats")
                            mat_rows = c.fetchall()
                            mat_ids = [r[0] for r in mat_rows if r[0]]
                            mat_names = [r[1] for r in mat_rows if r[1]]

                            def normalize(s):
                                return re.sub(r'[^0-9a-z]', '', str(s).lower())

                            normalized_map = {normalize(r[0]): r[0] for r in mat_rows if r[0]}
                            normalized_names_map = {normalize(r[1]): r[0] for r in mat_rows if r[1]}

                            for raw_token, per_qty in parsed_items:
                                try:
                                    add_qty = int(per_qty * order_qty)
                                except Exception:
                                    add_qty = int(order_qty or 0)

                                candidate = str(raw_token).strip()
                                found_id = None

                                # exact id or name (case-insensitive)
                                c.execute("SELECT mat_id FROM raw_mats WHERE lower(mat_id)=lower(?) LIMIT 1", (candidate,))
                                rowm = c.fetchone()
                                if rowm:
                                    found_id = rowm[0]
                                if not found_id:
                                    c.execute("SELECT mat_id FROM raw_mats WHERE lower(mat_name)=lower(?) LIMIT 1", (candidate,))
                                    rowm = c.fetchone()
                                    if rowm:
                                        found_id = rowm[0]

                                # normalized maps
                                if not found_id:
                                    norm = normalize(candidate)
                                    if norm in normalized_map:
                                        found_id = normalized_map[norm]
                                    elif norm in normalized_names_map:
                                        found_id = normalized_names_map[norm]

                                # fuzzy match
                                if not found_id:
                                    pool = [str(x) for x in (mat_ids + mat_names)]
                                    matches = difflib.get_close_matches(candidate, pool, n=1, cutoff=0.6)
                                    if matches:
                                        match = matches[0]
                                        if match in mat_ids:
                                            found_id = match
                                        else:
                                            for mid, mname in mat_rows:
                                                if mname == match:
                                                    found_id = mid
                                                    break

                                if found_id:
                                    c.execute("UPDATE raw_mats SET current_stock = current_stock + ? WHERE mat_id = ?", (add_qty, found_id))
                                    affected = c.rowcount
                                    print(f"[hard_delete] updated mat_id={found_id} candidate='{candidate}' add_qty={add_qty} affected={affected}")
                                else:
                                    missing.append(candidate)
                                    print(f"[hard_delete] no match for candidate='{candidate}'")

                            conn.commit()
                            if missing:
                                messagebox.showwarning("Materials Not Found", f"The following materials were not updated because they were not found in raw_mats: {', '.join(missing)}")
                        else:
                            messagebox.showwarning("Warning", "Could not parse product materials; no material stock adjusted.")
                    else:
                        messagebox.showwarning("Warning", "Product materials not found; stock not adjusted.")

            c.execute(f"DELETE FROM {table_name} WHERE {id_column} = ?", (record_id,))
            if c.rowcount == 0:
                messagebox.showwarning("Not found", "No record was deleted (record may not exist).")
                conn.rollback()
                return

            conn.commit()
            messagebox.showinfo("Deleted", "Record has been permanently deleted.")
            self.load_audit_data(self.current_selection)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while connecting to the database: {e}")
        finally:
            if conn:
                conn.close()

    def recover_data(self):
        #Make is_active = 1
        #Visible Again
        selected = self.inventory_tree.focus()

        values = self.inventory_tree.item(selected, 'values')


        if not selected:
            messagebox.showwarning("No selection", "Please select an item to recover.")
            return
        
        if not values:
            messagebox.showwarning("No values", "Selected item has no values.")
            return
        
        if self.current_selection == "None":
            messagebox.showwarning("No selection", "Please select a valid audit type.")
            return
        
        confirm = messagebox.askyesno("Confirm Recover", "Are you sure you want to recover this record?")
        if confirm:
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute('PRAGMA foreign_keys = ON')

                table_map = {
                    'Client Audit': ('clients', 'client_id'),
                    'Order Audit': ('orders', 'order_id'),
                    'Product Audit': ('products', 'product_id'),
                    'Supplier Audit': ('suppliers', 'supplier_id'),
                    'Material Audit': ('raw_mats', 'mat_id'),
                }

                if self.current_selection in table_map:
                    table_name, id_column = table_map[self.current_selection]
                    record_id = values[0]
                    c.execute(f"UPDATE {table_name} SET is_active = 1 WHERE {id_column} = ?", (record_id,))
                    conn.commit()
                    messagebox.showinfo("Recovered", "Record has been recovered.")
                    self.load_audit_data(self.current_selection)

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while connecting to the database: {e}")
                return
            finally:
                if conn:
                    conn.close()


    def show_info(self, event):
        print('Info')


    def clear_treeview(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)



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

    def on_show(self):
        on_show(self) 

    def handle_logout(self):
        handle_logout(self)
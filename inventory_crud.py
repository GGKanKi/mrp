import tkinter as tk
from tkcalendar import Calendar
from tkinter import font
from tkcalendar import DateEntry
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
import uuid
import bcrypt
import pandas as pd
import os

import sys
#Imported Files
from pages_handler import FrameNames

from global_func import on_show, handle_logout, send_email_with_attachment, load_credentials_if_logged_in, resource_path

class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.mat_window = None
            self.update_window = None
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
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

            print(user_email)


            # Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=60)

            vol_stat_search = CTkFrame(self, fg_color='white')
            vol_stat_search.pack(side="left", anchor="n", padx=(0, 5), pady=(5, 0), fill='x')

            CTkLabel(vol_stat_search,
                    text="STATUS:",
                    font=('Futura', 15, 'bold'),
                    width=100,
                    anchor="w").pack(side="left")

            self.vol_stat_var = tk.StringVar(value="None")
            self.vol_stat_dd = CTkComboBox(vol_stat_search,
                                            variable=self.vol_stat_var,
                                            values=["All", "Low Count", "Average Count", "High Count"],
                                            width=100,
                                            height=25,
                                            border_width=1,
                                            corner_radius=6)
            self.vol_stat_dd.pack(side="left", padx=(0, 5)) 

            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.upd_srch)
            self.add_btn = self.add_del_upd('ADD MATERIAL', '#2ecc71', command=self.add_mats)
            self.del_btn = self.add_del_upd('DELETE MATERIAL', '#e74c3c', command=self.del_mats)
            self.update_btn = self.add_del_upd('UPDATE MATERIAL', '#f39c12', command=self.upd_mats)
            self.refresh_btn = self.add_del_upd('REFRESH', '#3498db', command=self.load_mats_from_db)



            # Treeview style
            self.row_font = font.Font(family="Futura", size=13)
            self.head_font = font.Font(family="Futura", size=15, weight='bold')

            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Custom.Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=self.row_font, bordercolor="#cccccc", borderwidth=1)
            style.configure("Custom.Treeview.Heading", background="#007acc", foreground="white", font=self.head_font)
            style.map("Custom.Treeview", background=[('selected', '#b5d9ff')])



            tree_frame = tk.Frame(self)
            tree_frame.place(x=130, y=105, width=1100, height=475)
            tree_frame.pack_propagate(False)

            self.inventory_tree = ttk.Treeview(
            tree_frame, columns=('mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days'), show='headings', style='Custom.Treeview')
            self._column_heads('mat_id', 'MATERIAL ID')
            self._column_heads('mat_name', 'NAME')
            self._column_heads('mat_description', 'DESCRIPTION')
            self._column_heads('mat_volume', 'VOLUME')
            self._column_heads('current_stock', 'CURRENT STOCK')
            self._column_heads('unit_of_measure', 'UNIT OF MEASUREMENT')
            self._column_heads('min_stock_level', 'MINIMUM STOCK LEVEL')
            self._column_heads('mat_order_date', 'DELIVERY DATE')
            self._column_heads('supplier_id', 'SUPPLIER ID')
            self._column_heads('last_restocked', 'LAST RESTOCKED')
            self._column_heads('shelf_life_days', 'SHELF LIFE (DAYS)')
            for col in ('mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days'):
                self.inventory_tree.column(col, width=200, stretch=False)

            self.inventory_tree.bind("<Double-1>", self.material_info)

            # Configure stock level row highlights
            self.inventory_tree.tag_configure('low', background='light coral')
            self.inventory_tree.tag_configure('medium', background='orange')
            self.inventory_tree.tag_configure('high', background='light green')

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
            self.load_mats_from_db()

    def destroy(self):
        """Override destroy to clean up any open Toplevel windows."""
        if self.mat_window and self.mat_window.winfo_exists():
            self.mat_window.destroy()
        if hasattr(self, 'update_window') and self.update_window and self.update_window.winfo_exists():
            self.update_window.destroy()
        super().destroy()

    def _column_heads(self, columns, text):
        self.inventory_tree.heading(columns, text=text)
        self.inventory_tree.column(columns, width=195)

    def add_del_upd(self, text, fg_color, command=None):
        button = CTkButton(self, text=text, width=80, fg_color=fg_color, command=command, font=('Futura', 13, 'bold'))
        button.pack(side="left", anchor="n", padx=2)

    def _add_mat(self, label_text, y):
        label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.mat_window, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    
    def load_mats_from_db(self):
        supplier_email = self.controller.session.get('useremail')
        usertype = self.controller.session.get('usertype')

        if usertype in ('admin', 'owner', 'manager', 'staff'):
            try:
                conn = sqlite3.connect(resource_path("main.db"))
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM raw_mats WHERE is_active = 1")
                rows = cursor.fetchall()

                # Clear existing rows
                for i in self.inventory_tree.get_children():
                    self.inventory_tree.delete(i)

                for row in rows:
                    tags = ()
                    try:
                        # Indices based on raw_mats schema: current_stock=4, min_stock_level=6
                        current_stock = int(row[4]) if row[4] is not None else 0
                        min_stock_level = int(row[6]) if row[6] is not None else 0

                        if current_stock <= min_stock_level:
                            tags = ('low',)
                        elif min_stock_level > 0 and current_stock <= min_stock_level * 1.2:
                            tags = ('medium',)
                        else:
                            tags = ('high',)
                    except (ValueError, TypeError, IndexError):
                        # Fallback if values are not convertible to int or index is out of range
                        pass
                    self.inventory_tree.insert("", "end", values=row, tags=tags)

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        elif usertype == 'supplier':
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                fetch_supplies = c.execute('''
                    SELECT rm.* 
                    FROM raw_mats rm
                    JOIN suppliers s ON rm.supplier_id = s.supplier_id
                    WHERE s.supplier_mail = ?
                ''', (supplier_email,)).fetchall()

                # Clear existing rows
                for i in self.inventory_tree.get_children():
                    self.inventory_tree.delete(i)

                # Insert supplier rows with same low stock check
                for row in fetch_supplies:
                    tags = ()
                    try:
                        # Indices based on raw_mats schema: current_stock=4, min_stock_level=6
                        current_stock = int(row[4]) if row[4] is not None else 0
                        min_stock_level = int(row[6]) if row[6] is not None else 0

                        if current_stock <= min_stock_level:
                            tags = ('low',)
                        elif min_stock_level > 0 and current_stock <= min_stock_level * 1.2:
                            tags = ('medium',)
                        else:
                            tags = ('high',)
                    except (ValueError, TypeError, IndexError):
                        # Fallback if values are not convertible to int or index is out of range
                        pass
                    self.inventory_tree.insert('', 'end', values=row, tags=tags)

            except sqlite3.Error as e:
                messagebox.showerror('Error', f'Database Error: {e}')
            finally:
                if conn:
                    conn.close()



    #Inventory Load if Usertype = Supplier 
    #Load all their supplied materials
    def load_mats_supplier(self):

        supplier_email = self.controller.session.get('useremail')
        print(supplier_email)

        if not supplier_email:  # session not ready
            print("DEBUG: No session email yet, skipping supplier load.")
            return

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            fetch_supplies = c.execute('''
                            SELECT * FROM raw_mats 
                            WHERE supplier_mail IN (SELECT useremail FROM users WHERE useremail = ?)
                            ''', (supplier_email,)).fetchall()
            

            for i in self.inventory_tree.get_children(i):
                self.inventory_tree.delete()

            for row in fetch_supplies:
                self.inventory_tree.insert('', 'end', values=row)

        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Database Error: {e}')
            return
        finally:
            if conn:
                conn.close()



    def add_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to add materials.")
            return

        try:
            if self.mat_window and self.mat_window.winfo_exists():
                self.mat_window.lift()
                return

            self.mat_window = tk.Toplevel(self)
            self.mat_window.geometry('500x550')
            self.mat_window.title('Add Material')
            self.mat_window.config(bg='white')

            labels = [
                ("Material Name:", False),
                ("Material Description:", False),
                ("Material Volume:", True),
                ("Unit of Measurement:", True),
                ("Minimum Stock Level:", False), 
                ("Shelf Life:", False)
            ]

            self.mat_entries = []
            self.all_volume_options = []
            self.all_unit_options = []


            # Fetch volume options for the dropdown
            def get_volume_options():
                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    c.execute("SELECT volume_name FROM material_volumes ORDER BY volume_name")
                    return [row[0] for row in c.fetchall()]
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Could not load volume options: {e}", parent=self.mat_window)
                    return []
                finally:
                    if conn:
                        conn.close()

            self.all_volume_options = get_volume_options()

            # Fetch unit of measurement options for the dropdown
            def get_unit_options():
                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    c.execute("SELECT unit_name FROM unit_of_measures ORDER BY unit_name")
                    return [row[0] for row in c.fetchall()]
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Could not load unit options: {e}", parent=self.mat_window)
                    return []
                finally:
                    if conn:
                        conn.close()

            self.all_unit_options = get_unit_options()

            for i, (label_text, is_volume) in enumerate(labels):
                label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')

                if label_text == "Material Volume:":
                    frame = CTkFrame(self.mat_window, fg_color="transparent")
                    frame.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                    self.volume_var = tk.StringVar(value=self.all_volume_options[0] if self.all_volume_options else "")
                    self.volume_combo = CTkComboBox(frame, variable=self.volume_var, values=self.all_volume_options, height=28, width=180, border_width=2, border_color='#6a9bc3')
                    self.volume_combo.pack(side="left", fill="x", expand=True)
                    self.volume_combo.bind('<KeyRelease>', self._search_volumes)
                    edit_btn = CTkButton(frame, text="Edit", width=40, command=lambda v=self.volume_var: self.manage_volumes(v))
                    edit_btn.pack(side="left", padx=(5,0))
                    entry = self.volume_combo
                elif label_text == "Unit of Measurement:":
                    frame = CTkFrame(self.mat_window, fg_color="transparent")
                    frame.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                    self.unit_var = tk.StringVar(value=self.all_unit_options[0] if self.all_unit_options else "")
                    self.unit_combo = CTkComboBox(frame, variable=self.unit_var, values=self.all_unit_options, height=28, width=180, border_width=2, border_color='#6a9bc3')
                    self.unit_combo.pack(side="left", fill="x", expand=True)
                    self.unit_combo.bind('<KeyRelease>', self._search_units)
                    edit_btn = CTkButton(frame, text="Edit", width=40, command=lambda u=self.unit_var: self.manage_units(u))
                    edit_btn.pack(side="left", padx=(5,0))
                    entry = self.unit_combo
                else:
                    entry = CTkEntry(self.mat_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                    entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')

                self.mat_entries.append(entry)

            # 🔹 Order Date (calendar)
            tk.Label(self.mat_window, text="Order Date:", font=('Futura', 13, 'bold'), bg='white').grid(
                row=len(labels), column=0, padx=15, pady=10, sticky='e'
            )
            self.order_date_entry = DateEntry(
                self.mat_window,
                width=18,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.order_date_entry.grid(row=len(labels), column=1, padx=10, pady=10, sticky='w')

            # 🔹 Supplier dropdown
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute('SELECT supplier_id FROM suppliers WHERE is_active = 1')
            suppliers = [row[0] for row in c.fetchall()]
            conn.close()

            self.suppliers_ids = tk.StringVar()
            self.suppliers_ids.set(suppliers[0] if suppliers else "")

            CTkLabel(self.mat_window, text='Supplier ID:', font=('Futura', 13, 'bold')).grid(
                row=len(labels)+1, column=0, padx=15, pady=10, sticky='e'
            )
            self.suppliers_ids = tk.StringVar(value=suppliers[0] if suppliers else "")
            supplier_id_drop = CTkOptionMenu(
                self.mat_window,
                variable=self.suppliers_ids,
                values=suppliers if suppliers else [""]
            )
            supplier_id_drop.grid(row=len(labels)+1, column=1, padx=10, pady=10, sticky='w')

            def mat_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                mat_id = f"MAT-{uuid.uuid4().hex[:8].upper()}"

                mat_data = []
                # Manually build mat_data to handle the removed 'Current Stock' field
                mat_data.append(self.mat_entries[0].get().strip()) # Name
                mat_data.append(self.mat_entries[1].get().strip()) # Description
                mat_data.append(self.mat_entries[2].get()) # Volume
                mat_data.append(0) # Default Current Stock to 0
                mat_data.append(self.mat_entries[3].get()) # Unit of Measurement
                mat_data.append(self.mat_entries[4].get().strip()) # Min Stock
                mat_data.append(self.mat_entries[5].get().strip()) # Shelf Life

                order_date = self.order_date_entry.get_date().strftime('%Y-%m-%d')
                supplier_id = self.suppliers_ids.get().strip()

                # This loop is now just for validation, not data gathering
                for i, (label_text, is_dropdown) in enumerate(labels):
                    widget_value = self.mat_entries[i].get()
                    # For dropdowns, just check if a value exists. For entries, strip whitespace.
                    is_empty = not widget_value if is_dropdown else not widget_value.strip()

                    if is_empty:
                        messagebox.showerror("Input Error", f"{label_text.replace(':', '')} is required.")
                        return

                # Validate required fields
                # Check string-based fields in mat_data, skipping the integer 'current_stock' at index 3
                required_strings = [mat_data[0], mat_data[1], mat_data[2], mat_data[4], mat_data[5], mat_data[6]]
                if not all(required_strings) or not supplier_id:
                    # This provides a more specific error if a field is empty.
                    # The loop above should catch this first, but this is a good safeguard.
                    messagebox.showerror("Input Error", "A required field is empty. Please check all inputs.")
                    return

                try:
                    conn = sqlite3.connect(resource_path("main.db"))
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO raw_mats (
                            mat_id, mat_name, mat_description,
                            mat_volume, current_stock, unit_of_measure, min_stock_level, 
                            shelf_life_days, mat_order_date, supplier_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (mat_id, mat_data[0], mat_data[1], mat_data[2], mat_data[3], mat_data[4], mat_data[5], mat_data[6], order_date, supplier_id))
                    conn.commit()

                    messagebox.showinfo("Success", "Material registered successfully!")
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?,?,?)""",
                            (user_id, f"Added Material ID: {mat_data[0]}", timestamp))
                    conn.commit()
                    
                    # Log to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="create",
                        feature="inventory",
                        operation="add_material",
                        details=f"Added material ID: {mat_id}, Name: {mat_data[0]}, Supplier: {supplier_id}"
                    )

                    self.load_mats_from_db()
                    self.mat_window.destroy()


                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: raw_mats.mat_id" in str(e):
                        messagebox.showerror("Input Error", "Material ID already exists. Please use a unique ID.")
                    elif "UNIQUE constraint failed: raw_mats.mat_name" in str(e):
                        messagebox.showerror("Input Error", "Material name already exists. Please use a unique name.")
                    else:
                        messagebox.showerror("Database Error", str(e))
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

            submit_btn = CTkButton(
                self.mat_window, text='Submit All',
                font=("Arial", 12), width=120, height=30,
                bg_color='white', fg_color='blue',
                corner_radius=10, border_width=2, border_color='black',
                command=mat_to_db
            )
            submit_btn.grid(row=len(labels)+2, column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Materials window: {e}")

    def _search_volumes(self, event):
        """Filter the material volume combobox values based on user input."""
        # Determine which combobox to update based on which window is open
        if self.update_window and self.update_window.winfo_exists():
            combo = self.update_volume_combo
        else:
            combo = self.volume_combo

        value = event.widget.get()
        if value == '':
            combo.configure(values=self.all_volume_options)
        else:
            data = []
            for item in self.all_volume_options:
                if value.lower() in item.lower():
                    data.append(item)
            combo.configure(values=data)

    def _search_units(self, event):
        """Filter the unit of measurement combobox values based on user input."""
        if self.update_window and self.update_window.winfo_exists():
            combo = self.update_unit_combo
        else:
            combo = self.unit_combo
        value = event.widget.get()
        if value == '':
            combo.configure(values=self.all_unit_options)
        else:
            data = []
            for item in self.all_unit_options:
                if value.lower() in item.lower():
                    data.append(item)
            combo.configure(values=data)

    def manage_volumes(self, volume_var_to_update=None):
        """Open a Toplevel window to add or delete material volume options."""
        if hasattr(self, 'vol_window') and self.vol_window.winfo_exists():
            self.vol_window.lift()
            return

        self.vol_window = tk.Toplevel(self)
        vol_window = self.vol_window
        vol_window.title("Manage Material Volumes")
        vol_window.geometry("400x450")
        vol_window.grab_set()
        vol_window.configure(bg='white')

        # --- Add Volume ---
        add_frame = ttk.Frame(vol_window, style="Card.TFrame")
        add_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(add_frame, text="New Volume:", font=('Futura', 13, 'bold')).pack(side="left", padx=5)
        new_volume_entry = ttk.Entry(add_frame)
        new_volume_entry.pack(side="left", padx=5, expand=True, fill="x")

        def add_new_volume():
            new_vol = new_volume_entry.get().strip()
            if not new_vol:
                messagebox.showerror("Input Error", "Volume name cannot be empty.", parent=vol_window)
                return
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute("INSERT INTO material_volumes (volume_name) VALUES (?)", (new_vol,))
                conn.commit()
                messagebox.showinfo("Success", f"Volume '{new_vol}' added.", parent=vol_window)
                refresh_list()
                new_volume_entry.delete(0, 'end')
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Volume '{new_vol}' already exists.", parent=vol_window)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e), parent=vol_window)
            finally:
                conn.close()

        add_btn = ttk.Button(add_frame, text="Add", command=add_new_volume)
        add_btn.pack(side="left", padx=5)

        # --- Volume List ---
        list_frame = ttk.LabelFrame(vol_window, text="Existing Volumes")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def select_volume(volume_name):
            if volume_var_to_update:
                volume_var_to_update.set(volume_name)
                on_close()
                messagebox.showinfo("Selected", f"Volume '{volume_name}' has been selected.", parent=self.mat_window or self.update_window)

        def refresh_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT volume_name FROM material_volumes ORDER BY volume_name")
            volumes = c.fetchall()
            conn.close()
            
            for i, (vol_name,) in enumerate(volumes):
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill="x", pady=2, padx=5)
                label = ttk.Label(item_frame, text=vol_name, cursor="hand2")
                label.pack(side="left", padx=5)
                label.bind("<Button-1>", lambda e, v=vol_name: select_volume(v))
                del_btn = ttk.Button(item_frame, text="Delete",
                                     command=lambda v=vol_name: delete_volume(v))
                del_btn.pack(side="right", padx=5)

        def delete_volume(volume_name):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{volume_name}'?", parent=vol_window):
                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    c.execute("DELETE FROM material_volumes WHERE volume_name = ?", (volume_name,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Volume '{volume_name}' deleted.", parent=vol_window)
                    refresh_list()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e), parent=vol_window)
                finally:
                    conn.close()

        refresh_list()

        # --- Close and Refresh Dropdowns ---
        def on_close():
            # This is a bit tricky as we need to refresh dropdowns in potentially open windows.
            # A simpler approach is to just close this window. The user can reopen the add/update window
            # to see the new options. A more complex solution would involve callbacks.
            if self.mat_window and self.mat_window.winfo_exists():
                self.mat_window.destroy()
                self.add_mats() # Re-open it to get fresh data
            if self.update_window and self.update_window.winfo_exists():
                self.update_window.destroy()
                messagebox.showinfo("Info", "Please re-open the update window to see the new volume options.", parent=vol_window)
            vol_window.destroy()

        vol_window.protocol("WM_DELETE_WINDOW", on_close)
        close_button = ttk.Button(vol_window, text="Close", command=on_close)
        close_button.pack(pady=10)

    def manage_units(self, unit_var_to_update=None):
        """Open a Toplevel window to add or delete unit of measurement options."""
        if hasattr(self, 'unit_window') and self.unit_window.winfo_exists():
            self.unit_window.lift()
            return

        self.unit_window = tk.Toplevel(self)
        unit_window = self.unit_window
        unit_window.title("Manage Units of Measurement")
        unit_window.geometry("400x450")
        unit_window.grab_set()
        unit_window.configure(bg='white')

        # --- Add Unit ---
        add_frame = ttk.Frame(unit_window, style="Card.TFrame")
        add_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(add_frame, text="New Unit:", font=('Futura', 13, 'bold')).pack(side="left", padx=5)
        new_unit_entry = ttk.Entry(add_frame)
        new_unit_entry.pack(side="left", padx=5, expand=True, fill="x")

        def add_new_unit():
            new_unit = new_unit_entry.get().strip()
            if not new_unit:
                messagebox.showerror("Input Error", "Unit name cannot be empty.", parent=unit_window)
                return
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute("INSERT INTO unit_of_measures (unit_name) VALUES (?)", (new_unit,))
                conn.commit()
                messagebox.showinfo("Success", f"Unit '{new_unit}' added.", parent=unit_window)
                refresh_list()
                new_unit_entry.delete(0, 'end')
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Unit '{new_unit}' already exists.", parent=unit_window)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e), parent=unit_window)
            finally:
                conn.close()

        add_btn = ttk.Button(add_frame, text="Add", command=add_new_unit)
        add_btn.pack(side="left", padx=5)

        # --- Unit List ---
        list_frame = ttk.LabelFrame(unit_window, text="Existing Units")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def select_unit(unit_name):
            if unit_var_to_update:
                unit_var_to_update.set(unit_name)
                on_close()
                messagebox.showinfo("Selected", f"Unit '{unit_name}' has been selected.", parent=self.mat_window or self.update_window)

        def refresh_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT unit_name FROM unit_of_measures ORDER BY unit_name")
            units = c.fetchall()
            conn.close()
            
            for i, (unit_name,) in enumerate(units):
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill="x", pady=2, padx=5)
                label = ttk.Label(item_frame, text=unit_name, cursor="hand2")
                label.pack(side="left", padx=5)
                label.bind("<Button-1>", lambda e, u=unit_name: select_unit(u))
                del_btn = ttk.Button(item_frame, text="Delete",
                                     command=lambda u=unit_name: delete_unit(u))
                del_btn.pack(side="right", padx=5)

        def delete_unit(unit_name):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{unit_name}'?", parent=unit_window):
                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    c.execute("DELETE FROM unit_of_measures WHERE unit_name = ?", (unit_name,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Unit '{unit_name}' deleted.", parent=unit_window)
                    refresh_list()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e), parent=unit_window)
                finally:
                    conn.close()

        refresh_list()

        def on_close():
            if self.mat_window and self.mat_window.winfo_exists():
                self.mat_window.destroy()
                self.add_mats()
            if self.update_window and self.update_window.winfo_exists():
                self.update_window.destroy()
                messagebox.showinfo("Info", "Please re-open the update window to see the new unit options.", parent=unit_window)
            unit_window.destroy()

        unit_window.protocol("WM_DELETE_WINDOW", on_close)
        close_button = ttk.Button(unit_window, text="Close", command=on_close)
        close_button.pack(pady=10)


    
    def upd_srch(self):
        usertype = self.controller.session.get('usertype')
        useremail = self.controller.session.get('useremail')
        user_id = self.controller.session.get('user_id')
        username = self.controller.session.get('username')

        search = self.search_entry.get().strip()
        vol_stat = self.vol_stat_var.get().strip()

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            if search:
                # Search by material name
                if usertype == 'supplier':
                    # Supplier search limited by supplier email
                    query = """
                        SELECT rm.* FROM raw_mats rm
                        JOIN suppliers s ON rm.supplier_id = s.supplier_id
                        WHERE rm.mat_name LIKE ?
                        AND s.supplier_mail = ?
                        ORDER BY rm.mat_name
                    """
                    params = (f'%{search}%', useremail)
                    results = c.execute(query, params).fetchall()
                else:
                    # Admin or other user types see all matching materials
                    query = "SELECT * FROM raw_mats WHERE mat_name LIKE ? ORDER BY mat_name"
                    params = (f'%{search}%',)
                    results = c.execute(query, params).fetchall()
                
                if not results:
                    messagebox.showinfo("No Results", f"No materials found matching '{search}'")
                    self.load_mats_from_db()
                    
                    # Log unsuccessful search to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="read",
                        feature="inventory",
                        operation="search_materials",
                        details=f"Search for '{search}' returned no results"
                    )
                    return

            elif vol_stat != "None" and usertype != 'supplier':
                # Filter by volume status for non-suppliers
                if vol_stat == "Low Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock <= min_stock_level ORDER BY mat_name"
                elif vol_stat == "Average Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock > min_stock_level AND current_stock <= min_stock_level * 2 ORDER BY mat_name"
                elif vol_stat == "High Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock > min_stock_level * 2 ORDER BY mat_name"
                else:
                    self.load_mats_from_db()
                    return
                    
                results = c.execute(query).fetchall()
                
                if not results:
                    messagebox.showinfo("No Results", f"No materials with {vol_stat} status")
                    self.load_mats_from_db()
                    return
                
                
            elif vol_stat != "None" and usertype == 'supplier':
                # Filter by volume status for suppliers (limited to their materials only)
                if vol_stat == "Low Count":
                    query = "SELECT rm.* FROM raw_mats rm JOIN suppliers s ON rm.supplier_id = s.supplier_id WHERE rm.current_stock <= rm.min_stock_level AND s.supplier_mail = ? ORDER by rm.mat_name"
                elif vol_stat == "Average Count":
                    query = "SELECT rm.* FROM raw_mats rm JOIN suppliers s ON rm.supplier_id = s.supplier_id WHERE rm.current_stock > rm.min_stock_level AND rm.current_stock <= rm.min_stock_level * 2 AND s.supplier_mail = ? ORDER by rm.mat_name"
                elif vol_stat == "High Count":
                    query = "SELECT rm.* FROM raw_mats rm JOIN suppliers s ON rm.supplier_id = s.supplier_id WHERE rm.current_stock > rm.min_stock_level * 2 AND s.supplier_mail = ? ORDER by rm.mat_name"
                else:
                    self.load_mats_from_db()
                    return
                results = c.execute(query, (useremail,)).fetchall()

                if not results:
                    messagebox.showinfo("No Results", f"No materials with {vol_stat} status")
                    self.load_mats_from_db()
                    return

            else:
                self.load_mats_from_db()
                return

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
                
            for item in results:
                tags = ()
                try:
                    # Indices based on raw_mats schema: current_stock=4, min_stock_level=6
                    current_stock = int(item[4]) if item[4] is not None else 0
                    min_stock_level = int(item[6]) if item[6] is not None else 0

                    if current_stock <= min_stock_level:
                        tags = ('low',)
                    elif min_stock_level > 0 and current_stock <= min_stock_level * 1.2:
                        tags = ('medium',)
                    else:
                        tags = ('high',)
                except (ValueError, TypeError, IndexError):
                    # Fallback if values are not convertible to int or index is out of range
                    pass
                self.inventory_tree.insert("", "end", values=item, tags=tags)

                
            # Log successful search to user_activity.log
            from log_f.user_activity_logger import user_activity_logger
            search_term = search if search else f"Filter by {vol_stat}"
            user_activity_logger.log_activity(
                user_id=user_id,
                username=username,
                action="read",
                feature="inventory",
                operation="search_materials",
                details=f"Search for '{search_term}' returned {len(results)} results"
            )

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error executing query: {str(e)}")
            self.load_mats_from_db()
        finally:
            if 'conn' in locals():
                conn.close()
                                          

    def del_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to delete materials.")
            return


        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a material to delete.")
            return

        try:
            values = self.inventory_tree.item(selected, 'values')
            mat_id = values[0]  # Assuming client_id is the first column

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete material ID '{mat_id}'?")
            if not confirm:
                return

            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT * FROM raw_mats WHERE mat_id =  ? AND is_active = 1 ", (mat_id,))
            row = c.fetchone()

            if row:
                c.execute("UPDATE raw_mats SET is_active = 0 WHERE mat_id = ?", (mat_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{mat_id}' has been deleted.")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f"Deleted Material ID: {mat_id}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="delete",
                    feature="inventory",
                    operation="delete_material",
                    details=f"Deleted material ID: {mat_id}, Name: {values[1]}"
                )
            else:
                messagebox.showinfo("Not Found", f"No material found with ID '{mat_id}'")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            conn.close()

    def upd_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to add materials.")
            return
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a material to update.")
            return

        # If an update window is already open, bring it to the front
        if self.update_window and self.update_window.winfo_exists():
            self.update_window.lift()
            return

        values = self.inventory_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        self.update_window = top # Store reference to the window
        top.title(f"Update Material - {original_id}")
        top.geometry("500x650")
        top.config(bg="white")
        top.resizable(False, False)

        fields = [
            ("Material ID", values[0], False),
            ("Material Name", values[1], True),
            ("Material Description", values[2], True),
            ("Material Volume", values[3], True), # This will be a dropdown
            ("Current Stock", values[4], False),
            ("Unit of Measurement", values[5], True),
            ("Minimum Stock Level", values[6], True),
            ("Material Delivery Date", values[7], True),
            ("Supplier ID", values[8], False),
            ("Last Restocked", values[9], False),
            ("Shelf Life (Days)", values[10], False)
        ]
        entries = []

        # Fetch volume options for the dropdown
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT volume_name FROM material_volumes ORDER BY volume_name") # Re-fetch for update window
            self.all_volume_options = [row[0] for row in c.fetchall()]
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load volume options: {e}", parent=top)
            self.all_volume_options = []

        # Fetch unit options for the dropdown
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT unit_name FROM unit_of_measures ORDER BY unit_name") # Re-fetch for update window
            self.all_unit_options = [row[0] for row in c.fetchall()]
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load unit options: {e}", parent=top)
            self.all_unit_options = []

        for i, (label, value, editable) in enumerate(fields):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            if label == "Material Delivery Date" or label == "Last Restocked":
                entry = DateEntry(top, width=18, background='darkblue', foreground='white', borderwidth=2)
                try:
                    if value:
                        entry.set_date(value)
                except Exception as e:
                    print(f"Error setting date for {label}: {e}")
                    pass
            elif label == "Material Volume":
                frame = CTkFrame(top, fg_color="transparent")
                volume_var = tk.StringVar(value=value if value in self.all_volume_options else (self.all_volume_options[0] if self.all_volume_options else ""))
                self.update_volume_combo = CTkComboBox(frame, variable=volume_var, values=self.all_volume_options, height=28, width=180, border_width=2, border_color='#6a9bc3')
                self.update_volume_combo.pack(side="left", fill="x", expand=True)
                self.update_volume_combo.bind('<KeyRelease>', self._search_volumes)
                edit_btn = CTkButton(frame, text="Edit", width=40, command=lambda v=volume_var: self.manage_volumes(v))
                edit_btn.pack(side="left", padx=(5,0))
                entry = frame # The whole frame is now the 'entry'
            elif label == "Unit of Measurement":
                frame = CTkFrame(top, fg_color="transparent")
                unit_var = tk.StringVar(value=value if value in self.all_unit_options else (self.all_unit_options[0] if self.all_unit_options else ""))
                self.update_unit_combo = CTkComboBox(frame, variable=unit_var, values=self.all_unit_options, height=28, width=180, border_width=2, border_color='#6a9bc3')
                self.update_unit_combo.pack(side="left", fill="x", expand=True)
                self.update_unit_combo.bind('<KeyRelease>', self._search_units)
                edit_btn = CTkButton(frame, text="Edit", width=40, command=lambda u=unit_var: self.manage_units(u))
                edit_btn.pack(side="left", padx=(5,0))
                entry = frame # The whole frame is now the 'entry'
            else:
                entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.insert(0, value)
                if not editable:
                    entry.configure(state='readonly')
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            entries.append(entry) # This should be outside the if

            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute('SELECT supplier_id FROM suppliers WHERE is_active = 1')
                suppliers = [row[0] for row in c.fetchall()]

                if label == "Supplier ID":
                    entry.destroy()
                    supplier_var = tk.StringVar(value=value)
                    supplier_dropdown = CTkOptionMenu(top, variable=supplier_var, values=suppliers if suppliers else [""])
                    supplier_dropdown.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                    entries[i] = supplier_dropdown

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                return

        def update_field(idx, col_name):
            entry = entries[idx]
            if isinstance(entry, DateEntry):
                new_value = entry.get_date().strftime('%Y-%m-%d')
            elif isinstance(entry, CTkOptionMenu):
                new_value = entry.get()
            elif isinstance(entry, CTkFrame): # Handle the frame containing ComboBox and Button
                new_value = entry.winfo_children()[0].get() # Get value from the CTkComboBox
            else:
                new_value = entry.get().strip()

            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx][0]} cannot be empty.")
                return

            # Validate numeric fields
            # Removed 'mat_volume' from numeric check
            numeric_cols = ['current_stock', 'min_stock_level', 'shelf_life_days']
            if col_name in numeric_cols:
                try:
                    int(new_value)
                except ValueError:
                    messagebox.showerror("Input Error", f"{fields[idx][0]} must be numeric.")
                    return

            try:
                conn = sqlite3.connect(resource_path("main.db"))
                c = conn.cursor()
                c.execute(f"UPDATE raw_mats SET {col_name} = ?, last_restocked = ? WHERE mat_id = ?", (new_value, timestamp, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx][0]} updated successfully!")
                self.load_mats_from_db()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))

        def update_material():
            material_id = entries[0].get().strip()
            material_name = entries[1].get().strip() if isinstance(entries[1], CTkEntry) else entries[1].get()
            material_description = entries[2].get()
            mat_volume = entries[3].winfo_children()[0].get() # Get from ComboBox inside the frame
            current_stock = values[4] # Keep original value, not from an entry
            unit_of_measure = entries[5].winfo_children()[0].get() # Get from ComboBox inside the frame
            min_stock_level = entries[6].get().strip()
            delivery_date = entries[7].get_date().strftime('%Y-%m-%d')
            supplier_id = entries[8].get().strip()
            last_restocked = entries[9].get().strip()
            shelf_life = entries[10].get_date().strftime('%Y-%m-%d') if isinstance(entries[10], DateEntry) else entries[10].get().strip()

            # Check if all required fields are filled
            required_values = [material_id, material_name, mat_volume, unit_of_measure, min_stock_level, delivery_date, supplier_id]
            if not all(required_values):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            # Validate numeric fields
            # Removed mat_volume from this check
            try:
                int(min_stock_level)
                int(shelf_life)
            except ValueError:
                messagebox.showerror("Input Error", "Current Stock, Min Stock, and Shelf Life must be numeric.")
                return

            try:
                conn = sqlite3.connect(resource_path("main.db"))
                c = conn.cursor()
                c.execute('''
                    UPDATE raw_mats
                    SET mat_name=?, mat_description=?, mat_volume=?, unit_of_measure=?, min_stock_level=?, mat_order_date=?, supplier_id=?, last_restocked=?, shelf_life_days=?
                    WHERE mat_id=?
                ''', (material_name, material_description, mat_volume, unit_of_measure, min_stock_level, delivery_date, supplier_id, last_restocked, shelf_life, material_id))
                conn.commit()
                messagebox.showinfo("Success", "Material updated successfully!")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                        (user_id, f"Updated Material ID: {material_id}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="update",
                    feature="inventory",
                    operation="update_material",
                    details=f"Updated material ID: {material_id}, Name: {material_name}, Description: {material_description}"
                )
                top.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("-atabase Error", str(e))
            finally:
                conn.close()
        
        # Add update buttons for editable fields
        db_cols = ['mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days']
        for i, (label, value, editable) in enumerate(fields):
            if editable: # No individual update button for dropdowns
                col_name = db_cols[i]
                btn = CTkButton(top, text="Update", width=70, command=lambda idx=i, col=col_name: update_field(idx, col))
                btn.grid(row=i, column=2, padx=5, pady=10)

        update_btn = CTkButton(top, text="Update", width=120, fg_color="#6a9bc3", command=update_material)
        update_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)


    def mats_history(self, event):

        selected = self.inventory_tree.focus()

        if not selected:
            messagebox.showwarning("No selection", "Please select a material to view history.")
            return
        
        values = self.inventory_tree.item(selected, 'values')
        mat_id = values[0]
        mat_splr = values[4]

        try:

            conn = sqlite3.connect(resource_path("main.db"))
            c = conn.cursor()

            mat_info = c.execute("""
                SELECT rm.mat_id, rm.mat_name, rm.mat_volume, s.supplier_id
                FROM raw_mats rm
                JOIN suppliers s ON rm.supplier_id = s.supplier_id
                WHERE rm.mat_id = ? AND s.supplier_id = ?
            """, (mat_id, mat_splr)).fetchall()



            if not mat_info:
                messagebox.showerror('Error', f"No Material found with ID: {mat_id} and Supplier ID: {mat_splr}")
                return
            else:
                print('Supplier Info:', mat_info)

                mat_desc += "\n".join(f"Material ID: {row[0]}, Material Name: {row[1]}, Current Volume: {row[2]}, Ordered From: {row[3]}" for row in mat_info)

                popup = tk.Toplevel(self)
                popup.title(f"Material History: {mat_id}")
                popup.geometry("600x400")

                txt = tk.Text(popup, wrap="word", state="normal")
                txt.insert('1.0', mat_desc)
                txt.config(state='disabled')
                txt.pack(expand=True, fill='both', padx=10, pady=10)

                request_material = ctk.CTkFrame(
                    popup,
                    fg_color="blue",   # use fg_color for visible background
                    corner_radius=10,
                    height=50          # force some height
                )
                request_material.pack(side='bottom', fill='x', padx=0, pady=(0, 10))

        except sqlite3.Error as e:
            messagebox.showerror('Database Error', str(e))
            return
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return
        finally:
            conn.close()

    def material_info(self, event):
        user_type = self.controller.session.get('usertype')
        user_email = self.controller.session.get('useremail')

        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a material to view details.")
            return

        values = self.inventory_tree.item(selected, 'values')
        if len(values) < 9:
            messagebox.showerror('Error', "Incomplete material data in the selected row.")
            return

        mat_id = values[0]
        mat_supplier = values[8]

        try:
            conn = sqlite3.connect(resource_path("main.db"))
            c = conn.cursor()
            mat_info = c.execute("""
                SELECT rm.mat_id, rm.mat_name, rm.mat_description, rm.mat_volume, rm.current_stock, rm.unit_of_measure,
                    rm.min_stock_level, rm.mat_order_date, s.supplier_id, s.supplier_name, s.supplier_num, s.supplier_mail
                FROM raw_mats rm
                JOIN suppliers s ON rm.supplier_id = s.supplier_id
                WHERE rm.mat_id = ?
            """, (mat_id,)).fetchall()

            if not mat_info:
                messagebox.showerror("Error", "Material not found in database.")
                return

            row = mat_info[0]
            try:
                material_volume = int(row[3])
            except (ValueError, TypeError):
                material_volume = 0

            try:
                min_stock_level = int(row[6])
            except (ValueError, TypeError):
                min_stock_level = 0

            material_count = material_volume > min_stock_level

            # Create enhanced material information window
            popup = tk.Toplevel(self)
            popup.title(f"Material Details - {row[1]}")
            popup.geometry("800x600")
            popup.configure(bg='white')
            popup.resizable(False, False)  # prevent resizing/maximizing
            popup.minsize(800, 600)
            popup.maxsize(800, 600)
            popup.grab_set()  # Make window modal to ensure it gets focus
            
            # Main container with proper padding (anchor to top)
            main_frame = tk.Frame(popup, bg='white')
            main_frame.pack(fill="x", padx=20, pady=20)
            
            # ===== MATERIAL INFORMATION SECTION =====
            # Material information frame (attach to main_frame so it stays at the top)
            material_frame = CTkFrame(main_frame, fg_color="#e6f2ff", corner_radius=10)
            material_frame.pack(fill="x", padx=0, pady=10)
            
            # Material details header
            header_label = CTkLabel(material_frame, text="MATERIAL INFORMATION", font=('Futura', 16, 'bold'), 
                                  text_color="#003366", fg_color="#e6f2ff")
            header_label.pack(pady=(10, 5), anchor="w", padx=20)
            
            # Material details in a grid layout
            details_frame = CTkFrame(material_frame, fg_color="#e6f2ff")
            details_frame.pack(fill="x", padx=20, pady=5)
            
            # Left column
            left_col = CTkFrame(details_frame, fg_color="#e6f2ff")
            left_col.pack(side="left", fill="x", expand=True)
            
            # Right column
            right_col = CTkFrame(details_frame, fg_color="#e6f2ff")
            right_col.pack(side="right", fill="x", expand=True)
            
            # Material details - left column
            material_left_data = [
                ("Material ID:", row[0]),
                ("Material Name:", row[1]),
                ("Description:", row[2]),
                ("Material Volume:", f"{material_volume:,}" if material_volume > 0 else "0")
            ]
            
            for label, value in material_left_data:
                item_frame = CTkFrame(left_col, fg_color="#e6f2ff")
                item_frame.pack(fill="x", pady=5)
                
                label_widget = CTkLabel(item_frame, text=label, font=('Futura', 12, 'bold'), 
                                      text_color="#003366", width=120, anchor="w")
                label_widget.pack(side="left")
                
                value_widget = CTkLabel(item_frame, text=str(value) if value else "N/A", 
                                      font=('Futura', 12), text_color="#333333")
                value_widget.pack(side="left", padx=10)
            
            # Material details - right column
            material_right_data = [
                ("Unit of Measure:", row[5] or "N/A"),
                ("Current Stock:", f"{row[4]:,}" if row[4] else "0"),
                ("Minimum Stock Level:", f"{min_stock_level:,}" if min_stock_level > 0 else "0"),
                ("Order Date:", row[7] or "N/A")
            ]
            
            for label, value in material_right_data:
                item_frame = CTkFrame(right_col, fg_color="#e6f2ff")
                item_frame.pack(fill="x", pady=5)
                
                label_widget = CTkLabel(item_frame, text=label, font=('Futura', 12, 'bold'), 
                                      text_color="#003366", width=150, anchor="w")
                label_widget.pack(side="left")
                
                value_widget = CTkLabel(item_frame, text=str(value) if value else "N/A", 
                                      font=('Futura', 12), text_color="#333333")
                value_widget.pack(side="left", padx=10)
            
            # ===== SUPPLIER INFORMATION SECTION =====
            # Supplier information frame (attach to main_frame)
            supplier_frame = CTkFrame(main_frame, fg_color="#e6f2ff", corner_radius=10)
            supplier_frame.pack(fill="x", padx=0, pady=10)
            
            # Supplier details header
            supplier_header = CTkLabel(supplier_frame, text="SUPPLIER INFORMATION", font=('Futura', 16, 'bold'), 
                                     text_color="#003366", fg_color="#e6f2ff")
            supplier_header.pack(pady=(10, 5), anchor="w", padx=20)
            
            # Supplier details in a grid layout
            supplier_details_frame = CTkFrame(supplier_frame, fg_color="#e6f2ff")
            supplier_details_frame.pack(fill="x", padx=20, pady=5)
            
            # Left column
            supplier_left_col = CTkFrame(supplier_details_frame, fg_color="#e6f2ff")
            supplier_left_col.pack(side="left", fill="x", expand=True)
            
            # Right column
            supplier_right_col = CTkFrame(supplier_details_frame, fg_color="#e6f2ff")
            supplier_right_col.pack(side="right", fill="x", expand=True)
            
            # Supplier details - left column
            supplier_left_data = [
                ("Supplier ID:", row[8]),
                ("Supplier Name:", row[9])
            ]
            
            for label, value in supplier_left_data:
                item_frame = CTkFrame(supplier_left_col, fg_color="#e6f2ff")
                item_frame.pack(fill="x", pady=5)
                
                label_widget = CTkLabel(item_frame, text=label, font=('Futura', 12, 'bold'), 
                                      text_color="#003366", width=120, anchor="w")
                label_widget.pack(side="left")
                
                value_widget = CTkLabel(item_frame, text=str(value) if value else "N/A", 
                                      font=('Futura', 12), text_color="#333333")
                value_widget.pack(side="left", padx=10)
            
            # Supplier details - right column
            supplier_right_data = [
                ("Contact Number:", row[10]),
                ("Email:", row[11])
            ]
            
            for label, value in supplier_right_data:
                item_frame = CTkFrame(supplier_right_col, fg_color="#e6f2ff")
                item_frame.pack(fill="x", pady=5)
                
                label_widget = CTkLabel(item_frame, text=label, font=('Futura', 12, 'bold'), 
                                      text_color="#003366", width=150, anchor="w")
                label_widget.pack(side="left")
                
                value_widget = CTkLabel(item_frame, text=str(value) if value else "N/A", 
                                      font=('Futura', 12), text_color="#333333")
                value_widget.pack(side="left", padx=10)
            
            # ===== ACTION BUTTONS SECTION =====
            # Action buttons at the bottom (attach to main_frame)
            button_frame = CTkFrame(main_frame, fg_color="white")
            button_frame.pack(fill="x", pady=(10, 0))
            
            # Add an entry for the order deadline
            deadline_frame = CTkFrame(main_frame, fg_color="white")
            deadline_frame.pack(fill="x", padx=20, pady=5)
            
            CTkLabel(deadline_frame, text="Required By (Order Deadline):", font=('Futura', 12, 'bold')).pack(side="left")
            
            deadline_entry = DateEntry(deadline_frame, width=12, background='darkblue', 
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            deadline_entry.pack(side="left", padx=10)
            # Set a default date (e.g., today)
            deadline_entry.set_date(datetime.now().date())

            def request_materials():
                try:
                    # Load Gmail credentials
                    creds = load_credentials_if_logged_in()
                    if not creds:
                        messagebox.showerror('Email Error', 'Please login with Google first to send email.')
                        return

                    supplier_email = row[11]
                    supplier_name = row[9] if row[9] else 'Supplier'
                    if not supplier_email:
                        messagebox.showerror('Error', 'Supplier email not found for this material.')
                        return

                    # Sender details
                    f_name = self.controller.session.get('f_name') or ''
                    l_name = self.controller.session.get('l_name') or ''
                    sender_role = user_type or ''
                    sender_email = user_email

                    # Get the deadline from the new DateEntry widget
                    required_by_date = deadline_entry.get_date().strftime('%Y-%m-%d')

                    # Compose email
                    email_subject = f"Purchase Request: {row[1]} (ID: {row[0]})"
                    email_body = (
                        f"Dear {supplier_name},\n\n"
                        f"We would like to request a purchase for the following material, which is currently below the minimum stock threshold:\n\n"
                        f"Material Details:\n"
                        f"  • ID: {row[0]}\n"
                        f"  • Name: {row[1]}\n"
                        f"  • Description: {row[2]}\n"
                        f"  • Unit: {row[5]}\n"
                        f"  • Current Stock: {row[4]:,} {row[5]}\n"
                        f"  • Minimum Stock Level: {min_stock_level:,} {row[5]}\n"
                        f"  • Last Order Date: {row[7] or 'N/A'}\n\n"
                        f"Kindly confirm availability, lead time, and pricing at your earliest convenience.\n\n"
                        f"This material is urgently required for an order due on: {required_by_date}\n\n"
                        f"Best regards,\n"
                        f"{f_name} {l_name} ({sender_role})\n"
                        f"{sender_email}\n"
                    )

                    # Send email to supplier
                    try:
                        email_sent = send_email_with_attachment(creds, supplier_email, email_subject, email_body, [], from_email=sender_email)
                        if email_sent:
                            messagebox.showinfo('Success', 'Email has been sent to the supplier.')
                        else:
                            messagebox.showerror('Failed', 'Email has not been sent.')
                    except Exception as e:
                        messagebox.showerror('Email Error', f'Failed to send email: {e}')
                except Exception as e:
                    messagebox.showerror('Error', str(e))

            # Show the request button for all users except 'staff'
            if user_type != 'staff':
                request_btn = CTkButton(
                    button_frame,
                    text='Request Material',
                    width=200,
                    height=45,
                    font=("Futura", 14, "bold"),
                    corner_radius=12,
                    fg_color="#e67e22",
                    hover_color="#d35400",
                    command=request_materials
                )
                request_btn.pack(side="left", padx=20, pady=15)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            conn.close()

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
        # Reload inventory data when the frame is shown
        self.load_mats_from_db() 

    def handle_logout(self):
        handle_logout(self)
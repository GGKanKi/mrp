import tkinter as tk
from tkcalendar import Calendar, DateEntry
from tkcalendar import DateEntry
from tkinter import font
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import uuid
import pandas as pd
import logging
import os

import sys
#Import Files
from pages_handler import FrameNames
from global_func import on_show, handle_logout, resource_path, restock_logs_to_sheets
from log_f.user_activity_logger import user_activity_logger

class SuppliersPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.update_window = None
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

            novus_logo = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
            novus_logo = novus_logo.resize((50, 50))
            self.novus_photo = CTkImage(novus_logo, size=(50, 50))

            logging.basicConfig(filename=resource_path(os.path.join('log_f', 'actions.log')), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            self.splr_act = logging.getLogger('splr_act')
            self.splr_act.setLevel(logging.INFO)

            self.splr_act_warning = logging.getLogger('splr_act_warning')
            self.splr_act_warning.setLevel(logging.WARNING)

            self.splr_act_error = logging.getLogger('splr_act_error')
            self.splr_act_error.setLevel(logging.ERROR)
            
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

            # Search and CRUD buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=150)

            self.srch_btn = self.add_del_upd('SEARCH','#5dade2', command=self.srch_splr)
            self.add_btn = self.add_del_upd('ADD', '#2ecc71', command=self.add_splr)
            self.del_btn = self.add_del_upd('DELETE', '#e74c3c', command=self.del_splr)
            self.update_btn = self.add_del_upd('UPDATE','#f39c12', command=self.upd_splr)
            self.restock_btn = self.add_del_upd('RESTOCK MATERIALS', '#3498db', command=self.open_restock_window)

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


            self.tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
            self.tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

            self.supplier_tree = ttk.Treeview(
                tree_frame,
                columns=('supplier_id', 'supplier_name', 'supplier_add', 'supplier_num', 'supplier_mail', 'contact_person', 'rating', 'is_active', 'delivered_date', 'date_created', 'last_updated'),
                show='headings',
                style='Custom.Treeview'
            )
            self.supplier_tree.bind("<Double-1>", self.splr_history)


            self._column_heads('supplier_id', 'SUPPLIER ID')
            self._column_heads('supplier_name', 'NAME')
            self._column_heads('supplier_add', 'ADDRESS')
            self._column_heads('supplier_num', 'CONTACT')
            self._column_heads('supplier_mail', 'EMAIL')
            self._column_heads('contact_person', 'CONTACT PERSON')
            self._column_heads('rating', 'RATING')
            self._column_heads('is_active', 'ACTIVITY STATUS')
            self._column_heads('delivered_date', 'LAST DELIVERY')
            self._column_heads('date_created', 'DATE CREATED')
            self._column_heads('last_updated', 'LAST UPDATED')
                        
            for col in ('supplier_id', 'supplier_name', 'supplier_add', 'supplier_num', 'supplier_mail', 'contact_person', 'rating', 'is_active', 'delivered_date', 'date_created', 'last_updated'):
                self.supplier_tree.column(col, width=300, stretch=False)
            
                # Scrollbars
                self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.supplier_tree.yview)
                self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.supplier_tree.xview)
                self.supplier_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

                # Use grid for proper layout
                self.supplier_tree.grid(row=0, column=0, sticky="nsew")
                self.scrollbar.grid(row=0, column=1, sticky="ns")
                self.h_scrollbar.grid(row=1, column=0, sticky="ew")

                # Make the treeview expandable
                tree_frame.grid_rowconfigure(0, weight=1)
                tree_frame.grid_columnconfigure(0, weight=1)

            # Add a small frame in the corner to avoid scrollbar overlap
            corner_grip = tk.Frame(tree_frame)
            corner_grip.grid(row=1, column=1, sticky="nsew")

            # Load initial data
            self.load_splr_from_db()

    def load_splr_from_db(self):
        try:

            conn = sqlite3.connect(resource_path("main.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE is_active = 1 ORDER BY supplier_id")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.supplier_tree.get_children():
                self.supplier_tree.delete(i)

            for row in rows:
                self.supplier_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def srch_splr(self):
        spler_id = self.search_entry.get().strip()
        user_id = self.controller.session.get('user_id')
        username = self.controller.session.get('username', 'Unknown')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            row = """
                SELECT * FROM suppliers
                WHERE (
                    supplier_id LIKE ?
                    OR supplier_name LIKE ?
                    OR supplier_add LIKE ?
                    OR supplier_num LIKE ?
                    OR supplier_mail LIKE ?
                    OR rating LIKE ?
                    OR delivered_date LIKE ?
                    OR date_created LIKE ?
                    OR last_updated LIKE ?
                    OR contact_person LIKE ?
                )
                AND is_active = 1
                ORDER BY supplier_id
            """
            params = (spler_id,) * 10
            row = c.execute(row, params).fetchall()

            for i in self.supplier_tree.get_children():
                self.supplier_tree.delete(i)

            if row:
                for i in row:
                    self.supplier_tree.insert("", "end", values=i)
                
                # Log successful search to user_activity.log
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Searched for supplier '{spler_id}'",
                    feature="supplier",
                    operation="search",
                    details=f"Found {len(row)} results"
                )
            else:
                messagebox.showinfo("Not Found", f"No supplier found with ID '{spler_id}'")
                self.load_splr_from_db()
                
                # Log unsuccessful search to user_activity.log
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Searched for supplier '{spler_id}'",
                    feature="supplier",
                    operation="search",
                    details="No results found"
                )
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
    
    def add_splr(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):

            messagebox.showwarning("Access Denied", "You do not have permission to add suppliers.")
            return

        try:
            if hasattr(self, 'splr_window') and self.splr_window.winfo_exists():
                self.splr_window.lift()
                print("Window already exists, bringing it to the front.")
                return
            
            self.splr_window = tk.Toplevel()
            self.splr_window.geometry('500x400')
            self.splr_window.title('Add Supplier')
            self.splr_window.config(bg='white')

            labels = ["Supplier Name:", "Supplier Address:", "Supplier Number:", "Supplier Email:", "Contact Person:", "Rating (1-5):"]
            self.splr_entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.splr_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                entry = CTkEntry(self.splr_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                self.splr_entries.append(entry)

                

            def save_field(idx):
                value = self.splr_entries[idx].get().strip()
                if not value:
                    messagebox.showerror("Input Error", f"{labels[idx][:-1]} cannot be empty.")
                    return
                if idx == 2:  # Supplier Number
                    try:
                        int(value)
                    except ValueError:
                        messagebox.showerror("Input Error", "Supplier Number must be numeric.")
                        return

                if idx == 5:  # Rating
                    try:
                        rating = int(value)
                        if rating < 1 or rating > 5:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Input Error", "Rating must be an integer between 1 and 5.")
                        return
                messagebox.showinfo("Saved", f"{labels[idx][:-1]} saved as '{value}'.")

            # Add a save button for each field
            for i in range(len(labels)):
                self.splr_entries[i].grid(row=i, column=1, padx=10, pady=10, sticky='w')
                btn = CTkButton(self.splr_window, text="Save", width=60, command=lambda idx=i: save_field(idx))
                btn.grid(row=i, column=2, padx=5, pady=10)

            def splr_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                
                supplier_id = f"SUP-{uuid.uuid4().hex[:8].upper()}"
                splr_data = [e.get().strip() for e in self.splr_entries]
                
                keys = ['supplier_name', 'supplier_add', 'supplier_num', 'supplier_mail', 'contact_person', 'rating']
                data_dict = dict(zip(keys, splr_data))

                for key, value in data_dict.items():
                    if not value:
                        messagebox.showerror("Input Error", f"{key.replace('_', ' ').title()} cannot be empty.")
                        return
                try:
                    int(data_dict['supplier_num'])
                except ValueError:
                    messagebox.showerror("Input Error", "Supplier Number must be numeric.")
                    return

                try:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO suppliers 
                        (supplier_id, supplier_name, supplier_add, supplier_num, supplier_mail, contact_person, rating, is_active, delivered_date, date_created, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                        (supplier_id,) + tuple(splr_data) + (1, None, timestamp, timestamp))
                    conn.commit()
                    messagebox.showinfo("Success", "Supplier registered successfully!")
                    # Log the action - ADD SUPPLIER to USER LOG
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)""", 
                              (user_id, f'ADD SUPPLIER {supplier_id}', timestamp))
                    conn.commit()
                    
                    # Log to user_activity.log
                    username = self.controller.session.get('username', 'Unknown')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action=f"Added supplier {supplier_id}",
                        feature="supplier",
                        operation="create",
                        details=f"Supplier name: {data_dict['supplier_name']}, Email: {data_dict['supplier_mail']}"
                    )
                    
                    self.splr_act.info(f"Added supplier {supplier_id}, Time: {timestamp}")
                    self.load_splr_from_db()
                    self.splr_window.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.splr_act_error.error(f"Error adding supplier '{supplier_id}', Time: {timestamp}: {e}")
                finally:
                    conn.close()

            submit_btn = CTkButton(self.splr_window, text='Submit All', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=splr_to_db)
            submit_btn.grid(row=len(labels), column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Supplier window: {e}")
            self.splr_act_error.error(f"Error while creating Add Supplier window: {e}")

    def del_splr(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):

            messagebox.showwarning("Access Denied", "You do not have permission to delete suppliers")
            return

        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.supplier_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a supplier to delete.")
            return

        try:
            values = self.supplier_tree.item(selected, 'values')
            suplier_id = values[0]  # Assuming client_id is the first column

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete supplier ID '{suplier_id}'?")
            if not confirm:
                return

            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT * FROM suppliers WHERE supplier_id =  ?", (suplier_id,))
            row = c.fetchone()

            if row:
                is_inactive_val = 0
                c.execute("UPDATE suppliers SET is_active = ? WHERE supplier_id =  ?", (is_inactive_val, suplier_id))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{suplier_id}' has been deleted.")
                c.execute("""INSERT INTO user_logs (user_id, action, timestamp)
                            VALUES (?, ?, ?)""", (user_id, f'DELETE SUPPLIER {suplier_id}', timestamp))
                conn.commit()
                
                # Log to user_activity.log
                username = self.controller.session.get('username', 'Unknown')
                supplier_name = row[1] if len(row) > 1 else 'Unknown'
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Deleted supplier {suplier_id}",
                    feature="supplier",
                    operation="delete",
                    details=f"Supplier name: {supplier_name}"
                )
                
                self.load_splr_from_db()
                self.splr_act.info(f"Deleted supplier {suplier_id}, Time: {timestamp}")
            else:
                messagebox.showinfo("Not Found", f"No material found with ID '{suplier_id}'")
                self.splr_act_warning.warning(f"Attempted to delete non-existent supplier {suplier_id}, Time: {timestamp}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.splr_act_error.error(f"Error deleting supplier {suplier_id}: {e}, Time: {timestamp}")

        finally:
            conn.close()


    def upd_splr(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):

            messagebox.showwarning("Access Denied", "You do not have permission to udpate supplier's information.")
            return
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.supplier_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return

        # If an update window is already open, bring it to the front
        if self.update_window and self.update_window.winfo_exists():
            self.update_window.lift()
            return

        values = self.supplier_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        self.update_window = top # Store reference
        top.title(f"Update Supplier - {original_id}")
        top.geometry("550x700")
        top.config(bg="white")
        top.resizable(False, False)

        fields = [
            'Supplier ID', 'Supplier Name', "Supplier Address", "Supplier Number", 'Supplier Mail',
            'Contact Person', 'Rating', 'Activity Status', 'Delivered Date', 'Date Created', 'Last Updated'
        ]
        col_names = [
            'supplier_id', 'supplier_name', 'supplier_add', 'supplier_num', 'supplier_mail',
            'contact_person', 'rating', 'is_active', 'delivered_date', 'date_created', 'last_updated'
        ]
        entries = []

        readonly_fields = ['Supplier ID', 'Date Created', 'Last Updated']

        for i, (label, value) in enumerate(zip(fields, values)):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            if label == "Delivered Date":
                # Calendar dropdown for delivered date
                entry = DateEntry(top, width=18, background='darkblue', foreground='white', borderwidth=2)
                try:
                    entry.set_date(value)
                except Exception:
                    pass
            else:
                entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.insert(0, value)
                if label in readonly_fields:
                    entry.configure(state='readonly')
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            entries.append(entry)

        def update_field(idx):
            new_value = entries[idx].get().strip() if fields[idx] != "Delivered Date" else entries[idx].get_date().strftime('%Y-%m-%d')
            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx]} cannot be empty.")
                return

            col = col_names[idx]
            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                if col in ['supplier_id', 'date_created', 'last_updated']:
                    messagebox.showinfo("Info", f"{fields[idx]} cannot be changed here.")
                    return
                if col == 'supplier_num':
                    try:
                        int(new_value)
                    except ValueError:
                        messagebox.showerror("Input Error", "Supplier Number must be numeric.")
                        return
                if col == 'rating':
                    try:
                        new_rating = int(new_value)
                        if new_rating < 1 or new_rating > 5:
                            messagebox.showerror("Input Error", 'Rating Range (1 to 5)')
                            return
                    except ValueError:
                        messagebox.showerror('Input Error', 'Rating Number must be numeric')
                        return
                if col == 'is_active':
                    if new_value not in ['0', '1']:
                        messagebox.showerror("Input Error", "Activity Status must be 0 (Inactive) or 1 (Active).")
                        return
                    new_value = int(new_value)

                c.execute(f"UPDATE suppliers SET {col} = ?, last_updated = ? WHERE supplier_id = ?", (new_value, timestamp, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx]} updated!")
                c.execute('''INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)''',
                        (user_id, f"UPDATED {col.replace('_', ' ').upper()} OF SUPPLIER {original_id} TO {new_value}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                username = self.controller.session.get('username', 'Unknown')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Updated supplier {original_id}",
                    feature="supplier",
                    operation="update",
                    details=f"Changed {col.replace('_', ' ')} to '{new_value}'"
                )
                
                self.load_splr_from_db()
                self.splr_act.info(f"Updated {fields[idx]} for supplier {original_id} to '{new_value}', Time: {timestamp}")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.splr_act_error.error(f"Error updating {fields[idx]}: {e}")
            finally:
                conn.close()

        # Add an update button for each editable field
        for i, label in enumerate(fields):
            if label not in readonly_fields:
                btn = CTkButton(top, text="Update", width=70, command=lambda idx=i: update_field(idx))
                btn.grid(row=i, column=2, padx=5, pady=10)

        def update_all():
            all_values = []
            for i, entry in enumerate(entries):
                if fields[i] == "Delivered Date":
                    all_values.append(entry.get_date().strftime('%Y-%m-%d'))
                else:
                    all_values.append(entry.get().strip())
            if not all(all_values):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute('''
                    UPDATE suppliers
                    SET supplier_name=?, supplier_add=?, supplier_num=?, supplier_mail=?, contact_person=?, rating=?, is_active=?, delivered_date=?, last_updated=?
                    WHERE supplier_id=?
                ''', (
                    all_values[1], all_values[2], all_values[3], all_values[4], all_values[5],
                    all_values[6], all_values[7], all_values[8], timestamp, original_id
                ))
                conn.commit()
                messagebox.showinfo("Success", "All fields updated!")
                c.execute('''INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)''',
                        (user_id, f"UPDATED ALL FIELDS OF SUPPLIER {original_id} TO {', '.join(all_values[1:])}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                username = self.controller.session.get('username', 'Unknown')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Updated all fields for supplier {original_id}",
                    feature="supplier",
                    operation="update",
                    details=f"New values: Name={all_values[1]}, Address={all_values[2]}, Number={all_values[3]}, Email={all_values[4]}, Contact={all_values[5]}"
                )
                
                self.load_splr_from_db()
                top.destroy()
                self.splr_act.info(f"Updated all fields for supplier {original_id} to '{', '.join(all_values[1:])}', Time: {timestamp}")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.splr_act_error.error(f"Error updating all fields: {e}")
            finally:
                conn.close()

        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)
        
    def open_restock_window(self):
        if hasattr(self, 'restock_window') and self.restock_window.winfo_exists():
            self.restock_window.lift()
            return

        self.restock_window = tk.Toplevel(self)
        self.restock_window.title("Restock Materials")
        self.restock_window.geometry("800x600")
        self.restock_window.configure(bg='white')
        self.restock_window.grab_set()

        # --- Data storage ---
        self.all_restock_materials = []
        self.restock_quantities = {} # {mat_id: (StringVar, original_stock)}

        # --- Top Frame for Controls ---
        top_frame = CTkFrame(self.restock_window, fg_color="transparent")
        top_frame.pack(pady=10, padx=10, fill='x')

        # Material Search
        CTkLabel(top_frame, text="Search Material:", font=('Futura', 13, 'bold')).pack(side='left', padx=(0, 5))
        self.restock_search_var = tk.StringVar()
        search_entry = CTkEntry(top_frame, textvariable=self.restock_search_var, width=200)
        search_entry.pack(side='left', padx=(0, 20))
        search_entry.bind('<KeyRelease>', self._filter_and_display_materials)

        # Supplier Dropdown
        CTkLabel(top_frame, text="Filter by Supplier:", font=('Futura', 13, 'bold')).pack(side='left', padx=(0, 5))
        self.restock_supplier_var = tk.StringVar(value="All")
        self.supplier_combo = ttk.Combobox(top_frame, textvariable=self.restock_supplier_var, width=30)
        self.supplier_combo.pack(side='left')
        self.supplier_combo.bind('<<ComboboxSelected>>', self._filter_and_display_materials)
        self._load_suppliers_for_restock()

        # --- Scrollable Frame for Materials ---
        canvas_frame = CTkFrame(self.restock_window, fg_color="lightgrey")
        canvas_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_material_frame = CTkFrame(canvas, fg_color="white")

        self.scrollable_material_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_material_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Bottom Frame for Action Button ---
        bottom_frame = CTkFrame(self.restock_window, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=10, fill='x')

        submit_btn = CTkButton(bottom_frame, text="Submit Restock", command=self._perform_restock, font=('Futura', 14, 'bold'), height=40)
        submit_btn.pack(side='left', padx=(0, 10), expand=True)

        export_btn = CTkButton(bottom_frame, text="Export History", command=restock_logs_to_sheets, font=('Futura', 14, 'bold'), height=40, fg_color="#16a085")
        export_btn.pack(side='left', padx=(10, 0), expand=True)

        self._load_restock_materials()
        self._filter_and_display_materials()

    def _load_suppliers_for_restock(self):
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("SELECT supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name")
            suppliers = [row[0] for row in c.fetchall()]
            self.supplier_combo['values'] = ["All"] + suppliers
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load suppliers: {e}", parent=self.restock_window)
        finally:
            if conn: conn.close()

    def _load_restock_materials(self):
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute("""
                SELECT rm.mat_id, rm.mat_name, rm.current_stock, s.supplier_name
                FROM raw_mats rm
                JOIN suppliers s ON rm.supplier_id = s.supplier_id
                WHERE rm.is_active = 1
                ORDER BY rm.mat_name
            """)
            self.all_restock_materials = c.fetchall()
            self.restock_quantities.clear()
            for mat_id, _, current_stock, _ in self.all_restock_materials:
                self.restock_quantities[mat_id] = (tk.StringVar(value="0"), current_stock)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load materials: {e}", parent=self.restock_window)
        finally:
            if conn: conn.close()

    def _filter_and_display_materials(self, event=None):
        for widget in self.scrollable_material_frame.winfo_children():
            widget.destroy()

        search_term = self.restock_search_var.get().lower()
        selected_supplier = self.restock_supplier_var.get()

        filtered_materials = self.all_restock_materials
        if selected_supplier != "All":
            filtered_materials = [m for m in filtered_materials if m[3] == selected_supplier]
        if search_term:
            filtered_materials = [m for m in filtered_materials if search_term in m[1].lower()]

        for i, (mat_id, mat_name, current_stock, supplier_name) in enumerate(filtered_materials):
            row_frame = CTkFrame(self.scrollable_material_frame, fg_color="#f0f0f0" if i % 2 == 0 else "white")
            row_frame.pack(fill='x', padx=5, pady=2)

            CTkLabel(row_frame, text=f"{mat_name} ({supplier_name})", width=300, anchor='w').pack(side='left', padx=10)
            CTkLabel(row_frame, text=f"Current: {current_stock}", width=100, anchor='w').pack(side='left', padx=10)

            qty_var, _ = self.restock_quantities[mat_id]
            
            def create_handler(m_id, v):
                return lambda: self._adjust_qty(m_id, v)

            CTkButton(row_frame, text="-", width=30, command=create_handler(mat_id, -1)).pack(side='left', padx=(20, 2))
            qty_entry = CTkEntry(row_frame, textvariable=qty_var, width=60, justify='center')
            qty_entry.pack(side='left')
            CTkButton(row_frame, text="+", width=30, command=create_handler(mat_id, 1)).pack(side='left', padx=2)

    def _adjust_qty(self, mat_id, delta):
        qty_var, _ = self.restock_quantities[mat_id]
        try:
            current_val = int(qty_var.get())
            new_val = max(0, current_val + delta)
            qty_var.set(str(new_val))
        except ValueError:
            qty_var.set("0")

    def _perform_restock(self):
        updates_to_perform = []
        restocked_materials_info = []
        for mat_id, (qty_var, original_stock) in self.restock_quantities.items():
            try:
                qty_to_add = int(qty_var.get())
                if qty_to_add > 0:
                    new_stock = int(original_stock) + qty_to_add
                    updates_to_perform.append((new_stock, mat_id, qty_to_add))
            except (ValueError, TypeError):
                continue

        # Find material details for logging/exporting
        for _, mat_id, qty_added in updates_to_perform:
            # Find the material details from the initially loaded list
            mat_info = next((m for m in self.all_restock_materials if m[0] == mat_id), None)
            if mat_info:
                restocked_materials_info.append({'Material ID': mat_id, 'Material Name': mat_info[1], 'Quantity Added': qty_added, 'Supplier': mat_info[3]})
                continue

        if not updates_to_perform:
            messagebox.showinfo("No Changes", "No quantities were specified for restock.", parent=self.restock_window)
            return

        if not messagebox.askyesno("Confirm Restock", f"Are you sure you want to restock {len(updates_to_perform)} material(s)?", parent=self.restock_window):
            return

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            user_id = self.controller.session.get('user_id')

            for new_stock, mat_id, qty_added in updates_to_perform:
                c.execute("UPDATE raw_mats SET current_stock = ?, last_restocked = ? WHERE mat_id = ?", (new_stock, timestamp, mat_id))
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f"Restocked Material ID: {mat_id} by {qty_added}", timestamp))
            
            conn.commit()
            messagebox.showinfo("Success", "Materials have been restocked successfully!", parent=self.restock_window)
            self.load_splr_from_db() # Refresh supplier page

            # Ask user if they want to export the restock that just happened
            if messagebox.askyesno("Export Restock", "Do you want to export a record of this restock?", parent=self.restock_window):
                restock_logs_to_sheets(restocked_materials_info)

            self.restock_window.destroy()
            self.controller.get_frame(FrameNames.INVENTORY).load_mats_from_db() # Refresh inventory page
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during restock: {e}", parent=self.restock_window)
        finally:
            if conn: conn.close() # Refresh inventory page

    def splr_history(self, event):
        """Display a detailed popup for the selected supplier, including their information and material supply history."""
        selected = self.supplier_tree.focus()
        if not selected:
            return
    
        values = self.supplier_tree.item(selected, 'values')
        if not values or not values[0]:
            return
    
        supplier_id = values[0]
        supplier_name = values[1]
    
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
    
            # Fetch materials supplied by this supplier
            supplied_materials = c.execute("""
                SELECT rm.mat_id, rm.mat_name, rm.mat_order_date
                FROM raw_mats rm
                WHERE rm.supplier_id = ?
            """, (supplier_id,)).fetchall()
    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return
        finally:
            if conn:
                conn.close()
    
        # --- UI Creation ---
        try:
            popup = tk.Toplevel(self)
            popup.title(f"Details for {supplier_name}")
            popup.geometry("900x600")
            popup.configure(bg='white')
            popup.resizable(False, False)
            popup.grab_set()
    
            # Supplier Info Frame
            supplier_frame = CTkFrame(popup, fg_color="#e6f2ff", corner_radius=10)
            supplier_frame.pack(fill="x", padx=20, pady=10)
    
            header_label = CTkLabel(supplier_frame, text="SUPPLIER INFORMATION", font=('Futura', 16, 'bold'), text_color="#003366")
            header_label.pack(pady=(10, 5), anchor="w", padx=20)
    
            details_frame = CTkFrame(supplier_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=5, expand=True)
            details_frame.grid_columnconfigure(1, weight=1)
            details_frame.grid_columnconfigure(3, weight=1)
    
            # Display Supplier Details from the selected treeview row
            CTkLabel(details_frame, text="Supplier ID:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=values[0], font=('Arial', 12)).grid(row=0, column=1, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text="Email:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=0, column=2, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=values[4], font=('Arial', 12)).grid(row=0, column=3, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text="Address:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=values[2], font=('Arial', 12)).grid(row=1, column=1, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text="Contact:", font=('Arial', 12, 'bold'), text_color="#003366").grid(row=1, column=2, sticky='w', padx=5, pady=2)
            CTkLabel(details_frame, text=values[3], font=('Arial', 12)).grid(row=1, column=3, sticky='w', padx=5, pady=2)
    
            # Material Supply History Section
            history_header = CTkLabel(popup, text="MATERIAL SUPPLY HISTORY", font=('Futura', 16, 'bold'), text_color="#003366")
            history_header.pack(pady=(20, 10))
    
            history_container = CTkFrame(popup, fg_color="white", corner_radius=10)
            history_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
            if not supplied_materials:
                CTkLabel(history_container, text="No material supply history found for this supplier.", font=('Arial', 14), text_color="#666666").pack(pady=50)
            else:
                style = ttk.Style()
                style.configure("Popup.Treeview", background="white", foreground="black", rowheight=28, fieldbackground="white", font=('Arial', 11))
                # Add horizontal lines
                style.layout("Popup.Treeview", [('item', {'sticky': 'nswe'})])
                style.configure("Popup.Treeview", separator=True)
                style.configure("Popup.Treeview.Heading", background="#e6f2ff", foreground="#003366", font=('Futura', 12, 'bold'), relief="flat")
                style.map("Popup.Treeview", background=[('selected', '#b5d9ff')])
    
                history_tree = ttk.Treeview(
                    history_container,
                    columns=('mat_id', 'mat_name', 'order_date'),
                    show='headings',
                    style="Popup.Treeview"
                )
                history_tree['show'] = 'headings' # Ensure only headings are shown, lines will do the rest
                history_tree.pack(fill='both', expand=True, padx=10, pady=10)
    
                # Define columns
                history_tree.heading('mat_id', text='Material ID')
                history_tree.heading('mat_name', text='Material Name')
                history_tree.heading('order_date', text='Order Date')
    
                # Set column widths
                history_tree.column('mat_id', width=200, anchor='w')
                history_tree.column('mat_name', width=300, anchor='w')
                history_tree.column('order_date', width=200, anchor='center')
    
                # Populate with data
                for material in supplied_materials:
                    history_tree.insert('', 'end', values=material)
    
            popup.after(100, popup.lift) # Ensure it's on top
    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))



    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
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

    def add_del_upd(self, text, fg_color, command=None):
        button = CTkButton(self, text=text, width=90, fg_color=fg_color, command=command, font=('Futura', 13, 'bold'))
        button.pack(side="left", anchor="n", padx=4)
        
    def _column_heads(self, columns, text):
        self.supplier_tree.heading(columns, text=text)
        self.supplier_tree.column(columns, width=195)

    def _add_mat(self, label_text, y):
        label = CTkLabel(self.splr_window, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.splr_window, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    
    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self)
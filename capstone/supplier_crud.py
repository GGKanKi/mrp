import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
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
import bcrypt
import pandas as pd
import logging
import os
import sys
sys.path.append("D:/capstone")


#Import Files
from pages_handler import FrameNames
from global_func import on_show, handle_logout

class SuppliersPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

            novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
            novus_logo = novus_logo.resize((50, 50))
            self.novus_photo = CTkImage(novus_logo, size=(50, 50))

            logging.basicConfig(filename='D:/capstone/log_f/actions.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            self.splr_act = logging.getLogger('splr_act')
            self.splr_act.setLevel(logging.INFO)

            self.splr_act_warning = logging.getLogger('splr_act_warning')
            self.splr_act_warning.setLevel(logging.WARNING)

            self.splr_act_error = logging.getLogger('splr_act_error')
            self.splr_act_error.setLevel(logging.ERROR)
            
            #Buttons Images
            self.clients_btn = self._images_buttons('D:/capstone/labels/client_btn.png', size=(100,100))
            self.inv_btn = self._images_buttons('D:/capstone/labels/inventory.png', size=(100,100))
            self.order_btn = self._images_buttons('D:/capstone/labels/order.png', size=(100,100))
            self.supply_btn = self._images_buttons('D:/capstone/labels/supply.png', size=(100,100))
            self.logout_btn = self._images_buttons('D:/capstone/labels/logout.png', size=(100,100))
            self.mrp_btn = self._images_buttons('D:/capstone/labels/mrp_btn.png', size=(100,100))
            self.settings_btn = self._images_buttons('D:/capstone/labels/settings.png', size=(100,100))
            self.user_logs_btn = self._images_buttons('D:/capstone/labels/action.png', size=(100,100))
            self.mails_btn = self._images_buttons('D:/capstone/labels/mail.png', size=(100,100))

            # Search and CRUD buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=150)

            self.srch_btn = self.add_del_upd('SEARCH', command=self.srch_splr)
            self.add_btn = self.add_del_upd('ADD', command=self.add_splr)
            self.del_btn = self.add_del_upd('DELETE', command=self.del_splr)
            self.update_btn = self.add_del_upd('UPDATE', command=self.upd_splr)


            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=120, y=105, width=1100, height=475)


            self.tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
            self.tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

            self.supplier_tree = ttk.Treeview(
                tree_frame,
                columns=('supplier_id', 'supplier_add', 'supplier_num', 'supplier_mail', 'delivered_date'),
                show='headings',
                style='Treeview'
            )

            self._column_heads('supplier_id', 'SUPPLIER ID')
            self._column_heads('supplier_add', 'ADDRESS')
            self._column_heads('supplier_num', 'CONTACT')
            self._column_heads('supplier_mail', 'EMAIL')
            self._column_heads('delivered_date', 'LAST DELIVERY')
                        
            for col in ('supplier_id', 'supplier_add', 'supplier_num', 'supplier_mail', 'delivered_date'):
                self.supplier_tree.column(col, width=300, stretch=False)
            
                # Scrollbars
                self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.supplier_tree.yview)
                self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.supplier_tree.xview)
                self.supplier_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

                # Use grid for proper layout
                self.supplier_tree.grid(row=0, column=0, sticky="nsew")
                self.scrollbar.grid(row=0, column=1, sticky="w")
                self.h_scrollbar.grid(row=1, column=0, sticky="ew")

                # Make the treeview expandable
                tree_frame.grid_rowconfigure(0, weight=1)
                tree_frame.grid_columnconfigure(0, weight=1)

            # Load initial data
            self.load_splr_from_db()

    def load_splr_from_db(self):
        try:

            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers")
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

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM suppliers WHERE supplier_id = ?", (spler_id,))
            row = c.fetchone()

            for i in self.supplier_tree.get_children():
                self.supplier_tree.delete(i)

            if row:
                self.supplier_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Not Found", f"No supplier found with ID '{spler_id}'")
                self.load_splr_from_db()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
    
    def add_splr(self):
        try:
            if hasattr(self, 'splr_window') and self.splr_window.winfo_exists():
                self.splr_window.lift()
                print("Window already exists, bringing it to the front.")
                return

            print("Creating Add Supplier Window...")
            self.splr_window = tk.Toplevel()
            self.splr_window.geometry('500x400')
            self.splr_window.title('Add Supplier')
            self.splr_window.config(bg='white')

            labels = ["Supplier ID:", "Supplier Address:", "Supplier Number:", "Supplier Email:"]
            self.splr_entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.splr_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                entry = CTkEntry(self.splr_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
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
                messagebox.showinfo("Saved", f"{labels[idx][:-1]} saved as '{value}'.")

            # Add a save button for each field
            for i in range(len(labels)):
                btn = CTkButton(self.splr_window, text="Save", width=60, command=lambda idx=i: save_field(idx))
                btn.grid(row=i, column=2, padx=5, pady=10)

            def splr_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                splr_data = [e.get().strip() for e in self.splr_entries]
                keys = ['supplier_id', 'supplier_add', 'supplier_num', 'supplier_mail']
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
                    conn = sqlite3.connect('main.db')
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO suppliers (supplier_id, supplier_add, supplier_num, supplier_mail)
                        VALUES (?, ?, ?, ?)
                    """, tuple(splr_data))
                    conn.commit()
                    messagebox.showinfo("Success", "Supplier registered successfully!")
                    # Log the action - ADD SUPPLIER to USER LOG
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp)
                                VALUES (?, ?, ?)""", (user_id, f'ADD SUPPLIER {data_dict['supplier_id']}', timestamp))
                    conn.commit()
                    self.splr_act.info(f"Added supplier {data_dict['supplier_ide']}, Time: {timestamp}")
                    self.load_splr_from_db()
                    self.splr_window.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.splr_act_error.error(f"Error adding supplier '{data_dict['supplier_id']}, Time: {timestamp}: {e}")
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

            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM suppliers WHERE supplier_id =  ?", (suplier_id,))
            row = c.fetchone()

            if row:
                c.execute("DELETE FROM suppliers WHERE supplier_id =  ?", (suplier_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{suplier_id}' has been deleted.")
                c.execute("""INSERT INTO user_logs (user_id, action, timestamp)
                            VALUES (?, ?, ?)""", (user_id, f'DELETE SUPPLIER {suplier_id}', timestamp))
                conn.commit()
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
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.supplier_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return

        values = self.supplier_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        top.title("Update Supplier")
        top.geometry("500x400")
        top.config(bg="white")

        fields = ['Supplier ID', "Supplier Address", "Supplier Number", 'Supplier Mail', 'Delivered Date']
        entries = []

        # Read-only for Supplier ID and Delivered Date
        readonly_fields = ['Supplier ID', 'Delivered Date']

        for i, (label, value) in enumerate(zip(fields, values)):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            if label in readonly_fields:
                entry.configure(state='readonly')
            entries.append(entry)

        def update_field(idx):
            new_value = entries[idx].get().strip()
            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx]} cannot be empty.")
                return

            col_names = ['supplier_id', 'supplier_add', 'supplier_num', 'supplier_mail', 'delivered_date']
            col = col_names[idx]

            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                if col in ['supplier_id', 'delivered_date']:
                    messagebox.showinfo("Info", f"{fields[idx]} cannot be changed here.")
                    return
                c.execute(f"UPDATE suppliers SET {col} = ? WHERE supplier_id = ?", (new_value, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx]} updated!")
                c.execute(''' INSERT INTO user_logs (user_id, action, timestamp) VALUES (?,?,?) ''',
                        (user_id, f"UPDATED {col.replace('_', ' ').upper()} OF CLIENT {original_id} TO {new_value}", timestamp))
                conn
                self.load_splr_from_db()
                self.splr_act.info(f"Updated {fields[idx]} for supplier {original_id} to '{new_value}, Time: {timestamp}'")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.splr_act_error.error(f"Error updating {fields[idx]}: {e}")
            finally:
                conn.close()

        # Add an update button for each editable field
        for i in range(1, len(fields)-1):  # skip Supplier ID and Delivered Date
            btn = CTkButton(top, text="Update", width=70, command=lambda idx=i: update_field(idx))
            btn.grid(row=i, column=2, padx=5, pady=10)

        def update_all():
            all_values = [entry.get().strip() for entry in entries]
            if not all(all_values):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute('''
                    UPDATE suppliers
                    SET supplier_add=?, supplier_num=?, supplier_mail=?
                    WHERE supplier_id=?
                ''', (all_values[1], all_values[2], all_values[3], original_id))
                conn.commit()
                messagebox.showinfo("Success", "All fields updated!")
                c.execute(''' INSERT INTO user_logs (user_id, action, timestamp) VALUES (?,?,?) ''',
                        (user_id, f"UPDATED ALL FIELDS OF CLIENT {original_id} TO {', '.join(all_values[1:])}", timestamp))
                conn.commit()
                self.load_splr_from_db()
                top.destroy()
                self.splr_act.info(f"Updated all fields for supplier {original_id} to '{', '.join(all_values[1:])}, Time: {timestamp}'")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.splr_act_error.error(f"Error updating all fields: {e}")
            finally:
                conn.close()

        # "Update All" button at the bottom
        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)
        
    def splr_to_mat(self):
        search_del = self.search_entry.get().strip().lower()

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute('SELECT * FROM raw_mats WHERE mat_id = ?''', (search_del,))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.load_splr_from_db()
        finally:
            conn.close() 

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def add_del_upd(self, text, command):
        button = CTkButton(self, text=text, width=80, command=command)
        button.pack(side="left", anchor="n", padx=5)
        
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
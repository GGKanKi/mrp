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


#Data Imports
import pandas as pd
import json
import os
import sys
sys.path.append("D:/capstone")

#File imports
from product import ProductManagementSystem
from pages_handler import FrameNames
from global_func import on_show, handle_logout


class OrdersPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))  # Sticks to the left, fills Y
            parent.pack_propagate(False)

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))  # Sticks to the top, fills X

            novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
            novus_logo = novus_logo.resize((50, 50))
            self.novus_photo = CTkImage(novus_logo, size=(50, 50))

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



            #Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left",anchor="n", padx=(15, 20), ipadx=100)

            # Add Approve, Cancel for Status
            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2',command=self.srch_order)
            self.add_btn = self.add_del_upd('ADD ORDER', '#2ecc71', command=self.add_orders)
            self.approve_order_btn = self.add_del_upd('APPROVE ORDER', '#27ae60',command=self.approve_order)
            self.cancel_order_btn = self.add_del_upd('CANCEL ORDER', '#95a5a6', command=self.cancel_order)
            self.del_btn = self.add_del_upd('DELETE ORDER', '#e74c3c', command=self.del_order)
            self.excel_btn = self.add_del_upd('UPDATE ORDER', '#f39c12', command=self.upd_order)

            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=120, y=105, width=1100, height=475)

            self.order_tree = ttk.Treeview(        
            tree_frame,
                columns=('order_id', 'order_name', 'product_id', 'order_date', 
                        'order_dl', 'order_amount', 'client_id', 'status_quo'),
                show='headings',
                style='Treeview'
            )
            self.order_tree.bind("<Double-1>", self.show_materials_popup)


            # Configure column headings (assuming _column_heads does this)
            self._column_heads('order_id', 'ORDER ID')
            self._column_heads('order_name', 'ORDER NAME')
            self._column_heads('product_id', 'PRODUCT')
            self._column_heads('order_date', 'ORDER DATE')
            self._column_heads('order_dl', 'DEADLINE')
            self._column_heads('order_amount', 'VOLUME')
            self._column_heads('client_id', 'CLIENT ID')
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
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Configure weight for proper resizing
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            self.load_orders_from_db()

    def srch_order(self):
        search_order = self.search_entry.get().strip().lower()

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM orders WHERE order_id = ?", (search_order,))
            row = c.fetchone()

            for i in self.order_tree.get_children():
                self.order_tree.delete(i)

            if row:
                self.order_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Not Found", f"No client found with ID '{search_order}'")
                self.load_orders_from_db()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.load_orders_from_db()
        finally:
            conn.close()

    def add_orders(self):
        # Open the SimpleInventory top-level window
        # You can prevent multiple windows by keeping a reference if you want
        self.inventory_window = ProductManagementSystem(self, self.controller)

    #Checking the product status before verifying the order
    def approve_order(self):
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an order to approve.")
            return
        
        values = self.order_tree.item(selected, 'values')
        order_id = values[0]


        conn = sqlite3.connect('main.db')
        c = conn.cursor()

        try:
            c.execute("""
                        SELECT o.order_id, o.status_quo, p.product_id, p.status_quo
                        FROM orders o
                        JOIN products p ON o.product_id = p.product_id where o.order_id = ?
                        """, (order_id,))


            row = c.fetchone()

            if not row:
                messagebox.showinfo("Not Found", f"No orders found with ID '{order_id}'")
                return
            else:
                join_order_id = order_id
                order_stat = row[1]
                product_id = row[2]
                product_stat = row[3]

                if order_stat == 'Pending':
                    if product_stat == 'Approved':
                        new_status = 'Approved'
                        c.execute('UPDATE orders SET status_quo = ? where order_id = ?', (new_status, join_order_id))
                    elif product_stat == 'Pending' or product_stat == 'Cancelled':
                        messagebox.showwarning("Pending Product", f"Product ID '{product_id}' is not approved yet.")
                        return
                elif order_stat == 'Approved':
                    messagebox.showinfo("Already Approved", f"Order ID '{join_order_id}' is already approved.")
                    return
                elif order_stat == 'Cancelled':
                    messagebox.askyesno("Cancelled Order", f"Order ID '{join_order_id}' has been cancelled. Do you want to approve it again?")
                    new_status = 'Approved'
                    c.execute('UPDATE orders SET status_quo = ? where order_id = ?', (new_status, join_order_id))
                else:
                    return

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    
        conn.commit()
        conn.close()
        
        self.load_orders_from_db()


    def cancel_order(self):
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an order to approve.")
            return
        
        values = self.order_tree.item(selected, 'values')
        order_id = values[0]
        order_stat = values[7]

        status = 'Cancelled'

        conn = sqlite3.connect('main.db')
        c = conn.cursor()

        c.execute("UPDATE orders SET status_quo = ? WHERE order_id = ?", (status, order_id))
        messagebox.showinfo("Success", f"Order ID '{order_id}' has been cancelled.")

        conn.commit()
        conn.close()
        self.load_orders_from_db()

    def del_order(self):
        #Hard Deletion
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a order to delete.")
            return

        try:
            values = self.order_tree.item(selected, 'values')
            order_id = values[0]  # Assuming client_id is the first column

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete order ID '{order_id}'?")
            if not confirm:
                return

            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM orders WHERE order_id =  ?", (order_id,))
            row = c.fetchone()

            if row:
                c.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{order_id}' has been deleted.")
                self.load_orders_from_db()
            else:
                messagebox.showinfo("Not Found", f"No Orders found with ID '{order_id}'")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            conn.close()

    def upd_order(self):
        selected = self.order_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return

        values = self.order_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        top.title("Update Order")
        top.geometry("500x500")
        top.config(bg="white")

        fields = ['Order ID', "Order Name", 'Product', "Order Date", 'Deadline', "Order Volume", "Client ID"]
        db_cols = ['order_id', 'order_name', 'product_id', 'order_date', 'order_dl', 'order_amount', 'client_id']
        entries = []

        read_only_fields = ['Order ID', 'Order Date', 'Product', 'Client ID']

        for i, (label, value) in enumerate(zip(fields, values)):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            if label in read_only_fields:
                entry.configure(state='readonly')
            entries.append(entry)

        def update_field(idx):
            new_value = entries[idx].get().strip()
            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx]} cannot be empty.")
                return

            col = db_cols[idx]
            if fields[idx] in read_only_fields:
                messagebox.showinfo("Info", f"{fields[idx]} cannot be changed here.")
                return

            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute(f"UPDATE orders SET {col} = ? WHERE order_id = ?", (new_value, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx]} updated!")
                self.load_orders_from_db()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        # Add an update button for each editable field
        for i, label in enumerate(fields):
            if label not in read_only_fields:
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
                    UPDATE orders
                    SET order_name=?, order_dl=?, order_amount=?, mats_used=?
                    WHERE order_id=?
                ''', (all_values[1], all_values[4], all_values[5], all_values[6], original_id))
                conn.commit()
                messagebox.showinfo("Success", "All editable fields updated!")
                self.load_orders_from_db()
                top.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        # "Update All" button at the bottom
        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)

    def load_orders_from_db(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.order_tree.get_children():
                self.order_tree.delete(i)

            for row in rows:
                self.order_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def show_materials_popup(self, event):
        selected = self.order_tree.focus()
        if not selected:
            return
        values = self.order_tree.item(selected, 'values')
        mats_used = values[6]  # Assuming 'mats_used' is the 7th column
        popup = tk.Toplevel(self)
        popup.title("Materials Used")
        popup.geometry("400x300")
        txt = tk.Text(popup, wrap="word", state="normal")
        txt.insert("1.0", mats_used)
        txt.configure(state="disabled")
        txt.pack(expand=True, fill="both", padx=10, pady=10)

    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, fg_color=fg_color, width=80, command=command)
        button.pack(side="left", anchor="n", padx=5)

    def _column_heads(self, columns, text):
        self.order_tree.heading(columns, text=text)
        self.order_tree.column(columns, width=175)
        if text == 'MATERIALS':
            self.order_tree.column(columns, width=100)

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)

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

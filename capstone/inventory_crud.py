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
import os

#Imported Files
from pages_handler import FrameNames

from global_func import on_show, handle_logout

class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
            parent.pack_propagate(False)


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
      

            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left",anchor="n", padx=(15, 20), ipadx=150)

            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.srch_mats)
            self.add_btn = self.add_del_upd('ADD MATERIAL', '#2ecc71', command=self.add_mats)
            self.del_btn = self.add_del_upd('DELETE MATERIAL', '#e74c3c', command=self.del_mats)
            self.update_btn = self.add_del_upd('UPDATE MATERIAL', '#f39c12', command=self.upd_mats)
            self.check_orders = self.add_del_upd('CHECK MATERIAL', '#95a5a6', command=self.order_to_supplier)

            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=120, y=105, width=1100, height=475)

            self.inventory_tree = ttk.Treeview(        
            tree_frame, columns=('mat_id', 'mat_name', 'mat_volume', 'mat_order_date', 'supplier_id'), show='headings', style='Treeview')
            self.inventory_tree.bind("<Double-1>", self.mats_history)
            self._column_heads('mat_id', 'MATERIAL ID')
            self._column_heads('mat_name', 'MATERIAL NAME')
            self._column_heads('mat_volume', 'MATERIAL VOLUME')
            self._column_heads('mat_order_date', 'DELIVERY DATE')
            self._column_heads('supplier_id', 'SUPPLIER ID')
                
            for col in ('mat_id', 'mat_name', 'mat_volume', 'mat_order_date', 'supplier_id'):
                self.inventory_tree.column(col, width=400, stretch=False)

            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.inventory_tree.xview)
            self.inventory_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.inventory_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            self.load_mats_from_db()

    def _column_heads(self, columns, text):
        self.inventory_tree.heading(columns, text=text)
        self.inventory_tree.column(columns, width=195)

    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, width=73, fg_color=fg_color, command=command)
        button.pack(side="left", anchor="n", padx=4)

    def _add_mat(self, label_text, y):
        label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.mat_window, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    
    def load_mats_from_db(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_mats")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.inventory_tree.get_children():
                self.inventory_tree.delete(i)

            for row in rows:
                self.inventory_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def add_mats(self):
        try:
            if hasattr(self, 'mat_window') and self.mat_window.winfo_exists():
                self.mat_window.lift()
                return

            self.mat_window = tk.Toplevel()
            self.mat_window.geometry('500x400')
            self.mat_window.title('Add Material')
            self.mat_window.config(bg='white')

            labels = ["Material ID:", "Material Name:", "Material Volume:"]
            self.mat_entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                entry = CTkEntry(self.mat_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.mat_entries.append(entry)

            # Supplier dropdown
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute('SELECT supplier_id FROM suppliers')
            suppliers = [row[0] for row in c.fetchall()]
            conn.close()
            self.suppliers_ids = tk.StringVar()
            self.suppliers_ids.set(suppliers[0] if suppliers else "")
            CTkLabel(self.mat_window, text='Supplier ID:', font=('Futura', 13, 'bold')).grid(row=3, column=0, padx=15, pady=10, sticky='e')
            supplier_id_drop = tk.OptionMenu(self.mat_window, self.suppliers_ids, suppliers[0] if suppliers else "", *suppliers)
            supplier_id_drop.grid(row=3, column=1, padx=10, pady=10, sticky='w')

            def save_field(idx):
                value = self.mat_entries[idx].get().strip()
                if not value:
                    messagebox.showerror("Input Error", f"{labels[idx][:-1]} cannot be empty.")
                    return
                if idx == 2:  # Material Volume
                    try:
                        int(value)
                    except ValueError:
                        messagebox.showerror("Input Error", "Material Volume must be numeric.")
                        return
                messagebox.showinfo("Saved", f"{labels[idx][:-1]} saved as '{value}'.")

            # Save button for each field
            for i in range(len(labels)):
                btn = CTkButton(self.mat_window, text="Save", width=60, command=lambda idx=i: save_field(idx))
                btn.grid(row=i, column=2, padx=5, pady=10)

            def mat_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                mat_data = [e.get().strip() for e in self.mat_entries]
                supplier_id = self.suppliers_ids.get().strip()
                # Manila Timezone Setup
                manila_tz = pytz.timezone('Asia/Manila')
                manila_time = datetime.now(manila_tz).strftime('%Y-%m-%d %H:%M:%S')
                mat_data.append(manila_time)
                mat_data.append(supplier_id)

                if not all(mat_data[:3]) or not supplier_id:
                    messagebox.showerror("Input Error", "All fields are required.")
                    return
                try:
                    int(mat_data[2])
                except ValueError:
                    messagebox.showerror("Input Error", "Material Volume must be numeric.")
                    return

                try:
                    conn = sqlite3.connect('main.db')
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO raw_mats (mat_id, mat_name, mat_volume, mat_order_date, supplier_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, tuple(mat_data))
                    conn.commit()
                    messagebox.showinfo("Success", "Material registered successfully!")
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?,?,?)""",
                                (user_id, f"Added Material ID: {mat_data[0]}", timestamp))
                    conn.commit()
                    self.load_mats_from_db()
                    self.mat_window.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

            submit_btn = CTkButton(self.mat_window, text='Submit All', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=mat_to_db)
            submit_btn.grid(row=4, column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Materials window: {e}")
    
    def srch_mats(self):
        search_client = self.search_entry.get().strip().lower()

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM raw_mats WHERE mat_id = ?", (search_client,))
            row = c.fetchone()

            for i in self.inventory_tree.get_children():
                self.inventory_tree.delete(i)

            if row:
                self.inventory_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Not Found", f"No client found with ID '{search_client}'")
                self.load_mats_from_db()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def del_mats(self):
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

            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM raw_mats WHERE mat_id =  ?", (mat_id,))
            row = c.fetchone()

            if row:
                c.execute("DELETE FROM raw_mats WHERE mat_id = ?", (mat_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{mat_id}' has been deleted.")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f"Deleted Material ID: {mat_id}", timestamp))
            else:
                messagebox.showinfo("Not Found", f"No material found with ID '{mat_id}'")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            conn.close()

    def upd_mats(self):
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return

        values = self.inventory_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        top.title("Update Material")
        top.geometry("500x400")
        top.config(bg="white")

        fields = ['Material ID', "Material Name", "Material Volume", "Material Delivery Date", "Supplier ID"]
        db_cols = ['mat_id', 'mat_name', 'mat_volume', 'mat_order_date', 'supplier_id']
        entries = []

        read_only_fields = ['Material ID', 'Material Delivery Date', 'Supplier ID']

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
                c.execute(f"UPDATE raw_mats SET {col} = ? WHERE mat_id = ?", (new_value, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx]} updated!")
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f"Updated {fields[idx]} for Material ID: {original_id} to '{new_value}'", timestamp))
                conn.commit()
                self.load_mats_from_db()
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
                    UPDATE raw_mats
                    SET mat_name=?, mat_volume=?
                    WHERE mat_id=?
                ''', (all_values[1], all_values[2], original_id))
                conn.commit()
                messagebox.showinfo("Success", "All editable fields updated!")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                        (user_id, f"UPDATED ALL FIELDS OF CLIENT {original_id} TO {', '.join(all_values[1:])}", timestamp))
                conn.commit()
                top.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        # "Update All" button at the bottom
        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)

    def order_to_supplier(self):
        self.order_id = self.search_entry.get().strip().lower()

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute('SELECT * FROM suppliers WHERE order_id = ?')
            row = c.fetchone()

            for i in self.inventory_tree.get_children():
                self.inventory_tree.delete(i)


            if row:
                self.inventory_tree.insert("", 'end', values = row)
            else:
                messagebox.showinfo('Not Found', f"No Order ID found with ID '{self.order_id}'")
                self.load_mats_from_db()

        except sqlite3.Error as e:
            messagebox.showerror('Wrong Supplier')
            self.load_mats_from_db()

    def mats_history(self, event):

        selected = self.inventory_tree.focus()

        if not selected:
            messagebox.showwarning("No selection", "Please select a material to view history.")
            return
        
        values = self.inventory_tree.item(selected, 'values')
        mat_id = values[0]
        mat_splr = values[4]

        try:

            conn = sqlite3.connect('main.db')
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

        except sqlite3.Error as e:
            messagebox.showerror('Database Error', str(e))
            return
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return
        finally:
            conn.close()

            


    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self) 

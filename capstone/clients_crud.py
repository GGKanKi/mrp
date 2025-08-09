import tkinter as tk
import pytz
import time
from datetime import datetime
from tkinter import ttk, messagebox
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import os
import logging
import sys
sys.path.append("D:/capstone")

from pages_handler import FrameNames
from global_func import on_show, handle_logout


class ClientsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0)) 

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
        parent.pack_propagate(False)

        #Logger Files
        logging.basicConfig(filename='D:/capstone/log_f/actions.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.client_act = logging.getLogger('CLIENT_ACT')
        self.client_act.setLevel(logging.INFO)

        self.client_act_warning = logging.getLogger('CLIENT_ACT_WARNING')
        self.client_act_warning.setLevel(logging.WARNING)

        self.client_act_error = logging.getLogger('CLIENT_ACT_ERROR')
        self.client_act_error.setLevel(logging.ERROR)

        novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        # Buttons Images
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

        self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.srch_clients)
        self.add_btn = self.add_del_upd('ADD CLIENT', '#2ecc71', command=self.add_clients)
        self.del_btn = self.add_del_upd('DELETE CLIENT', '#e74c3c', command=self.del_clients)
        self.update_btn = self.add_del_upd('UPDATE CLIENT', '#f39c12', command=self.upd_clients)
        self.check_orders = self.add_del_upd('CHECK ORDER', '#95a5a6', command=self.clients_to_order)

        # Treeview style
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
        style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
        style.map("Treeview", background=[('selected', '#b5d9ff')])

        tree_frame = tk.Frame(self)
        tree_frame.place(x=120, y=105, width=1100, height=475)

        self.client_tree = ttk.Treeview(        
            tree_frame,
            columns=('client_id', 'client_name', 'client_email', 'client_add', 'client_num'),
            show='headings',
            style='Treeview'
        )
        self.client_tree.bind("<Double-1>", self.show_client_details)


        self._column_heads('client_id', 'CLIENT ID')
        self._column_heads('client_name', 'CLIENT NAME')
        self._column_heads('client_email', 'CLIENT EMAIL')
        self._column_heads('client_add', 'CLIENT ADDRESS')
        self._column_heads('client_num', 'CONTACT NUMBER')

        for col in ('client_id', 'client_name', 'client_email', 'client_add', 'client_num'):
            self.client_tree.column(col, width=400, stretch=False)

        # Scrollbars
        self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.client_tree.yview)
        self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.client_tree.xview)
        self.client_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Use grid for proper layout
        self.client_tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="w")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Make the treeview expandable
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.load_clients_from_db()

    def on_show(self):
        on_show(self)

    def handle_logout(self):
        handle_logout(self)

    def add_del_upd(self, text, fg_color,  command):
        button = ctk.CTkButton(self, text=text, width=73, fg_color = fg_color, command=command)
        button.pack(side="left", anchor="n", padx=4)

    def load_clients_from_db(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, client_name, client_email, client_address, client_contactnum FROM clients")
            rows = cursor.fetchall()
            for i in self.client_tree.get_children():
                self.client_tree.delete(i)
            for row in rows:
                self.client_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.client_act_error.error(f"Error loading clients from DB: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            conn.close()

    def add_clients(self):
        #Information Fill up for adding a new client
        try:
            if hasattr(self, 'add_window') and self.add_window.winfo_exists():
                self.add_window.lift()
                return
            self.add_window = tk.Toplevel()
            self.add_window.geometry('500x400')
            self.add_window.title('Add Client')
            self.add_window.config(bg='white')
            labels = ["Client ID:", "Client Name:", "Client Email:", "Client Address:", "Client Number:"]
            self.entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.add_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                entry = CTkEntry(self.add_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.entries.append(entry)

            #Client Insertion to DB
            def client_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                client_data = [e.get().strip() for e in self.entries]
                keys = ['client_id', 'client_name', 'client_email', 'client_add', 'client_num']
                data_dict = dict(zip(keys, client_data))
                for key, value in data_dict.items():
                    if not value:
                        messagebox.showerror("Input Error", f"{key.replace('_', ' ').title()} cannot be empty.")
                        return
                try:
                    int(data_dict['client_num'])
                except ValueError:
                    messagebox.showerror("Input Error", "Client Number must be numeric.")
                    return
                try:
                    conn = sqlite3.connect('main.db')
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO clients (client_id, client_name, client_email, client_address, client_contactnum)
                        VALUES (?, ?, ?, ?, ?)
                    """, tuple(client_data))
                    conn.commit()
                    messagebox.showinfo("Success", "Client registered successfully!")
                    c.execute("""
                        INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)""",
                        (user_id, f"ADDED CLIENT {data_dict['client_id']}", timestamp))
                    conn.commit()
                    self.load_clients_from_db()
                    self.add_window.destroy()
                    self.client_act.info(f"Client {data_dict['client_id']} added successfully, Time: {timestamp}")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.client_act_error.error(f"Error adding client: {e}, Time: {timestamp}")
                finally:
                    conn.close()
            submit_btn = CTkButton(self.add_window, text='Submit All', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=client_to_db)
            submit_btn.grid(row=len(labels), column=0, columnspan=3, pady=20)
        except Exception as e:
            print(f"Error while creating Add Client window: {e}")
            self.client_act_error.error(f"Error while creating Add Client window: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def srch_clients(self):
        search_client = self.search_entry.get().strip().lower()
        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM clients WHERE client_id = ?", (search_client,))
            row = c.fetchone()
            for i in self.client_tree.get_children():
                self.client_tree.delete(i)
            if row:
                self.client_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Not Found", f"No client found with ID '{search_client}'")
                self.load_clients_from_db()
                self.client_act_warning.warning(f"Client ID '{search_client}' not found, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.client_act_error.error(f"Error searching client: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            conn.close()

    def del_clients(self):
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.client_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a client to delete.")
            return
        try:
            values = self.client_tree.item(selected, 'values')
            client_id = values[0]
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete client ID '{client_id}'?")
            if not confirm:
                return
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
            row = c.fetchone()
            if row:
                c.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Client ID '{client_id}' has been deleted.")
                self.load_clients_from_db()
                c.execute(""" INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)""",
                        (user_id, f"DELETED CLIENT {client_id}", timestamp))
                conn.commit()
                self.client_act.info(f"Client {client_id} deleted successfully, Time: {timestamp}")
            else:
                messagebox.showinfo("Not Found", f"No client found with ID '{client_id}'")
                self.client_act_warning.warning(f"Client ID '{client_id}' not found for deletion, Time: {timestamp}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.client_act_error.error(f"Error deleting client: {e}, Time: {timestamp}")
        finally:
            conn.close()

    def upd_clients(self):
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.client_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return
        values = self.client_tree.item(selected, 'values')
        original_id = values[0]
        top = tk.Toplevel(self)
        top.title("Update Client")
        top.geometry("500x400")
        top.config(bg="white")
        fields = ['Client ID', "Client Name", "Client Email", "Client Address", "Client Phone"]
        entries = []
        for i, (label, value) in enumerate(zip(fields, values)):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            if label == 'Client ID':
                entry.configure(state='readonly')
            entries.append(entry)
        def update_field(idx):
            new_value = entries[idx].get().strip()
            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx]} cannot be empty.")
                return
            col_names = ['client_id', 'client_name', 'client_email', 'client_address', 'client_contactnum']
            col = col_names[idx]
            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute('PRAGMA foreign_keys = ON;')
                if col == 'client_id':
                    messagebox.showinfo("Info", "Client ID cannot be changed.")
                    return
                c.execute(f"UPDATE clients SET {col} = ? WHERE client_id = ?", (new_value, original_id))
                conn.commit()
                messagebox.showinfo("Success", f"{fields[idx]} updated!")
                c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)""",
                        (user_id, f"UPDATED {col.replace('_', ' ').upper()} OF CLIENT {original_id} TO {new_value}", timestamp))
                conn.commit()
                self.load_clients_from_db()
                self.client_act.info(f"Client {original_id} updated {col.replace('_', ' ').upper()} to {new_value}, Time: {timestamp}")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.client_act_error.error(f"Error updating client {original_id}: {e}, Time: {timestamp}")
            finally:
                conn.close()
        for i in range(1, len(fields)):
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
                c.execute('''UPDATE clients SET client_name=?, client_email=?, client_address=?, client_contactnum=? WHERE client_id=?
                ''', (all_values[1], all_values[2], all_values[3], all_values[4], original_id))
                conn.commit()
                messagebox.showinfo("Success", "All fields updated!")
                #User Log Actions if Updated ALL values in the client DATA
                c.execute('''INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)''',
                        (user_id, f"UPDATED ALL FIELDS OF CLIENT {original_id} TO {', '.join(all_values[1:])}", timestamp))
                conn.commit()
                self.load_clients_from_db()
                self.client_act.info(f"Client {original_id} updated all fields to {', '.join(all_values[1:])}, Time: {timestamp}")
                top.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.client_act_error.error(f"Error updating all fields of client {original_id}: {e}, Time: {timestamp}")
            finally:
                conn.close()
        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)

    def clients_to_order(self):
        search_id = self.search_entry.get().strip().lower()
        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        try:
            c.execute('''SELECT * FROM orders WHERE client_id = ?''', (search_id,))
            rows = c.fetchall() 
            for i in self.client_tree.get_children():
                self.client_tree.delete(i)
            for row in rows:
                self.client_tree.insert("", "end", values=row)
            if not rows:
                messagebox.showinfo("No results", "No orders found for this client ID.")
                self.load_clients_from_db()
                self.client_act_warning.warning(f"No orders found for client ID '{search_id}', Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", "Database Error", f"An error occurred: {e}")
            self.load_clients_from_db()
            self.client_act_error.error(f"Error fetching orders for client ID '{search_id}': {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            return
        finally:
            conn.close()

    def show_client_details(self, event):
        selected = self.client_tree.focus()
        if not selected:
            return
        values = self.client_tree.item(selected, 'values')
        client_information = values[0:5]  # Assuming the first 5 values are relevant for the popup
        client_information = "\n".join(f"{key}: {value}" for key, value in zip(['Client ID', 'Name', 'Email', 'Address', 'Contact'], client_information))


        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            client_history = c.execute("""
                SELECT o.order_id, o.product_id, o.order_date, o.deadline
                FROM orders o
                WHERE o.client_id = ?
                """, (values[0],)).fetchall()
            
            if not client_history:
                messagebox.showinfo("No History", "No order history found for this client.")
                return

            else:
                client_information += "\n\nOrder History:\n"
                client_information += "\n".join(f"Order ID: {row[0]}, Product ID: {row[1]}, Order Date: {row[2]}, Deadline: {row[3]}" for row in client_history)

                popup = tk.Toplevel(self)
                popup.title("User Order History")
                popup.geometry("400x300")
                txt = tk.Text(popup, wrap="word", state="normal")
                txt.insert("1.0", client_information)
                txt.configure(state="disabled")
                txt.pack(expand=True, fill="both", padx=10, pady=10)
                self.client_act.info(f"Client details viewed for ID: {values[0]}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", "An error occurred while accessing the database.")
            print(e)
            return
        except Exception as e:
            messagebox.showerror(f'Unexpected Error {e}')
            print(e)
            return
        finally:
            conn.close()


    def _column_heads(self, columns, text):
        self.client_tree.heading(columns, text=text)
        self.client_tree.column(columns, width=400, stretch=False)

    def _main_buttons(self, parent, image, text, command):
        button = ctk.CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)
    
    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        image = image.resize(size)
        return CTkImage(image)

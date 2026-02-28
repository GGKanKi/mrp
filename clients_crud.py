import tkinter as tk
import pytz
from tkinter import font
from datetime import datetime
from tkinter import ttk, messagebox
import customtkinter as ctk
import customtkinter as ctk, customtkinter
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import os
import uuid
import logging
# --- Pathing Setup ---
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from pages_handler import FrameNames
from global_func import on_show, handle_logout, resource_path
from log_f.user_activity_logger import user_activity_logger


class ClientsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')
        self.client_details_window = None  # Variable to track the client details window
        self.update_window = None  # Variable to track the update client window

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0)) 

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
        parent.pack_propagate(False)

        #Logger Files
        logging.basicConfig(filename=os.path.join(BASE_DIR, 'log_f', 'actions.log'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.client_act = logging.getLogger('CLIENT_ACT')
        self.client_act.setLevel(logging.INFO)

        self.client_act_warning = logging.getLogger('CLIENT_ACT_WARNING')
        self.client_act_warning.setLevel(logging.WARNING)

        self.client_act_error = logging.getLogger('CLIENT_ACT_ERROR')
        self.client_act_error.setLevel(logging.ERROR)

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

        self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.srch_clients)
        self.add_btn = self.add_del_upd('ADD CLIENT', '#2ecc71', command=self.add_clients)
        self.del_btn = self.add_del_upd('DELETE CLIENT', '#e74c3c', command=self.del_clients)
        self.update_btn = self.add_del_upd('UPDATE CLIENT', '#f39c12', command=self.upd_clients)

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
        
        self.client_tree = ttk.Treeview(        
            tree_frame,
            columns=('client_id', 'client_name', 'client_email', 'client_add', 'client_num', 'last_updated', 'notes', 'is_active'),
            show='headings',
            style='Custom.Treeview'
        )
        self.client_tree.bind("<Double-1>", self.show_client_details)


        self._column_heads('client_id', 'CLIENT ID')
        self._column_heads('client_name', 'CLIENT NAME')
        self._column_heads('client_email', 'CLIENT EMAIL')
        self._column_heads('client_add', 'CLIENT ADDRESS')
        self._column_heads('client_num', 'CONTACT NUMBER')
        self._column_heads('last_updated', 'LAST UPDATED')
        self._column_heads('notes', 'NOTES')
        self._column_heads('is_active', 'ACTIVE (1 or 0)')

        for col in ('client_id', 'client_name', 'client_email', 'client_add', 'client_num', 'last_updated', 'notes', 'is_active'):
            self.client_tree.column(col, width=200, stretch=False)

        # Scrollbars
        self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.client_tree.yview)
        self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.client_tree.xview)
        self.client_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Use grid for proper layout within the tree_frame
        self.client_tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Make the treeview expandable
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Add a small frame in the corner to avoid scrollbar overlap
        corner_grip = tk.Frame(tree_frame)
        corner_grip.grid(row=1, column=1, sticky="nsew")

        self.load_clients_from_db()

    def on_show(self):
        on_show(self)

    def handle_logout(self):
        handle_logout(self)

    def add_del_upd(self, text, fg_color, command):
        button = ctk.CTkButton(self, text=text, width=90, fg_color=fg_color, command=command, font=('Futura', 15, 'bold'))
        button.pack(side="left", anchor="n", padx=4)

    def load_clients_from_db(self):
        try:
            conn = sqlite3.connect(resource_path("main.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, client_name, client_email, client_address, client_contactnum, last_updated, notes, is_active FROM clients WHERE is_active = 1 ORDER BY client_name")
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
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to add clients.")
            self.client_act_warning.warning(f"Unauthorized add client attempt by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            return
        #Information Fill up for adding a new client
        try:
            if hasattr(self, 'add_window') and self.add_window.winfo_exists():
                self.add_window.lift()
                return
            self.add_window = tk.Toplevel()
            self.add_window.geometry('500x400')
            self.add_window.title('Add Client')
            self.add_window.config(bg='white')
            labels = ["Client Name:", "Client Email:", "Client Address:", "Client Number:", "Notes: (Optional)"]
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
                
                client_id = f"CLT-{uuid.uuid4().hex[:8].upper()}"
                client_data = [e.get().strip() for e in self.entries]
                keys = ['client_name', 'client_email', 'client_add', 'client_num', 'notes']
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
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()

                    c.execute("""
                        INSERT INTO clients (client_id, client_name, client_email, client_address, client_contactnum, notes, date_created, last_updated, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (client_id,) + tuple(client_data) + (timestamp, timestamp, 1))
                    conn.commit()
                    messagebox.showinfo("Success", "Client registered successfully!")
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)""",
                        (user_id, f"ADDED CLIENT {client_id}", timestamp))
                    conn.commit()
                    
                    # Log to user_activity.log
                    username = self.controller.session.get('username', 'Unknown')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action=f"Added client {client_id}",
                        feature="client",
                        operation="create",
                        details=f"Client name: {data_dict['client_name']}, Email: {data_dict['client_email']}"
                    )
                    
                    self.load_clients_from_db()
                    self.add_window.destroy()
                    self.client_act.info(f"Client {client_id} added successfully, Time: {timestamp}")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.client_act_error.error(f"Error adding client: {e}, Time: {timestamp}")
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: raw_mats.mat_id" in str(e) or "UNIQUE constraint failed: raw_mats.mat_name" in str(e):
                        messagebox.showerror("Input Error", "Material ID already exists. Please use a unique ID.")
                    else:
                        messagebox.showerror("Database Error", str(e))
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
        user_id = self.controller.session.get('user_id')
        username = self.controller.session.get('username', 'Unknown')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            query = """
                SELECT *
                FROM clients
                WHERE client_name LIKE ? 
                AND is_active = 1
                ORDER BY client_name
            """
            params = (f'%{search_client}%',)
            rows = c.execute(query, params).fetchall()
            for i in self.client_tree.get_children():
                self.client_tree.delete(i)
            if rows:
                for row in rows:
                    self.client_tree.insert("", "end", values=row)
                    
                # Log successful search to user_activity.log
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Searched for client '{search_client}'",
                    feature="client",
                    operation="search",
                    details=f"Found {len(rows)} results"
                )
            else:
                messagebox.showinfo("Not Found", f"No client found matching '{search_client}'")
                self.load_clients_from_db()
                self.client_act_warning.warning(
                    f"Client search '{search_client}' not found, Time: {timestamp}"
                )
                
                # Log unsuccessful search to user_activity.log
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Searched for client '{search_client}'",
                    feature="client",
                    operation="search",
                    details="No results found"
                )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.client_act_error.error(
                f"Error searching client: {e}, Time: {timestamp}"
            )
        finally:
            conn.close()

    def del_clients(self):

        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.client_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a client to delete.")
            return

        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to delete clients.")
            self.client_act_warning.warning(f"Unauthorized delete client attempt by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            return


        try:
            values = self.client_tree.item(selected, 'values')
            client_id = values[0]
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete client ID '{client_id}'?")
            if not confirm:
                return

            with sqlite3.connect(resource_path('main.db')) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
                row = c.fetchone()
                is_inactive_cal = 0
                if row:
                    c.execute("UPDATE clients SET is_active = ? WHERE client_id = ?", (is_inactive_cal, client_id))
                    c.execute(
                        "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                        (user_id, f"DELETED CLIENT {client_id}", timestamp)
                    )
                    
                    # Log to user_activity.log
                    username = self.controller.session.get('username', 'Unknown')
                    client_name = row[1] if len(row) > 1 else 'Unknown'
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action=f"Deleted client {client_id}",
                        feature="client",
                        operation="delete",
                        details=f"Client name: {client_name}"
                    )
                    
                    messagebox.showinfo("Deleted", f"Client ID '{client_id}' has been deleted.")
                    self.load_clients_from_db()
                    self.client_act.info(f"Client {client_id} deleted successfully, Time: {timestamp}")
                else:
                    messagebox.showinfo("Not Found", f"No client found with ID '{client_id}'")
                    self.client_act_warning.warning(f"Client ID '{client_id}' not found for deletion, Time: {timestamp}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.client_act_error.error(f"Error deleting client: {e}, Time: {timestamp}")

        finally:
            if conn:
                conn.close()
                self.load_clients_from_db()

    def upd_clients(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'manager', 'owner'):
            messagebox.showwarning("Access Denied", "You do not have permission to update clients.")
            self.client_act_warning.warning(
                f"Unauthorized add client attempt by {user_type}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return

        # If an update window is already open, close it
        if self.update_window is not None and self.update_window.winfo_exists():
            self.update_window.destroy()

        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.client_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an item to update.")
            return
        values = self.client_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        self.update_window = top  # Store reference to the window
        top.title(f"Update Client - {original_id}")
        top.geometry("550x600")
        top.config(bg="white")
        top.resizable(False, False)

        fields = ['Client ID', "Client Name", "Client Email", "Client Address", "Client Phone", 'Last Updated', 'Notes', 'Active (1 or 0)']
        entries = []

        for i, (label, value) in enumerate(zip(fields, values)):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            if label == 'Client ID' or label == 'Last Updated':
                entry.configure(state='disabled')
            entries.append(entry)

        def update_field(idx):
            new_value = entries[idx].get().strip()
            if not new_value:
                messagebox.showerror("Input Error", f"{fields[idx]} cannot be empty.")
                return

            col_names = ['client_id', 'client_name', 'client_email', 'client_address', 'client_contactnum', 'last_updated', 'notes', 'is_active']
            col = col_names[idx]

            if col == 'client_id' or col == 'last_updated':
                messagebox.showinfo("Info", "Client ID and Last Update cannot be changed.")
                return

            if col == 'is_active':
                if new_value not in ('0', '1'):
                    messagebox.showerror("Input Error", "Active field must be 1 (active) or 0 (inactive).")
                    return
                new_value = int(new_value)

            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute('PRAGMA foreign_keys = ON;')

                # Update the selected field and last_updated timestamp
                c.execute(
                    f"UPDATE clients SET {col} = ?, last_updated = ? WHERE client_id = ?",
                    (new_value, timestamp, original_id)
                )
                conn.commit()

                messagebox.showinfo("Success", f"{fields[idx]} updated!")

                # Insert user log
                c.execute(
                    "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                    (user_id, f"UPDATED {col.replace('_', ' ').upper()} OF CLIENT {original_id} TO {new_value}", timestamp)
                )
                conn.commit()

                # Log to user_activity.log
                username = self.controller.session.get('username', 'Unknown')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Updated client {original_id}",
                    feature="client",
                    operation="update",
                    details=f"Changed {col.replace('_', ' ')} to '{new_value}'"
                )

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

            # Validate is_active field
            if all_values[-1] not in ('0', '1'):
                messagebox.showerror("Input Error", "Active field must be 1 (active) or 0 (inactive).")
                return

            try:
                conn = sqlite3.connect(resource_path('main.db'))
                c = conn.cursor()
                c.execute('PRAGMA foreign_keys = ON;')

                # Update all editable fields and last_updated timestamp
                c.execute('''
                    UPDATE clients SET
                        client_name = ?,
                        client_email = ?,
                        client_address = ?,
                        client_contactnum = ?,
                        notes = ?,
                        is_active = ?,
                        last_updated = ?
                    WHERE client_id = ?
                ''', (
                    all_values[1],  # client_name
                    all_values[2],  # client_email
                    all_values[3],  # client_address
                    all_values[4],  # client_contactnum
                    all_values[6],  # notes
                    int(all_values[7]),  # is_active
                    timestamp,
                    original_id
                ))
                conn.commit()

                messagebox.showinfo("Success", "All fields updated!")

                # Insert user log
                c.execute(
                    "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                    (user_id, f"UPDATED ALL FIELDS OF CLIENT {original_id} TO {', '.join(all_values[1:])}", timestamp)
                )
                conn.commit()

                # Log to user_activity.log
                username = self.controller.session.get('username', 'Unknown')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action=f"Updated all fields for client {original_id}",
                    feature="client",
                    operation="update",
                    details=f"New values: Name={all_values[1]}, Email={all_values[2]}, Address={all_values[3]}, Phone={all_values[4]}, Notes={all_values[6]}, Active={all_values[7]}"
                )

                self.load_clients_from_db()
                self.client_act.info(f"Client {original_id} updated all fields to {', '.join(all_values[1:])}, Time: {timestamp}")
                top.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.client_act_error.error(f"Error updating all fields of client {original_id}: {e}, Time: {timestamp}")

            finally:
                conn.close()
                self.load_clients_from_db()

        update_all_btn = CTkButton(top, text="Update All", width=120, fg_color="#6a9bc3", command=update_all)
        update_all_btn.grid(row=len(fields), column=0, columnspan=3, pady=20)


    def show_client_details(self, event):
        selected = self.client_tree.focus()
        if not selected:
            return
        values = self.client_tree.item(selected, 'values')
        client_id = values[0]
        
        # If a window is already open, close it
        if self.client_details_window is not None and self.client_details_window.winfo_exists():
            self.client_details_window.destroy()
        
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            client_history = c.execute("""
                SELECT o.order_id, o.order_name, o.product_id, o.quantity, o.order_date, o.deadline, o.status_quo
                FROM orders o
                WHERE o.client_id = ?
            """, (client_id,)).fetchall()
            
            # Create a better designed popup window
            popup = tk.Toplevel(self)
            self.client_details_window = popup  # Store reference to the window
            popup.title(f"Client Details - {values[1]}")
            popup.geometry("800x600")
            popup.configure(bg='white')
            
            # Client information frame
            client_frame = CTkFrame(popup, fg_color="#e6f2ff", corner_radius=10)
            client_frame.pack(fill="x", padx=20, pady=10)
            
            # Client details header
            header_label = CTkLabel(client_frame, text="CLIENT INFORMATION", font=('Futura', 16, 'bold'), 
                                    text_color="#003366", fg_color="#e6f2ff")
            header_label.pack(pady=(10, 5))
            
            # Client details
            fields = ['Client ID', 'Name', 'Email', 'Address', 'Contact']
            for i, (field, value) in enumerate(zip(fields, values[:5])):
                info_frame = CTkFrame(client_frame, fg_color="#e6f2ff")
                info_frame.pack(fill="x", padx=20, pady=2)
                
                field_label = CTkLabel(info_frame, text=f"{field}:", font=('Arial', 12, 'bold'), 
                                      text_color="#003366", width=100, anchor="w")
                field_label.pack(side="left", padx=(10, 5))
                
                value_label = CTkLabel(info_frame, text=f"{value}", font=('Arial', 12), 
                                      text_color="#000000", anchor="w")
                value_label.pack(side="left", fill="x", expand=True)
            
            # Order history section
            if not client_history:
                no_history = CTkLabel(popup, text="No order history found for this client.", 
                                     font=('Arial', 14), text_color="#666666")
                no_history.pack(pady=50)
            else:
                # Order history header
                history_header = CTkLabel(popup, text="ORDER HISTORY", font=('Futura', 16, 'bold'), 
                                         text_color="#003366")
                history_header.pack(pady=(20, 10))
                
                # Create a fixed-size frame for the order history table (non-resizable)
                table_container = CTkFrame(popup, fg_color="white", corner_radius=10)
                table_container.pack(pady=(0, 20))
                # Set fixed width and height to prevent resizing
                table_container.pack_propagate(False)
                table_container.configure(width=700, height=300)
                
                # Create a frame for the order history table
                table_frame = CTkFrame(table_container, fg_color="white", corner_radius=10)
                table_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Create a canvas with scrollbar for the order history
                canvas = tk.Canvas(table_frame, bg="white", highlightthickness=0)
                scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg="white")
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                # Center the content in the canvas
                canvas.create_window((350, 0), window=scrollable_frame, anchor="n")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Order history table headers - removed Order ID, Product ID, and Deadline
                headers = ['Order Name', 'Quantity', 'Order Date', 'Status']
                for col, header in enumerate(headers):
                    header_label = tk.Label(scrollable_frame, text=header, font=('Arial', 12, 'bold'), 
                                          bg="#007acc", fg="white", padx=10, pady=5)
                    header_label.grid(row=0, column=col, sticky="ew")
                
                # Order history data - skip Order ID (index 0), Product ID (index 2), and Deadline (index 5)
                for row_idx, order in enumerate(client_history, start=1):
                    bg_color = "#f0f7ff" if row_idx % 2 == 0 else "white"
                    # Create a filtered list without Order ID, Product ID, and Deadline
                    filtered_values = [order[1], order[3], order[4], order[6]]
                    for col_idx, value in enumerate(filtered_values):
                        cell = tk.Label(scrollable_frame, text=str(value), font=('Arial', 11), 
                                      bg=bg_color, padx=10, pady=5, borderwidth=1, 
                                      relief="groove", anchor="center", width=15)
                        cell.grid(row=row_idx, column=col_idx, sticky="ew")
            
            # Close button
            close_btn = CTkButton(popup, text="Close", font=("Arial", 12), width=120, height=30,
                                fg_color="#007acc", corner_radius=10, command=popup.destroy)
            close_btn.pack(pady=(0, 20))
            
            self.client_act.info(f"Client details viewed for ID: {client_id}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", "An error occurred while accessing the database.")
            print(e)
            return
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))
            print(e)
            return
        finally:
            conn.close()


    def _column_heads(self, columns, text):
        self.client_tree.heading(columns, text=text)
        self.client_tree.column(columns, width=400, stretch=False)

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
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkComboBox
import sqlite3
from PIL import Image
from tkinter import messagebox, filedialog
import os
from datetime import datetime
import pytz
import time
import json
import logging

# --- Pathing Setup ---
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


from pages_handler import FrameNames
from global_func import on_show, handle_logout, create_email, see_mails, to_gmail_web, resource_path


class MessagesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.add_window = None
        self.user_info_window = None

        #Logging Info, Errors, 
        logging.basicConfig(filename=os.path.join(BASE_DIR, 'log_f', 'mails.log'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.mail_log = logging.getLogger('MAIL_LOGS')
        self.mail_log.setLevel(logging.INFO)

        self.mail_warning = logging.getLogger('MAIL_WARNING')
        self.mail_warning.setLevel(logging.WARNING)

        self.mail_error = logging.getLogger('MAIL_ERROR')
        self.mail_error.setLevel(logging.ERROR)

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0))

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

        novus_logo = Image.open(os.path.join(BASE_DIR, 'labels', 'novus_logo1.png'))
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))


        #User Type Var
        user_type = self.controller.session.get('usertype')


        #Buttons Images
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



        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.pack(side="left",anchor="n", padx=(15, 20), ipadx=150)



        self.add_btn = self.add_del_upd('CREATE MAIL', '#2ecc71', command=lambda: create_email(self.controller))
        self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.search_user)
        self.see_mails = self.add_del_upd('SEE MAILS', '#f1c40f', command=to_gmail_web)
        self.delete_user_btn = self.add_del_upd('DELETE USER', '#913831', command =self.delete_user )
        # Make CREATE ACCOUNT button visible to all users
        self.create_account_btn = self.add_del_upd('CREATE ACCOUNT', '#2ecc71', command=self.create_account)
        self.refresh_btn = self.add_del_upd('REFRESH DATA', '#2ecc71', command=self.load_users)
        
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

        self.mail_tree = ttk.Treeview(
            tree_frame,
            columns=('user_id', 'f_name', 'l_name', 'useremail', 'phonenum'),
            show='headings',
            style='Custom.Treeview'
        )
        self.mail_tree.bind("<Double-1>", self.user_information)


        self._column_heads('user_id', 'USER ID')
        self._column_heads('f_name', 'FIRST NAME')
        self._column_heads('l_name', 'LAST NAME')
        self._column_heads('useremail', 'E-MAIL')
        self._column_heads('phonenum', 'PHONE NUMBER')

                    
        for col in ('user_id', 'f_name', 'l_name', 'useremail', 'phonenum'):
            self.mail_tree.column(col, width=300, stretch=False)
        
            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.mail_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.mail_tree.xview)
            self.mail_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.mail_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

        # Add a small frame in the corner to avoid scrollbar overlap
        corner_grip = tk.Frame(tree_frame)
        corner_grip.grid(row=1, column=1, sticky="nsew")

        # Load initial data
        self.load_users()

    def destroy(self):
        """Override destroy to clean up any open Toplevel windows."""
        if self.add_window and self.add_window.winfo_exists():
            self.add_window.destroy()
        if self.user_info_window and self.user_info_window.winfo_exists():
            self.user_info_window.destroy()
        super().destroy()
    def create_account(self):
        if( user_type := self.controller.session.get('usertype')) not in ('owner', 'admin'):
            messagebox.showwarning('Error', 'Only the owner can create new accounts.')
            return

        self.controller.show_frame(FrameNames.SIGNUP)


    def load_mails(self):
        try:
            conn = sqlite3.connect(resource_path("main.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, f_name, l_name, useremail, phonenum FROM users")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.mail_tree.get_children():
                self.mail_tree.delete(i)

            for row in rows:
                self.mail_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.mail_error.error(f"Database Error: {e}")
        finally:
            conn.close()

    def add_mail(self):
        user_type = self.controller.session.get('usertype')
        user_id = self.controller.session.get('user_id')

        print(f'DEBUG {user_type, user_id}')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        try:
            if hasattr(self, 'add_window') and self.add_window.winfo_exists():
                self.add_window.lift()
                return
            self.add_window = tk.Toplevel(self)
            self.add_window.geometry('600x500')  # Increased size for attachments
            self.add_window.title('Write New Mail')
            self.add_window.config(bg='white')

            conn = sqlite3.connect(resource_path("main.db"))
            c = conn.cursor()
            c.execute("SELECT user_id, f_name, l_name FROM users WHERE user_id != ?", (user_id,))
            users = c.fetchall()
            conn.close()

            user_options = [f"{user[0]} - {user[1]} {user[2]}" for user in users]
            self.users_id = tk.StringVar(value=user_options[0] if user_options else "No Users Available")

            # USER ID
            CTkLabel(self.add_window, text='USER ID:', font=('Futura', 13, 'bold')).grid(row=0, column=0, padx=15, pady=10, sticky='e')
            usermail_drop = ctk.CTkOptionMenu(self.add_window, variable=self.users_id, values=user_options if user_options else ["No Users Available"])
            usermail_drop.grid(row=0, column=1, padx=10, pady=10, sticky='w')

            # Topic Title
            CTkLabel(self.add_window, text="Topic Title:", font=('Futura', 13, 'bold')).grid(row=1, column=0, padx=15, pady=10, sticky='e')
            topic_entry = CTkEntry(self.add_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
            topic_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

            # Body
            CTkLabel(self.add_window, text="Body:", font=('Futura', 13, 'bold')).grid(row=2, column=0, padx=15, pady=10, sticky='e')
            body_entry = ctk.CTkTextbox(self.add_window, height=100, width=300, border_width=2, border_color='#6a9bc3')
            body_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

            # Priority
            CTkLabel(self.add_window, text="Priority:", font=('Futura', 13, 'bold')).grid(row=3, column=0, padx=15, pady=10, sticky='e')
            self.mail_priority_var = tk.StringVar(value="2")
            self.mail_priority_dd = ctk.CTkComboBox(self.add_window,
                                                    variable=self.mail_priority_var,
                                                    values=["1", "2", "3"],
                                                    width=100,
                                                    height=25,
                                                    border_width=1,
                                                    corner_radius=6)
            self.mail_priority_dd.grid(row=3, column=1, padx=10, pady=10, sticky='w')

            # File Attachment
            CTkLabel(self.add_window, text="Attachment:", font=('Futura', 13, 'bold')).grid(row=4, column=0, padx=15, pady=10, sticky='e')
            self.attachment_path = tk.StringVar()
            attachment_entry = CTkEntry(self.add_window, textvariable=self.attachment_path, height=28, width=220, border_width=2, border_color='#6a9bc3')
            attachment_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
            
            browse_btn = ctk.CTkButton(self.add_window, text="Browse", width=80, height=28, 
                                    command=self.browse_attachment)
            browse_btn.grid(row=4, column=2, padx=5, pady=10)

            self.mail_entries = [topic_entry, body_entry]

            def send_mail():
                if not user_options:
                    messagebox.showerror("Input Error", "No users available to send mail to.")
                    return
                
                try:
                    conn = sqlite3.connect(resource_path("main.db"))
                    c = conn.cursor()
                    
                    # Insert the main message
                    c.execute("""
                        INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp, priority) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        self.users_id.get().split(' - ')[0],
                        self.mail_entries[0].get(),
                        self.mail_entries[1].get("1.0", "end").strip(),
                        timestamp,
                        self.mail_priority_var.get()
                    ))
                    
                    # Get the last inserted message_id
                    message_id = c.lastrowid
                    
                    # Handle attachment if provided
                    attachment_path = self.attachment_path.get()
                    if attachment_path and os.path.exists(attachment_path):
                        try:
                            with open(attachment_path, 'rb') as file:
                                file_data = file.read()
                                file_name = os.path.basename(attachment_path)
                                file_type = os.path.splitext(file_name)[1][1:]
                                file_size = len(file_data)
                                
                                # Insert attachment
                                c.execute("""
                                    INSERT INTO message_attachments (message_id, file_name, file_type, file_size, file_data)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (message_id, file_name, file_type, file_size, file_data))
                                
                        except Exception as e:
                            print(f"Error reading attachment: {e}")
                    
                    conn.commit()
                    messagebox.showinfo("Success", "Mail sent successfully!")
                    self.mail_log.info(f"Mail sent from {user_id} to {self.users_id.get().split(' - ')[0]} with subject '{self.mail_entries[0].get()}' at {timestamp}")
                    
                    # Log to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="create",
                        feature="mail",
                        operation="send_mail",
                        details=f"Sent mail to user ID: {self.users_id.get().split(' - ')[0]}, Subject: '{self.mail_entries[0].get()}', Priority: {self.mail_priority_var.get()}"
                    )
                    
                    self.load_users()
                    self.add_window.destroy()
                    
                except sqlite3.Error as e:
                    conn.rollback()
                    messagebox.showerror("Database Error", f"Failed to send mail: {e}")
                    print(f"Database error: {e}")
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                    print(f"Unexpected error: {e}")
                finally:
                    conn.close()

            submit_btn = CTkButton(self.add_window, text='Send Mail', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=send_mail)
            submit_btn.grid(row=5, column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Mail window: {e}")
            import traceback
            traceback.print_exc()
            
    def del_mail(self):
        selected = self.mail_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a mail to delete.")
            return
        values = self.mail_tree.item(selected, 'values')
        message_id = values[0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the mail with ID {message_id}?")
        if confirm:
            try:
                conn = sqlite3.connect(resource_path("main.db"))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE message_id=?", (message_id,))
                conn.commit()
                conn.close()
                self.load_mails()
                messagebox.showinfo("Success", "Mail deleted successfully.")
                self.mail_log.info(f"Mail with ID {message_id} deleted successfully.")
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                user_id = self.controller.session.get('user_id')
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="delete",
                    feature="mail",
                    operation="delete_mail",
                    details=f"Deleted mail with ID: {message_id}"
                )
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.mail_error.error(f"Database Error: {e}, unable to delete mail with ID {message_id}")

    def delete_user(self):
        selected = self.mail_tree.focus()

        if not selected:
            messagebox.showwarning('Warning', "Please Select A User")
            return  # stop here if nothing is selected

        values = self.mail_tree.item(selected, 'values')
        user_id = values[0]

        if (usertype := self.controller.session.get('usertype')) not in ('admin', 'owner'):
            messagebox.showerror('Error', 'You do not have permission to delete.')
            return

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()

            # Remove from Treeview
            self.mail_tree.delete(selected)

            messagebox.showinfo('Success', f'User {user_id} deleted successfully.')

        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Database Error: {e}')
        finally:
            if conn:
                conn.close()


    def user_information(self, event):
        user_type = self.controller.session.get('usertype')
        selected = self.mail_tree.focus()
        if not selected:
            return
        
        values = self.mail_tree.item(selected, 'values')
        user_id = values[0]

        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            fetch = c.execute("SELECT user_id, f_name, l_name, useremail, phonenum, usertype FROM users WHERE user_id = ?", (user_id,)).fetchone()

            if not fetch:
                messagebox.showinfo("Not Found", "No details found for this user.")
                return

            # --- UI Creation ---
            popup = tk.Toplevel(self)
            self.user_info_window = popup
            popup.title("User Details")
            popup.geometry("700x400")
            popup.configure(bg='white')
            popup.resizable(False, False)
            popup.grab_set()

            # User Info Frame
            user_frame = CTkFrame(popup, fg_color="#e6f2ff", corner_radius=10)
            user_frame.pack(fill="x", padx=20, pady=20)

            header_label = CTkLabel(user_frame, text="USER INFORMATION", font=('Futura', 16, 'bold'), text_color="#003366")
            header_label.pack(pady=(10, 15), anchor="w", padx=20)

            details_frame = CTkFrame(user_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=5, expand=True)
            details_frame.grid_columnconfigure(1, weight=1)
            details_frame.grid_columnconfigure(3, weight=1)

            # Display User Details
            details_map = {
                "User ID:": fetch[0],
                "First Name:": fetch[1],
                "Last Name:": fetch[2],
                "User Level:": fetch[5],
                "Email:": fetch[3],
                "Phone Number:": fetch[4]
            }

            row_num = 0
            for label, value in details_map.items():
                CTkLabel(details_frame, text=label, font=('Arial', 12, 'bold'), text_color="#003366").grid(row=row_num, column=0, sticky='w', padx=5, pady=4)
                CTkLabel(details_frame, text=value, font=('Arial', 12)).grid(row=row_num, column=1, sticky='w', padx=5, pady=4)
                row_num += 1

            # Close button
            close_btn = CTkButton(popup, text="Close", command=popup.destroy, width=120, fg_color="#6a9bc3")
            close_btn.pack(pady=(10, 20))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.mail_error.error(f"Database Error: {e}, unable to fetch user details for ID: {user_id}")
        finally:
            if conn:
                conn.close()


    def load_users(self):
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            fetch_all = c.execute("SELECT * FROM users").fetchall()

            for i in self.mail_tree.get_children():
                self.mail_tree.delete(i)

            for row in fetch_all:
                self.mail_tree.insert("", "end", values=row)
        
        except sqlite3.error as e:
            messagebox.showerror('Database Error', f"Error: {e}")
            return
        finally:
            if conn:
                conn.close()

        
    def search_user(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            messagebox.showinfo("Search", "Please enter a search term")
            return
            
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            
            # Search in multiple columns with wildcard pattern
            query = """SELECT * FROM users WHERE 
                    lower(user_id) LIKE ? OR 
                    lower(f_name) LIKE ? OR 
                    lower(l_name) LIKE ? OR 
                    lower(useremail) LIKE ? OR 
                    lower(phonenum) LIKE ?"""
            
            # Add wildcards to search term
            search_pattern = f"%{search_term}%"
            parameters = (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern)
            
            results = c.execute(query, parameters).fetchall()
            
            # Clear current treeview
            for i in self.mail_tree.get_children():
                self.mail_tree.delete(i)
                
            # Populate with search results
            if results:
                for row in results:
                    self.mail_tree.insert("", "end", values=row)
                messagebox.showinfo("Search Results", f"Found {len(results)} matching users")
            else:
                messagebox.showinfo("Search Results", "No matching users found")
                # Reload all users if no results found
                self.load_users()
                
        except sqlite3.Error as e:
            messagebox.showerror('Database Error', f"Error during search: {e}")
            self.mail_error.error(f"Database Error during search: {e}")
        finally:
            if conn:
                conn.close()


    def browse_attachment(self):
        """Open file dialog to select attachment"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Attachment",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("Document files", "*.doc *.docx *.xls *.xlsx")
            ]
        )
        if file_path:
            self.attachment_path.set(file_path)

    
    def _column_heads(self, columns, text):
        self.mail_tree.heading(columns, text=text)
        self.mail_tree.column(columns, width=195)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, width=70, fg_color=fg_color, command=command, font=('Futura', 12, 'bold'))
        button.pack(side="left", anchor="n", padx=2)

    
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

    def on_show(self):
        # Print user and usertype information when mail page is accessed
        username = self.controller.session.get('username')
        usertype = self.controller.session.get('usertype')
        on_show(self)

    def handle_logout(self):
        handle_logout(self)
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
import sqlite3
from PIL import Image
from tkinter import messagebox, filedialog
import os
from datetime import datetime
import pytz
import time
import json
import logging


from pages_handler import FrameNames
from global_func import on_show, handle_logout


class MessagesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Logging Info, Errors, 
        logging.basicConfig(filename='mails.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.mail_log = logging.getLogger('MAIL_LOGS')
        self.mail_log.setLevel(logging.INFO)

        self.mail_warning = logging.getLogger('MAIL_WARNING')
        self.mail_warning.setLevel(logging.WARNING)

        self.mail_error = logging.getLogger('MAIL_ERROR')
        self.mail_error.setLevel(logging.ERROR)

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0))

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

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


        self.add_btn = self.add_del_upd('CREATE MAIL', command=self.add_mail)
        self.del_btn = self.add_del_upd('DELETE MATERIAL', command=self.del_mail)


        '''        self.srch_btn = self.add_del_upd('SEARCH', command=self.srch_mats)
        self.update_btn = self.add_del_upd('UPDATE MATERIAL', command=self.upd_mats)
        self.check_orders = self.add_del_upd('CHECK MATERIAL', command=self.order_to_supplier)'''

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

        self.mail_tree = ttk.Treeview(
            tree_frame,
            columns=('message_id', 'sender_id', 'receiver_id', 'subject', 'timestamp'),
            show='headings',
            style='Treeview'
        )
        self.mail_tree.bind("<Double-1>", self.show_mail_details)


        self._column_heads('message_id', 'MESSAGE ID')
        self._column_heads('sender_id', 'SENDER')
        self._column_heads('receiver_id', 'RECIEVER')
        self._column_heads('subject', 'TOPIC')
        self._column_heads('timestamp', 'TIME SENT')
                    
        for col in ('message_id', 'sender_id', 'receiver_id', 'subject', 'timestamp'):
            self.mail_tree.column(col, width=300, stretch=False)
        
            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.mail_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.mail_tree.xview)
            self.mail_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.mail_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

        # Load initial data
        self.load_mails()

    def load_mails(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT message_id, sender_id, receiver_id, subject, timestamp FROM messages")
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
            
        #Create Divider

    def add_mail(self):
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        try:
            if hasattr(self, 'add_window') and self.add_window.winfo_exists():
                self.add_window.lift()
                return
            self.add_window = tk.Toplevel()
            self.add_window.geometry('500x400')
            self.add_window.title('Write New Mail')
            self.add_window.config(bg='white')

            conn = sqlite3.connect("main.db")
            c = conn.cursor()
            c.execute("SELECT user_id, f_name, l_name FROM users WHERE user_id != ?", (user_id,))
            users = c.fetchall()
            conn.close()

            #Dropdown for selecting user fir messaging
            self.users_id = tk.StringVar(value="Select Receiver ID")
            self.users_id.set(users[0] if users else "No Users Available")
            CTkLabel(self.add_window, text='USER ID:', font=('Futura', 13, 'bold')).grid(row=3, column=0, padx=15, pady=10, sticky='e')
            usermail_drop = ctk.CTkOptionMenu(self.add_window, variable=self.users_id, values=[f"{user[0]} - {user[1]} {user[2]}" for user in users])
            usermail_drop.grid(row=3, column=1, padx=10, pady=10, sticky='w')

            # Labels and Entries for mail fields
            labels = ["Topic Title:", "Body"]
            self.mail_entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.add_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                if label_text == "Body":
                    entry = ctk.CTkTextbox(self.add_window, height=100, width=300, border_width=2, border_color='#6a9bc3')
                else:
                    entry = CTkEntry(self.add_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.mail_entries.append(entry)

            def save_field(idx):
                value = self.mail_entries[idx].get().strip()
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

            for i in range(len(labels)):
                btn = CTkButton(self.add_window, text="Save", width=60, command=lambda idx=i: save_field(idx))
                btn.grid(row=i, column=2, padx=5, pady=10)

            def send_mail():
                conn = sqlite3.connect("main.db")
                c = conn.cursor()
                c.execute("INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (user_id, self.users_id.get().split(' - ')[0], self.mail_entries[0].get(), self.mail_entries[1].get("1.0", "end").strip(), timestamp))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Mail sent successfully!")
                self.mail_log.info(f"Mail sent from {user_id} to {self.users_id.get().split(' - ')[0]} with subject '{self.mail_entries[0].get()}' at {timestamp}")
                self.load_mails()
            submit_btn = CTkButton(self.add_window, text='Submit All', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=send_mail)
            submit_btn.grid(row=len(labels), column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Client window: {e}")
            self.mail_error.error(f"Error while creating Add Client window: {e}")
    
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
                conn = sqlite3.connect("main.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE message_id=?", (message_id,))
                conn.commit()
                conn.close()
                self.load_mails()
                messagebox.showinfo("Success", "Mail deleted successfully.")
                self.mail_log.info(f"Mail with ID {message_id} deleted successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.mail_error.error(f"Database Error: {e}, unable to delete mail with ID {message_id}")
    
    # This file is part of the NOVUS INDUSTRY SOLUTIONS INVENTORY project.
    #Create a Dropdown for Unread and Read Mails Create color 
    #Create Disparity for Mails (For Admin, For Employee, For Manager, For Clerk)
    def show_mail_details(self, event):
        user_type = self.controller.session.get('user_type')
        selected = self.mail_tree.focus()
        if not selected:
            return
        values = self.mail_tree.item(selected, 'values')
        mails_info = f"Message ID: {values[0]}\nSender ID: {values[1]}\nReceiver ID: {values[2]}\nSubject: {values[3]}\nTimestamp: {values[4]}"
        popup = tk.Toplevel(self)
        popup.title("Mail Details")
        popup.geometry("400x300")
        txt = tk.Text(popup, wrap="word", state="normal")
        txt.insert("1.0", mails_info)
        txt.configure(state="disabled")
        txt.pack(expand=True, fill="both", padx=10, pady=10)

        if user_type == 'admin' or  user_type == 'manager' or user_type == 'clerk':
            def reply_mail():
                if hasattr(self, 'reply_window') and self.reply_window.winfo_exists():
                    self.reply_window.lift()
                    return
                self.reply_window = tk.Toplevel()
                self.reply_window.geometry('500x400')
                self.reply_window.title('Reply to Mail')
                self.reply_window.config(bg='white')

                ctk.CTkLabel(self.reply_window, text='Reply to:', font=('Futura', 13, 'bold')).grid(row=0, column=0, padx=15, pady=10, sticky='e')
                ctk.CTkLabel(self.reply_window, text=values[1], font=('Futura', 13)).grid(row=0, column=1, padx=10, pady=10, sticky='w')
                
                reply_body = ctk.CTkTextbox(self.reply_window, height=100, width=300, border_width=2, border_color='#6a9bc3')
                reply_body.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

                def send_reply():
                    reply_text = reply_body.get("1.0", "end").strip()
                    if not reply_text:
                        messagebox.showerror("Input Error", "Reply body cannot be empty.")
                        return

                    # Insert reply as a new message
                    try:
                        conn = sqlite3.connect("main.db")
                        c = conn.cursor()
                        sender_id = self.controller.session.get('user_id')
                        receiver_id = values[1]  # reply to the original sender
                        subject = "Reply: " + values[3]
                        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                        c.execute(
                            "INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (sender_id, receiver_id, subject, reply_text, timestamp)
                        )
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Reply sent successfully!")
                        self.mail_log.info(f"Reply sent from {sender_id} to {receiver_id} with subject '{subject}' at {timestamp}")
                        self.load_mails()
                        self.reply_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Database Error", str(e))
                        self.mail_error.error(f"Error sending reply: {e}")

                ctk.CTkButton(self.reply_window, text='Send Reply', command=send_reply).grid(row=2, column=0, columnspan=2, pady=20)

            ctk.CTkButton(
                popup, text="Reply", command=reply_mail, width=100, height=30, fg_color='blue',
                bg_color='white', corner_radius=10, border_width=2, border_color='black'
            ).pack(side="bottom", pady=10)
    

    
    def _column_heads(self, columns, text):
        self.mail_tree.heading(columns, text=text)
        self.mail_tree.column(columns, width=195)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
    def add_del_upd(self, text, command):
        button = CTkButton(self, text=text, width=73, command=command)
        button.pack(side="left", anchor="n", padx=4)

    
    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def on_show(self):
        on_show(self)

    def handle_logout(self):
        handle_logout(self)


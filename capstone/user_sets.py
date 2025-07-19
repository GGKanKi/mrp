import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import filedialog
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
import pandas as pd
import re
import logging
import sys
sys.path.append('D:/capstone')

from pages_handler import FrameNames

class UserSet(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0)) 

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))  # Sticks to the top, fills X
        parent.pack_propagate(False)


        #Txt Logs For Info, Warning, Error
        logging.basicConfig(filename='settings.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.sett_info = logging.getLogger('settings_info')
        self.sett_info.setLevel(logging.INFO)

        self.sett_warning = logging.getLogger('settings_warning')
        self.sett_warning.setLevel(logging.WARNING)

        self.sett_error = logging.getLogger('settings_error')
        self.sett_error.setLevel(logging.ERROR)

        self.logout_info = logging.getLogger('logout_info')
        self.logout_info.setLevel(logging.INFO)
        logout_handler = logging.FileHandler('login.log')
        logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logout_handler.setFormatter(logout_formatter)
        self.logout_info.addHandler(logout_handler)

        novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        
        user_type = self.controller.session.get('user_type', '')
        print("DEBUG: user_type =", user_type)

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

        # --- Make the whole card scrollable ---
        scroll_frame = customtkinter.CTkScrollableFrame(self, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Main container for the profile card
        card = CTkFrame(scroll_frame, fg_color="#f5f6fa", corner_radius=20, border_color='#6a9bc3', border_width=2)
        card.pack(padx=40, pady=40, fill="both", expand=True)

        left_col = CTkFrame(card, fg_color="#e1e8ed", width=250, corner_radius=15)
        left_col.pack(side="left", fill="y", padx=(30, 15), pady=30)
        right_col = CTkFrame(card, fg_color="white", corner_radius=15)
        right_col.pack(side="left", fill="both", expand=True, padx=(15, 30), pady=30)

        self.profile_image_label = CTkLabel(left_col, text="No Image", width=120, height=120)
        self.profile_image_label.pack(pady=(20, 10))
        upload_btn = CTkButton(left_col, text="Upload Image", command=self.upload_image, width=120)
        upload_btn.pack(pady=(0, 20))

        # Display name and user type
        self.display_name = CTkLabel(left_col, text=self.controller.session.get('f_name', '') + " " + self.controller.session.get('l_name', ''),
                                    font=("Futura", 18, "bold"), fg_color="#e1e8ed")
        self.display_name.pack(pady=(10, 2))
        self.display_type = CTkLabel(left_col, text=self.controller.session.get('user_type', ''),
                                    font=("Futura", 14), fg_color="#e1e8ed")
        self.display_type.pack(pady=(0, 20))

        title = CTkLabel(right_col, text="User Details", font=("Futura", 22, "bold"), fg_color="white")
        title.pack(pady=(10, 20))

        form = CTkFrame(right_col, fg_color="white")
        form.pack(padx=30, pady=10, fill="x")

        # Helper for adding labeled entries in a grid
        def add_row(label, entry, row):
            CTkLabel(form, text=label, font=('Futura', 15, 'bold'), anchor="w", width=120).grid(row=row, column=0, sticky="w", pady=8, padx=(0, 10))
            entry.grid(row=row, column=1, sticky="ew", pady=8)
            form.grid_columnconfigure(1, weight=1)

        self.user_id_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.user_id_entry.insert(0, self.controller.session.get('user_id', ''))
        add_row("User ID:", self.user_id_entry, 0)

        self.f_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.f_name_entry.insert(0, self.controller.session.get('f_name', ''))
        add_row("First Name:", self.f_name_entry, 1)

        self.m_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.m_name_entry.insert(0, self.controller.session.get('m_name', ''))
        add_row("Middle Name:", self.m_name_entry, 2)

        self.l_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.l_name_entry.insert(0, self.controller.session.get('l_name', ''))
        add_row("Last Name:", self.l_name_entry, 3)

        self.email_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.email_entry.insert(0, self.controller.session.get('e_mail', ''))
        add_row("Email:", self.email_entry, 4)

        self.phone_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.phone_entry.insert(0, self.controller.session.get('number', ''))
        add_row("Phone Number:", self.phone_entry, 5)

        self.username_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.username_entry.insert(0, self.controller.session.get('username', ''))
        add_row("Username:", self.username_entry, 6)

        self.password_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3', show="*")
        self.password_entry.insert(0, self.controller.session.get('password', ''))
        add_row("Password:", self.password_entry, 7)

        self.confirm_pass_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3', show="*")
        self.confirm_pass_entry.insert(0, self.controller.session.get('confirm_pass', ''))
        add_row("Confirm Password:", self.confirm_pass_entry, 8)

        self.user_type_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.user_type_entry.insert(0, self.controller.session.get('user_type', ''))
        add_row("User Type:", self.user_type_entry, 9)

        # Save button at the bottom
        save_btn = CTkButton(right_col, text="Save Changes", command=self.save_user_settings, width=180, fg_color="#6a9bc3")
        save_btn.pack(pady=(30, 10))

    def save_user_settings(self):
        # Get values from entries
        user_id = self.user_id_entry.get()
        f_name = self.f_name_entry.get()
        m_name = self.m_name_entry.get()
        l_name = self.l_name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        user_type = self.user_type_entry.get()

        # Regex validation
        if not re.fullmatch(r"[A-Za-z ]{2,}", f_name):
            messagebox.showerror("Input Error", "First name must contain only letters and spaces.")
            return
        if m_name and not re.fullmatch(r"[A-Za-z ]*", m_name):
            messagebox.showerror("Input Error", "Middle name must contain only letters and spaces.")
            return
        if not re.fullmatch(r"[A-Za-z ]{2,}", l_name):
            messagebox.showerror("Input Error", "Last name must contain only letters and spaces.")
            return
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Input Error", "Invalid email address.")
            return
        if not re.fullmatch(r"\+?\d{10,15}", phone):
            messagebox.showerror("Input Error", "Phone must be 10-15 digits (optionally starting with +).")
            return
        if not re.fullmatch(r"\w{4,20}", username):
            messagebox.showerror("Input Error", "Username must be 4-20 characters (letters, numbers, or _).")
            return
        if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            messagebox.showerror("Input Error", "Password must be at least 8 characters, include a letter and a number.")
            return
        if password != confirm_pass:
            messagebox.showerror("Input Error", "Passwords do not match.")
            return
        if not re.fullmatch(r"[A-Za-z]{3,}", user_type):
            messagebox.showerror("Input Error", "User type must contain only letters.")
            return

        # Update session
        #User Profile Image
        self.profile_image_data = None
        self.profile_image_label = CTkLabel(self.settings_frame, text="No Image")
        self.profile_image_label.pack(side="left", padx=(0, 10))
        CTkButton(self.settings_frame, text="Upload Image", command=self.upload_image).pack(side="left", padx=(0, 10))

        #User Profile Information
        self.controller.session['user_id'] = user_id
        self.controller.session['f_name'] = f_name
        self.controller.session['m_name'] = m_name
        self.controller.session['l_name'] = l_name
        self.controller.session['e_mail'] = email
        self.controller.session['number'] = phone
        self.controller.session['username'] = username
        self.controller.session['password'] = password
        self.controller.session['confirm_pass'] = confirm_pass
        self.controller.session['user_type'] = user_type

        # Update the database
        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("""
                UPDATE users SET f_name = ?, m_name = ?, l_name = ?, useremail = ?, phonenum = ?,
                    username = ?, password = ?, confirmpass = ?, usertype = ? WHERE user_id = ?
            """, (
                f_name, m_name, l_name, email, phone, username, password, confirm_pass, user_type, user_id
            ))
            conn.commit()
            messagebox.showinfo("Success", "User settings updated!")
            self.sett_info.info(f"User settings updated for user_id: {user_id}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.sett_error.error(f"Database error while updating user settings for user_id: {user_id}, Error: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            conn.close()

    def on_show(self):
        # Remove all widgets from self.main (sidebar)
        for widget in self.main.winfo_children():
            widget.destroy()

        user_type = self.controller.session.get('user_type', '')

        self.mrp_main = self._main_buttons(self.main, self.mrp_btn, 'MRP', command=lambda: self.controller.show_frame(FrameNames.MAIN_MRP))

        if user_type == "admin" or user_type == "owner":
            self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
            self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
            self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
            self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
            self.user_logs_main = self._main_buttons(self.main, self.user_logs_btn, 'User Logs', command=lambda: self.controller.show_frame(FrameNames.LOGS))
        elif user_type == "clerk" or user_type == "manager":
            self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
            self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        elif user_type == "employee":
            self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
            self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))

        self.settings_main = self._main_buttons(self.main, self.settings_btn, 'Settings', command=lambda: self.controller.show_frame(FrameNames.SETTINGS))
        self.logout_main = self._main_buttons(self.main, self.logout_btn,  'Logout', command=self.handle_logout)

        # Update profile fields
        self.user_id_entry.delete(0, "end")
        self.user_id_entry.insert(0, self.controller.session.get('user_id', ''))
        self.f_name_entry.delete(0, "end")
        self.f_name_entry.insert(0, self.controller.session.get('f_name', ''))
        self.m_name_entry.delete(0, "end")
        self.m_name_entry.insert(0, self.controller.session.get('m_name', ''))
        self.l_name_entry.delete(0, "end")
        self.l_name_entry.insert(0, self.controller.session.get('l_name', ''))
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, self.controller.session.get('e_mail', ''))
        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, self.controller.session.get('number', ''))
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, self.controller.session.get('username', ''))
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, self.controller.session.get('password', ''))
        self.confirm_pass_entry.delete(0, "end")
        self.confirm_pass_entry.insert(0, self.controller.session.get('confirm_pass', ''))
        self.user_type_entry.delete(0, "end")
        self.user_type_entry.insert(0, self.controller.session.get('user_type', ''))

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT profile_image FROM users WHERE user_id = ?", (self.controller.session.get('user_id'),))
            row = c.fetchone()
            if row and row[0]:
                from io import BytesIO
                img = Image.open(BytesIO(row[0]))
                img = img.resize((100, 100))
                self.profile_photo = CTkImage(img, size=(100, 100))
                self.profile_image_label.configure(image=self.profile_photo, text="")
            else:
                self.profile_image_label.configure(image=None, text="No Image")
        except Exception as e:
            self.profile_image_label.configure(image=None, text="No Image")
        finally:
            conn.close()

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)
        
    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

        
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((100, 100))
                self.profile_photo = CTkImage(image, size=(100, 100))
                self.profile_image_label.configure(image=self.profile_photo, text="")
                # Optionally, store the image data for saving to DB
                with open(file_path, "rb") as f:
                    self.profile_image_data = f.read()

                # Save the image to the database
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute("UPDATE users SET userimage = ? WHERE user_id = ?"
                          , (self.profile_image_data, self.controller.session.get('user_id')))
                conn.commit()
                self.sett_info.info(f"Profile image updated for user_id: {self.controller.session.get('user_id')}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {e}")
                self.sett_error.error(f"Error uploading image: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")


    def handle_logout(self):


        user_id = self.controller.session.get('user_id')
        if user_id:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, 'Logout', timestamp))
            print('DEBUG: User logged out:', user_id, timestamp)
            conn.commit()
            conn.close()
            self.logout_info.info(f"User {user_id} logged out, Time: {timestamp}, From: {__name__}")

        self.controller.show_frame(FrameNames.LOGIN)
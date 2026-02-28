import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel, CTkComboBox
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import re
import uuid
import bcrypt
import pandas as pd
import os
import hashlib

# --- Pathing Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from pages_handler import FrameNames
from global_func import load_credentials_if_logged_in, send_email_with_attachment
from global_func import load_credentials_if_logged_in, send_email_with_attachment, resource_path



class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        # Main container for the signup form to allow better centering and padding
        container = CTkFrame(self, fg_color='white')
        container.pack(fill="both", expand=True)

        # Title
        title = CTkLabel(container,
                         text="CREATE NEW USER ACCOUNT",
                         font=('Futura', 25, 'bold'))
        title.pack(pady=(20, 10))

        # Signup Frame
        self.signup_frame = CTkFrame(container,
                                     fg_color='white',
                                     border_color='#00117F',
                                     border_width=2,
                                     corner_radius=10)
        self.signup_frame.pack(pady=10, padx=20, fill='x', expand=True)
        
        # Logo
        logo_image = Image.open(os.path.join(BASE_DIR, 'labels', 'novus_logo1.png'))
        logo_image = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
        self.logo_photo = CTkImage(logo_image, size=(80, 80))
        logo_label = CTkLabel(self.signup_frame, image=self.logo_photo, text="")
        logo_label.pack(pady=(10, 5))


        # Create a frame to hold all form fields for better alignment
        form_fields_container = CTkFrame(self.signup_frame, fg_color='transparent', width=500)
        form_fields_container.pack(pady=10, padx=30, expand=True) # Center the container
        form_fields_container.grid_columnconfigure(1, weight=1)
        
        # Form fields
        entry_fields = [
            ("FIRST NAME:", "f_name_input"),
            ("MIDDLE NAME:", "m_name_input"), 
            ("LAST NAME:", "l_name_input"),
            ("EMAIL:", "email_input"),
            ("PHONE:", "phone_input"),
            ("USERNAME:", "username_input"),
            ("PASSWORD:", "pass_input")
        ]

        for i, (label_text, attr_name) in enumerate(entry_fields):
            CTkLabel(form_fields_container,
                    text=label_text,
                    font=('Futura', 15, 'bold'),
                    width=120,
                    anchor="e").grid(row=i, column=0, padx=(0, 10), pady=5, sticky='e')
            
            entry = CTkEntry(form_fields_container,
                           height=25,
                           width=300, # Set a fixed width for the entry
                           border_width=1,
                           border_color='black')
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='w') # Use sticky='w'
            setattr(self, attr_name, entry)

            if label_text == "PASSWORD:":
                entry.configure(show="*")

        # User Type Dropdown
        i += 1
        CTkLabel(form_fields_container,
                text="USER TYPE:",
                font=('Futura', 15, 'bold'),
                width=120,
                anchor="e").grid(row=i, column=0, padx=(0, 10), pady=5, sticky='e')
        
        self.user_type_var = tk.StringVar(value="staff")  # Default to staff
        self.user_type_dropdown = CTkComboBox(form_fields_container,
                                            variable=self.user_type_var,
                                            values=["admin", "manager", "staff"],
                                            width=300, # Set a fixed width
                                            height=25,
                                            border_width=1,
                                            corner_radius=6)
        self.user_type_dropdown.grid(row=i, column=1, padx=5, pady=5, sticky='w') # Use sticky='w'

        # Buttons
        buttons_frame = CTkFrame(self.signup_frame, fg_color='white')
        buttons_frame.pack(pady=20)
        
        CTkButton(buttons_frame,
                text='SIGN UP',
                width=120,
                height=30,
                fg_color='blue',
                command=self.add_user).pack(side="left", padx=10)
        
        CTkButton(buttons_frame,
                text='BACK',
                width=120,
                height=30,
                fg_color='blue',
                command=lambda: controller.show_frame(FrameNames.MAILS)).pack(side="left", padx=10)

    def add_user(self):
        # Default Image Path
        default_image_path = os.path.join(BASE_DIR, 'labels', 'user_logo.png')
        default_image_path = resource_path(os.path.join('labels', 'user_logo.png'))
        with open(default_image_path, 'rb') as img_file:
            default_image_data = img_file.read()
        
        # Get input values
        try:
            user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
            f_name = self.f_name_input.get()
            m_name = self.m_name_input.get()
            l_name = self.l_name_input.get()
            email = self.email_input.get()
            phone = self.phone_input.get()
            username = self.username_input.get()
            password = self.pass_input.get()
            user_type = self.user_type_var.get()
        except AttributeError as e:
            messagebox.showerror("Input Error", f"Failed to read input: {str(e)}")
            return

        # Input Validation
        validations = [
            (r"[A-Za-z ]{2,}", f_name, "First name must contain only letters and spaces"),
            (r"[A-Za-z ]*", m_name, "Middle name must contain only letters and spaces"),
            (r"[A-Za-z ]{2,}", l_name, "Last name must contain only letters and spaces"),
            (r"[^@]+@[^@]+\.[^@]+", email, "Invalid email address"),
            (r"\+?\d{10,15}", phone, "Phone must be 10-15 digits (optionally starting with +)"),
            (r"\w{4,20}", username, "Username must be 4-20 characters (letters, numbers, or _)"),
            (r"^(?=.*[A-Za-z])(?=.*\d).{8,}$", password, "Password must be at least 8 characters, with letters and numbers")
        ]

        for pattern, value, error_msg in validations:
            if not re.fullmatch(pattern, value or ""):
                messagebox.showerror("Input Error", error_msg)
                return

        if user_type not in ["admin", "manager", "staff", "supplier"]:
            messagebox.showerror("Input Error", "Invalid user type selected")
            return

        
        salt = os.urandom(16).hex()
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()

        # Default values after user entry from the fields
        user_data = (
            user_id, f_name, l_name, m_name, email, phone,
            username, hashed_password, salt, user_type, default_image_data,
            None,  # last_login
            0,     # failed_login_attempts
            0,     # account_locked
            datetime.now(pytz.timezone("Asia/Manila")).strftime('%Y-%m-%d %H:%M:%S'),  # date_created
            None,  # last_updated (will use current_timestamp)
            None,  # reset_token
            None   # reset_token_expiry
        )

        # Database Insertion
        conn = None
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            
            c.execute("""
                INSERT INTO users (
                    user_id, f_name, l_name, m_name, useremail, phonenum,
                    username, password_hash, salt, usertype, userimage,
                    last_login, failed_login_attempts, account_locked,
                    date_created, last_updated, reset_token, reset_token_expiry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user_data)

            conn.commit()


            self.send_account_to_user(email, password, user_type)

            self.clear_fields()
            messagebox.showinfo("Success", "User registered successfully!")
            self.controller.show_frame(FrameNames.MAILS)

        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                if "useremail" in str(e):
                    messagebox.showerror("Error", "Email already exists")
                elif "username" in str(e):
                    messagebox.showerror("Error", "Username already exists")
                else:
                    messagebox.showerror("Error", "User ID already exists")
            else:
                messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()

    def send_account_to_user(self, email, password, user_type):
        user_type_session = self.controller.session.get('usertype')
        user_email = self.controller.session.get('useremail')
        first = self.controller.session.get('f_name')
        last = self.controller.session.get('l_name')
        try:
            conn2 = sqlite3.connect(resource_path('main.db'))
            c2 = conn2.cursor()
            fetch_email = c2.execute(
                'SELECT f_name, m_name, l_name, username, useremail FROM users WHERE useremail = ?', (email,)
            ).fetchone()
            if not fetch_email:
                messagebox.showerror('Error', 'Account cannot be found.')
                return
            f_name, m_name, l_name_db, username, useremail_db = fetch_email
            creds = load_credentials_if_logged_in()
            if username and email:
                email_subject = f"Account Creation: Welcome To Novus {l_name_db}, {f_name}"
                email_body = (
                    f"Dear {f_name},\n\n"
                    f"We welcome you to our company.\n"
                    f"This is your account.\n\n"
                    f"Username: {username}\n\n"
                    f"Password: {password}\n\n"  # Consider removing this for security
                    f"Company Role: {user_type}\n\n"
                    f"This will be your account to use in our MRP system.\n\n"
                    f"Best Regards, \n"
                    f"{last} {first}, {user_type_session}"
                )
                try:
                    email_sent = send_email_with_attachment(creds, email, email_subject, email_body, from_email=user_email)
                    if email_sent:
                        messagebox.showinfo('Success', 'Account has been e-mailed.')
                    else:
                        messagebox.showerror('Failed', 'Email has not been sent.')
                except Exception as e:
                    messagebox.showerror('Email Error', f"Error sending email: {e}")
            else:
                messagebox.showerror('Error', 'Invalid user data for email.')
        except sqlite3.Error as e:
            messagebox.showerror('Database Error', f"Error: {e}")
        finally:
            if conn2:
                conn2.close()



    def clear_fields(self):
        """Clear all input fields after successful registration"""
        self.f_name_input.delete(0, tk.END)
        self.m_name_input.delete(0, tk.END)
        self.l_name_input.delete(0, tk.END)
        self.email_input.delete(0, tk.END)
        self.phone_input.delete(0, tk.END)
        self.username_input.delete(0, tk.END)
        self.pass_input.delete(0, tk.END)
        self.user_type_var.set("staff")  # Reset to default

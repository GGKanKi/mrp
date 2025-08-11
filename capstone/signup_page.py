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

from pages_handler import FrameNames

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        # Title
        title = CTkLabel(self, 
                        text="SIGN UP FOR INVENTORY CLERK", 
                        font=('Futura', 25, 'bold'))
        title.pack(pady=(25, 20))

        # Signup Frame
        self.signup_frame = CTkFrame(self, 
                                   fg_color='white', 
                                   border_color='#00117F', 
                                   border_width=2, 
                                   corner_radius=10,
                                   width=550)
        self.signup_frame.pack(pady=(0, 20))

        # Form fields
        entry_fields = [
            ("USER ID:", "user_id"),
            ("FIRST NAME:", "f_name_input"),
            ("MIDDLE NAME:", "m_name_input"), 
            ("LAST NAME:", "l_name_input"),
            ("EMAIL:", "email_input"),
            ("PHONE:", "phone_input"),
            ("USERNAME:", "username_input"),
            ("PASSWORD:", "pass_input")
        ]

        for label_text, attr_name in entry_fields:
            frame = CTkFrame(self.signup_frame, fg_color='white')
            frame.pack(pady=5, padx=30, fill='x')
            
            CTkLabel(frame,
                    text=label_text,
                    font=('Futura', 15, 'bold'),
                    width=120,
                    anchor="w").pack(side="left")
            
            entry = CTkEntry(frame,
                           height=25,
                           width=300,
                           border_width=1,
                           border_color='black')
            entry.pack(side="left", padx=5)
            setattr(self, attr_name, entry)

        # User Type Dropdown
        user_type_frame = CTkFrame(self.signup_frame, fg_color='white')
        user_type_frame.pack(pady=5, padx=30, fill='x')
        
        CTkLabel(user_type_frame,
                text="USER TYPE:",
                font=('Futura', 15, 'bold'),
                width=120,
                anchor="w").pack(side="left")
        
        self.user_type_var = tk.StringVar(value="staff")  # Default to staff
        self.user_type_dropdown = CTkComboBox(user_type_frame,
                                            variable=self.user_type_var,
                                            values=["admin", "manager", "staff", "supplier"],
                                            width=300,
                                            height=25,
                                            border_width=1,
                                            corner_radius=6)
        self.user_type_dropdown.pack(side="left", padx=5)

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
                command=lambda: controller.show_frame(FrameNames.LOGIN)).pack(side="left", padx=10)

    def add_user(self):
        # Default Image Path
        default_image_path = 'D:/capstone/labels/user_logo.png'
        
        # Get input values
        try:
            user_id = self.user_id.get()
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
            (r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password, "Password must be at least 8 characters, with letters and numbers")
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
            username, hashed_password, salt, user_type, default_image_path,
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
            conn = sqlite3.connect('main.db')
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
            self.clear_fields()
            messagebox.showinfo("Success", "User registered successfully!")
            self.controller.show_frame(FrameNames.LOGIN)

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

    def clear_fields(self):
        """Clear all input fields after successful registration"""
        self.user_id.delete(0, tk.END)
        self.f_name_input.delete(0, tk.END)
        self.m_name_input.delete(0, tk.END)
        self.l_name_input.delete(0, tk.END)
        self.email_input.delete(0, tk.END)
        self.phone_input.delete(0, tk.END)
        self.username_input.delete(0, tk.END)
        self.pass_input.delete(0, tk.END)
        self.user_type_var.set("staff")  # Reset to default




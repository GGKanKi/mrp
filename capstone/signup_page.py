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
import re
import uuid
import bcrypt
import pandas as pd
import os

from pages_handler import FrameNames

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        CTkLabel(self, text="SIGN UP FOR INVENTORY CLERK", font=('Futura', 25, 'bold')).place(x=420, y=25)

        self.signup_frame = CTkFrame(self, fg_color='white', border_color='#00117F', border_width=2, corner_radius=10, width=500, height=450)
        self.signup_frame.place(x=380, y=100)

        self.user_id = self._add_entry("USER ID:", 30)
        self.f_name_input = self._add_entry("FIRST NAME:", 60)
        self.m_name_input = self._add_entry("MIDDLE NAME:", 90)
        self.l_name_input = self._add_entry("LAST NAME:", 120)
        self.email_input = self._add_entry("EMAIL:", 150)
        self.phone_input = self._add_entry("PHONE:", 180)
        self.username_input = self._add_entry("USERNAME:", 210)
        self.pass_input = self._add_entry("PASSWORD:", 240)
        self.confirm_pass_input = self._add_entry("CONFIRM PASSWORD:", 270)
        self.username_type = self._add_entry("USER TYPE:", 300)

        CTkButton(self.signup_frame, text='SIGN UP', font=("Arial", 12), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.add_user).place(x=190, y=370)

        CTkButton(self.signup_frame, text='BACK', font=("Arial", 12), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black',
                  command=lambda: controller.show_frame(FrameNames.LOGIN)).place(x=190, y=405)

    def _add_entry(self, label_text, y):
        row_frame = CTkFrame(self.signup_frame, fg_color='white')
        row_frame.place(x=50, y=y)

        label = CTkLabel(row_frame, text=label_text, font=('Futura', 15, 'bold'), width=16, anchor="w")
        label.pack(side="left", padx=(0, 5))
        entry = CTkEntry(row_frame, height=20, width=250, border_width=1, border_color='black')
        entry.pack(side="left")
        return entry

    def add_user(self):
        user_id = self.user_id.get()
        f_name = self.f_name_input.get()
        m_name = self.m_name_input.get()
        l_name = self.l_name_input.get()
        email = self.email_input.get()
        phone = self.phone_input.get()
        username = self.username_input.get()
        password = self.pass_input.get()
        confirm_pass = self.confirm_pass_input.get()
        user_type = self.username_type.get()

        if not re.fullmatch(r"[A-Za-z ]{2,}", f_name):
            messagebox.showerror("Input Error", "First name must contain only letters and spaces.")
            return
        if m_name and not re.fullmatch(r"[A-Za-z ]{0,}", m_name):
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

        if confirm_pass != password:
            messagebox.showerror("Input Error", "Passwords do not match.")
            return

        if not re.fullmatch(r"[A-Za-z]{3,}", user_type):
            messagebox.showerror("Input Error", "User type must contain only letters.")
            return

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (user_id, f_name, m_name, l_name, useremail, phonenum, username, password, confirmpass, usertype)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, f_name, m_name, l_name, email, phone, username, password, confirm_pass, user_type))
            # Hash the password before storing it
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            self.controller.show_frame(FrameNames.LOGIN)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

        self.user_id.delete(0, tk.END)
        self.f_name_input.delete(0, tk.END)
        self.m_name_input.delete(0, tk.END)
        self.l_name_input.delete(0, tk.END)
        self.email_input.delete(0, tk.END)
        self.phone_input.delete(0, tk.END)
        self.username_input.delete(0, tk.END)
        self.pass_input.delete(0, tk.END)
        self.confirm_pass_input.delete(0, tk.END)
        self.username_type.delete(0, tk.END)

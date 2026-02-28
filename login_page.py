import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import time
from datetime import datetime, timedelta
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import os
import uuid
import hashlib
import bcrypt
import logging

# --- Pathing Setup ---
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))





from pages_handler import FrameNames
from global_func import get_credentials, send_email_with_attachment, load_credentials_if_logged_in, resource_path


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.option_menu = CTkFrame(self, fg_color="#00117F", height=60)
        self.option_menu.pack(side="top", fill="x", pady=(0, 10))
        # LP_NB - LOBBY PAGE NAV BAR
        self.lp_nb_btn()

        self.login_act = logging.getLogger('LOGIN_ACT')
        self.login_act.setLevel(logging.INFO)
        act_handler = logging.FileHandler(os.path.join(BASE_DIR, 'log_f', 'login.log'))
        act_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        act_handler.setFormatter(act_formatter)
        self.login_act.addHandler(act_handler)
        self.login_act.propagate = False

        self.login_warning = logging.getLogger('LOGIN_WARNING')
        self.login_warning.setLevel(logging.WARNING)
        warn_handler = logging.FileHandler(os.path.join(BASE_DIR, 'log_f', 'login.log'))
        warn_handler.setFormatter(act_formatter)
        self.login_warning.addHandler(warn_handler)
        self.login_warning.propagate = False

        self.login_error = logging.getLogger('LOGIN_ERROR')
        self.login_error.setLevel(logging.ERROR)
        err_handler = logging.FileHandler(os.path.join(BASE_DIR, 'log_f', 'login.log'))
        err_handler.setFormatter(act_formatter)
        self.login_error.addHandler(err_handler)
        self.login_error.propagate = False

        #Login Variables
        self.attempts = 0
        self.max_attempts = 3
        self.locked = False
        self.lock_time = 30
        self.end_time = 0 
        
        self.timer_label = tk.Label(self, text="", fg="red")
        self.timer_label.pack(pady=5)

    def create_label_frame(self, parent, label_text, label_font, desc_text):
        CTkLabel(parent, text=label_text, font=label_font, bg_color='transparent').pack()
        CTkLabel(parent, text=desc_text, bg_color='transparent', wraplength=800).pack()

    def lp_nb_btn(self):
        def show_frame(frame):
            # Try to hide all frames, but ignore if they don't exist
            for frame_name in ['about_frame', 'contact_frame']:
                if hasattr(self, frame_name):
                    getattr(self, frame_name).place_forget()
                    
            if frame:
                frame.place(y=100)
        def home_page():
            try:
                self.about_frame.place_forget()
                self.contact_frame.place_forget()
            except AttributeError:
                pass
            
        def about_page():
            # Create about frame if it doesn't exist
            if not hasattr(self, 'about_frame'):
                self.about_frame = CTkFrame(self, fg_color='#f0f2f5', height=600, width=1200)
                
                # --- Mission Card ---
                mission_card = CTkFrame(self.about_frame, fg_color='white', corner_radius=15, border_width=1, border_color='#dce4ee', width=900, height=250)
                mission_card.place(relx=0.5, rely=0.25, anchor='center')
                
                mission_title = CTkLabel(mission_card, text='Our Mission', font=("Roboto", 24, 'bold'), text_color='#0046FF')
                mission_title.pack(pady=(20, 10))
                
                mission_text = (
                    "To make our customers happy and satisfied with our supplies and services through our NOVUS Economical & World Class (NEW) Industry Solutions.\n\n"
                    "To phase-in state-of-the-art equipment and technologies to meet customer needs in a timely manner.\n\n"
                    "To continuously develop the organization’s engineering capabilities and skills through training and seminars that promote a higher level of excellence.\n\n"
                    "To create more jobs for other Filipino people, embracing the vision mindset as God-fearing individuals, and help build a better community within our reach."
                )
                mission_desc = CTkLabel(mission_card, text=mission_text, font=("Roboto", 13), wraplength=850, justify="left", text_color='#333333')
                mission_desc.pack(pady=(0, 20), padx=30)

                # --- Vision Card ---
                vision_card = CTkFrame(self.about_frame, fg_color='white', corner_radius=15, border_width=1, border_color='#dce4ee', width=900, height=130)
                vision_card.place(relx=0.5, rely=0.65, anchor='center')
                
                vision_title = CTkLabel(vision_card, text='Our Vision', font=("Roboto", 24, 'bold'), text_color='#0046FF')
                vision_title.pack(pady=(15, 10))
                
                vision_desc = CTkLabel(vision_card, text='To be the customer‘s preferred outsource and service provider in mind.', font=("Roboto", 16, "italic"), wraplength=800, text_color='#333333')
                vision_desc.pack(pady=(0, 20), padx=30)

            show_frame(self.about_frame)

        def contact_page():
            # Create contact frame if it doesn't exist
            if not hasattr(self, 'contact_frame'):
                self.contact_frame = CTkFrame(self, fg_color='#f0f2f5', height=600, width=1200)
                
                contact_card = CTkFrame(self.contact_frame, fg_color='white', corner_radius=15, border_width=1, border_color='#dce4ee', width=800, height=380)
                contact_card.place(relx=0.5, rely=0.40, anchor='center')

                contact_title = CTkLabel(contact_card, text='Get in Touch', font=("Roboto", 28, 'bold'), text_color='#0046FF')
                contact_title.pack(pady=(30, 15))

                contact_subtitle = CTkLabel(contact_card, text='For inquiries and system support, please reach out to us through the following channels:', font=("Roboto", 14), wraplength=700, text_color='#555555')
                contact_subtitle.pack(pady=(0, 30), padx=30)

                # Helper to create an info row
                def create_info_row(parent, icon_char, label, value):
                    row_frame = CTkFrame(parent, fg_color='transparent')
                    row_frame.pack(fill='x', padx=50, pady=10)
                    icon_label = CTkLabel(row_frame, text=icon_char, font=("Segoe UI Emoji", 20), width=30)
                    icon_label.pack(side='left')
                    label_widget = CTkLabel(row_frame, text=label, font=("Roboto", 16, 'bold'), width=150, anchor='w')
                    label_widget.pack(side='left', padx=(10, 20))
                    value_widget = CTkLabel(row_frame, text=value, font=("Roboto", 14), anchor='w', text_color='#333333')
                    value_widget.pack(side='left', fill='x', expand=True)

                # Contact details
                create_info_row(contact_card, "📞", "Phone:", "+63 992 286 5855")
                create_info_row(contact_card, "✉️", "Email:", "mheng@novus-is.com")
                create_info_row(contact_card, "📍", "Address:", "Novus Industry Solution, Sicily, Calamba, 4027 Laguna")
                create_info_row(contact_card, "💻", "Developers:", "vamorana@ccc.edu.ph | atnarvarte@ccc.edu.ph")

            show_frame(self.contact_frame)

        # --- Centered Navigation Buttons ---
        button_container = CTkFrame(self.option_menu, fg_color="transparent")
        button_container.pack(expand=True)

        home_btn = CTkButton(button_container, text='HOME', font=("Futura", 15, 'bold'), fg_color='#00117F', command=home_page)
        about_btn = CTkButton(button_container, text='ABOUT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=about_page)
        contact_btn = CTkButton(button_container, text='CONTACT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=contact_page)

        home_btn.pack(side='left', padx=20, pady=30)
        about_btn.pack(side='left', padx=20, pady=30)
        contact_btn.pack(side='left', padx=20, pady=30)



        # Clear any existing login frames to avoid overlaps
        for widget in self.winfo_children():
            if isinstance(widget, CTkFrame) and widget != self.option_menu:
                widget.destroy()
                
        # Create a centered container for the login form
        container_frame = CTkFrame(self, fg_color='white', width=1200, height=540)
        container_frame.place(x=0, y=60)
        
        # Create the main login frame with a white background and black border
        login_frame = CTkFrame(
            container_frame,
            fg_color='white',
            width=540,
            height=400,
            corner_radius=15,
            border_color='black',      # Add black border
            border_width=2             # Border thickness
        )
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Load logos
        novus_logo = Image.open(os.path.join(BASE_DIR, 'labels', 'novus_logo1.png'))
        novus_logo = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
        novus_logo = novus_logo.resize((120, 120))
        self.novus_photo = CTkImage(novus_logo, size=(120, 120))
        
        # Place logo and title INSIDE the login_frame, at the top
        CTkLabel(login_frame, image=self.novus_photo, text="").place(relx=0.5, rely=0.2, anchor='center')
        CTkLabel(
            login_frame,
            text='NOVUS INDUSTRY SOLUTIONS',
            font=('Futura', 18, 'bold'),
            text_color='#0046FF'
        ).place(relx=0.5, rely=0.4, anchor='center')
        
        # Create the form section
        form_frame = CTkFrame(login_frame, fg_color='transparent', width=400)
        form_frame.place(relx=0.5, rely=0.7, anchor='center')
        
        # Username entry
        self.username_entry = CTkEntry(
            form_frame, 
            height=40, 
            width=300,
            corner_radius=20,
            border_width=0,
            placeholder_text="Username",
            placeholder_text_color="#A0A0A0",
            fg_color="white",
            text_color="#000000"
        )
        self.username_entry.pack(pady=(0, 10))
        
        # Password entry
        self.password_entry = CTkEntry(
            form_frame, 
            height=40, 
            width=300,
            corner_radius=20,
            border_width=0,
            placeholder_text="Password",
            placeholder_text_color="#A0A0A0",
            fg_color="white",
            text_color="#000000",
            show="*"
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = CTkFrame(form_frame, fg_color='transparent')
        buttons_frame.pack(fill='x')
        
        # Login button
        self.loginbutton = CTkButton(
            buttons_frame, 
            text='LOGIN',
            font=("Futura", 14, 'bold'),
            width=360, 
            height=40, 
            fg_color='#0046FF',  # Blue for primary action
            hover_color='#2E75B6',
            corner_radius=20,
            command=self.login
        )
        self.loginbutton.pack(side='left', padx=(0, 10))
    
        
        # Forgot password link
        forgot_frame = CTkFrame(form_frame, fg_color='transparent')
        forgot_frame.pack(fill='x', pady=(10, 0))
        
        self.forgot_pass = CTkButton(
            forgot_frame, 
            text='Forgot Password?',
            font=("Futura", 12),
            fg_color='transparent', 
            hover_color='#2E75B6',
            text_color='#0046FF',  # Blue for links
            command=self.forgot_pass
        )
        self.forgot_pass.pack(side='right')
        
        # Email login option
        email_login = CTkButton(
            forgot_frame, 
            text='Email Login',
            font=("Futura", 12),
            fg_color='transparent', 
            hover_color='#2E75B6',
            text_color='#0046FF',
            command=lambda: get_credentials(self.controller)
        )
        email_login.pack(side='left')

        # --- Enter key triggers login ---
        self.bind("<Return>", lambda event: self.login())

        
    def only_owner_sign(self, title="Owner Verification"):
        self.only_owner = tk.Toplevel(self)
        self.only_owner.title("Owner Sign Up")
        self.only_owner.geometry("400x300")
        self.only_owner.grab_set()

        CTkLabel(self.only_owner, text="Owner Verification", font=("Futura", 20, 'bold')).pack(pady=20)
        CTkLabel(self.only_owner, text="PASSCODE").pack(pady=10)
        passcode_entry = CTkEntry(self.only_owner, show="*", placeholder_text="Enter Passcode", width=200)
        passcode_entry.pack(pady=10)

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            admin_pass = c.execute("SELECT * FROM users WHERE user_id = 'nickdiaz'").fetchone()

            if not admin_pass:
                messagebox.showerror("Error", "Owner passcode not found in the database.")
                self.only_owner.destroy()
                return

            # Unpack stored values
            _, _, _, _, _, _, _, password_hash, salt, _ = admin_pass[0:10]

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.only_owner.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.only_owner.destroy()
            return
        finally:
            conn.close()

        def verify_passcode():
            entered_password = passcode_entry.get()

            if password_hash.startswith('$2b$'): 
                if bcrypt.checkpw(entered_password.encode('utf-8'), password_hash.encode('utf-8')):
                    self.controller.show_frame(FrameNames.SIGNUP)
                    self.only_owner.destroy()
                else:
                    messagebox.showerror("Error", "Incorrect Passcode")
            else:
                computed_hash = hashlib.sha256((entered_password + salt).encode()).hexdigest()
                if computed_hash == password_hash:
                    self.controller.show_frame(FrameNames.SIGNUP)
                else:
                    messagebox.showerror("Error", "Incorrect Passcode")

        CTkButton(self.only_owner, text="Verify", command=verify_passcode).pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.locked:
            messagebox.showwarning("Account Locked", "Please wait before trying again.")
            return

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            self.attempts += 1
            self.login_warning.warning(
                f"Empty fields for login attempt {self.attempts}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.check_attempts()
            return

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()

            # Verify credentials - first try exact match on username
            user_search = '''SELECT * FROM users 
                            WHERE username = ? 
                            OR useremail = ?
                            ORDER BY user_id LIMIT 1'''
            login_user = c.execute(user_search, (username, username)).fetchone()

            if not login_user:
                self.attempts += 1
                self.check_attempts()
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_warning.warning(
                    f"Failed login attempt {self.attempts} for username: {username}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return

            # Unpack user data
            user_id, f_name, m_name, l_name, e_mail, number, username_db, password_hash, salt, user_type = login_user[0:10]

            # Debug log the user data (excluding sensitive info)
            self.login_act.info(f"Attempting login for user: {user_id}, email: {e_mail}")

            # Password verification
            login_ok = False
            if password_hash and password_hash.startswith('$2b$'):
                # bcrypt
                try:
                    login_ok = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
                    self.login_act.info(f"bcrypt verification result: {login_ok}")
                except Exception as e:
                    login_ok = False
                    self.login_error.error(f"bcrypt verification failed: {e}")
                    messagebox.showerror("Error", f"Password verification failed: {e}")
            else:
                # SHA256 + salt
                if salt is None:
                    salt = ""
                computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                login_ok = computed_hash == password_hash
                self.login_act.info(f"SHA256 verification result: {login_ok}")

            if not login_ok:
                self.attempts += 1
                self.check_attempts()
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_warning.warning(
                    f"Failed login attempt {self.attempts} for username: {username}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return

            # Log successful login
            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            c.execute(
                "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                (user_id, 'Login', timestamp)
            )
            c.execute('UPDATE users SET last_login = ? WHERE user_id = ?', (timestamp, user_id))
            conn.commit()
            # Log with more detailed information including email
            self.login_act.info(f"User {user_id} ({username_db}, {e_mail}) logged in at {timestamp}")

            # Success
            self.controller.login(
                user_id, f_name, m_name, l_name, e_mail, number,
                username_db, password_hash, password_hash, user_type
            )


            # Send email notification for successful login
            from global_func import send_email_with_attachment, load_credentials_if_logged_in
            creds = load_credentials_if_logged_in()
            email_sent = False
            if creds:
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                email_subject = "Login Notification"
                email_body = f"Hello {f_name} {l_name},\n\nYour account was successfully logged in at {timestamp}.\n\nIf this wasn't you, please contact the administrator immediately.\n\nRegards,\nNovus Industry Solutions"
                
                try:
                    # Make sure we're using the email address from the database for this user
                    # Use the email from the user who is logging in, not the credentials email
                    user_email = e_mail
                    # First try sending from the user's own email if available == True
                    email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body, from_email=e_mail)
                    if email_sent:
                        self.login_act.info(f"Login notification email sent to {user_email} from {e_mail}")
                    else:
                        # If sending from user email fails, try with default sender
                        email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body)
                        if email_sent:
                            self.login_act.info(f"Login notification email sent to {user_email} using default sender")
                        else:
                            self.login_warning.warning(f"Failed to send login notification email to {user_email}")
                except Exception as e:
                    self.login_error.error(f"Failed to send login notification email: {e}")

            self.attempts = 0
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

            # Show main page or settings page as needed
            self.controller.show_frame("MainMRP")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.login_error.error(
                f"Database error during login attempt {self.attempts}: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
            )
        finally:
            conn.close()

    def check_attempts(self):
        if self.attempts >= 3:  # Lock after 3 attempts
            self.lock_account()
            self.login_warning.warning(f"Account locked after {self.attempts} failed attempts, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def lock_account(self):
        self.locked = True
        self.loginbutton.configure(state=tk.DISABLED)
        self.end_time = time.time() + self.lock_time
        self.update_timer()

    def update_timer(self):
        if not self.locked:
            return
        
        remaining = int(self.end_time - time.time())
        if remaining > 0:
            self.timer_label.config(text=f"Account locked. Try again in {remaining} seconds.")
            self.after(1000, self.update_timer)  # Update every second
        else:
            self.unlock_account()
            self.login_error.error(f"Account unlocked after {self.lock_time} seconds, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def unlock_account(self):

        self.locked = False
        self.attempts = 0
        self.loginbutton.configure(state=tk.NORMAL)
        self.timer_label.config(text="")
        messagebox.showinfo("Unlocked", "You may now attempt to login again.")
        self.login_act.info(f"Account unlocked, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def forgot_pass(self, title="Forgot Password"):
        self.forgot_pass = tk.Toplevel(self)
        self.forgot_pass.title("Forgot Password")
        self.forgot_pass.geometry("400x500")
        self.forgot_pass.grab_set()

        CTkLabel(self.forgot_pass, text="Forgot Password", font=("Futura", 20, 'bold')).pack(pady=20)
        CTkLabel(self.forgot_pass, text="Enter your username or email: ").pack(pady=10)
        self.forgot_username_entry = CTkEntry(self.forgot_pass, placeholder_text="Username or Email", width=200)
        self.forgot_username_entry.pack(pady=10)

        search_acc = CTkButton(self.forgot_pass, text="Send Reset Token", command=self.reset_password)
        search_acc.pack(pady=20)
        reset_pass = CTkButton(self.forgot_pass, text="Reset Password with Token", command=lambda: [self.show_reset_password_dialog(), self.forgot_pass.destroy()]
)
        reset_pass.pack(pady=10)

    def reset_password(self):
        forgot_username = self.forgot_username_entry.get().strip()
        if not forgot_username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            # Try to find user by username or email
            fetched_user = c.execute('SELECT user_id, f_name, l_name, useremail, reset_token, reset_token_expiry FROM users WHERE username = ? OR useremail = ?', 
                                    (forgot_username, forgot_username)).fetchone()
            if not fetched_user:
                messagebox.showerror("Error", "Username or email not found in the database.")
                return
            user_id, f_name, l_name, user_email, reset_token, reset_expiry = fetched_user
            
            # Check if user has an email address
            if not user_email:
                messagebox.showerror("Error", "No email address found for this user.")
                return
                
            # Generate a new reset token and expiry time
            new_reset_token = str(uuid.uuid4())
            expiry_time = datetime.now(pytz.timezone('Asia/Manila')) + timedelta(minutes=30)
            
            # Update the user record with the new reset token and expiry
            c.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE user_id = ?', (new_reset_token, expiry_time, user_id))
            conn.commit()
            
            
            # Try to load existing credentials or get new ones
            creds = load_credentials_if_logged_in()
            email_sent = False
            
            if creds:
                email_subject = "Password Reset Token"
                email_body = f"Hello {f_name} {l_name},\n\nYou have requested to reset your password.\n\nYour reset token is: {new_reset_token}\n\nIt will expire at {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nIf you did not request this password reset, please contact the administrator immediately.\n\nRegards,\nNovus Industry Solutions"
                
                try:
                    # First try sending from the user's own email
                    email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body, from_email=user_email)
                    if email_sent:
                        messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                        self.login_act.info(f"Password reset token sent to {user_email} for user {user_id}")
                    else:
                        # If sending from user email fails, try with default sender
                        email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body)
                        if email_sent:
                            messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                            self.login_act.info(f"Password reset token sent to {user_email} for user {user_id} using default sender")
                        else:
                            raise Exception("Failed to send email with both user and default sender")
                except Exception as e:
                    # If email fails, try to refresh credentials and try again
                    try:
                        # Try to get fresh credentials
                        if os.path.exists('json_f/token.json'):
                            os.remove('json_f/token.json')
                        # Ask user if they want to try logging in with Google again
                        if messagebox.askyesno("Email Authentication", "Email sending failed. Would you like to authenticate with Google to send the reset token?"): 
                            new_creds = get_credentials(self.controller)
                            if new_creds:
                                email_sent = send_email_with_attachment(new_creds, user_email, email_subject, email_body)
                                if email_sent:
                                    messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                                    self.login_act.info(f"Password reset token sent to {user_email} for user {user_id} after credential refresh")
                    except Exception as refresh_error:
                        self.login_error.error(f"Failed to refresh credentials and send email: {refresh_error}")
            
            # If email wasn't sent successfully, show the token in a messagebox as fallback
            if not email_sent:
                messagebox.showinfo("Reset Token", f"Your reset token is: {new_reset_token}\nIt will expire at {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.login_warning.warning(f"Showing reset token in UI for user {user_id} as email sending failed")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.login_error.error(f"Database error during password reset: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.login_error.error(f"Unexpected error during password reset: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def show_reset_password_dialog(self):
        """Show dialog to reset password using token"""
        self.reset_dialog = tk.Toplevel(self)
        self.reset_dialog.title("Reset Password")
        self.reset_dialog.geometry("400x800")

        tk.Label(self.reset_dialog, text="Reset Password", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.reset_dialog, text="Username or Email:").pack()
        self.reset_username_entry = CTkEntry(self.reset_dialog, placeholder_text="Username or Email")
        self.reset_username_entry.pack(pady=5)

        tk.Label(self.reset_dialog, text="Reset Token:").pack()
        self.reset_token_entry = CTkEntry(self.reset_dialog)
        self.reset_token_entry.pack(pady=5)

        tk.Label(self.reset_dialog, text="New Password:").pack()
        self.new_password_entry = CTkEntry(self.reset_dialog, show="*")
        self.new_password_entry.pack(pady=5)

        tk.Button(self.reset_dialog, text="Submit", command=self.process_password_reset).pack(pady=10)

    def process_password_reset(self):
        """Verify token and update password"""
        user_identifier = self.reset_username_entry.get().strip()
        token = self.reset_token_entry.get().strip()
        new_password = self.new_password_entry.get().strip()

        if not all([user_identifier, token, new_password]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            c = conn.cursor()
            
            # Verify the token is valid and not expired
            current_time = datetime.now(pytz.timezone('Asia/Manila'))
            c.execute("""SELECT user_id FROM users
                WHERE (username = ? OR useremail = ?) AND reset_token = ? AND reset_token_expiry > ?
            """, (user_identifier, user_identifier, token, current_time))

            result = c.fetchone()
            if not result:
                messagebox.showerror("Error", "Invalid or expired token.")
                return

            # Generate new password hash
            salt = os.urandom(16).hex()
            hashed_pw = hashlib.sha256((new_password + salt).encode()).hexdigest()

            # Update password and clear reset token
            c.execute("""
                UPDATE users
                SET password_hash = ?, salt = ?, 
                    reset_token = NULL, reset_token_expiry = NULL
                WHERE user_id = ?
            """, (hashed_pw, salt, result[0]))

            conn.commit()
            messagebox.showinfo("Success", "Password has been reset successfully!")
            self.reset_dialog.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()
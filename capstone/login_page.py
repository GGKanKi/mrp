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
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging

from pages_handler import FrameNames


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
        act_handler = logging.FileHandler('D:/capstone/log_f/login.log')
        act_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        act_handler.setFormatter(act_formatter)
        self.login_act.addHandler(act_handler)
        self.login_act.propagate = False

        self.login_warning = logging.getLogger('LOGIN_WARNING')
        self.login_warning.setLevel(logging.WARNING)
        warn_handler = logging.FileHandler('D:/capstone/log_f/login.log')
        warn_handler.setFormatter(act_formatter)
        self.login_warning.addHandler(warn_handler)
        self.login_warning.propagate = False

        self.login_error = logging.getLogger('LOGIN_ERROR')
        self.login_error.setLevel(logging.ERROR)
        err_handler = logging.FileHandler('D:/capstone/log_f/login.log')
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
            for frame_name in ['about_frame', 'contact_frame', 'team_frame']:
                if hasattr(self, frame_name):
                    getattr(self, frame_name).place_forget()
                    
            if frame:
                frame.place(y=100)
        def home_page():
            try:
                self.about_frame.place_forget(),
                self.contact_frame.place_forget(),
                self.team_frame.place_forget()
            except AttributeError:
                pass
            
        def about_page():
            # Create about frame if it doesn't exist
            if not hasattr(self, 'about_frame'):
                self.about_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.about_box = CTkLabel(self.about_frame, bg_color='transparent', text='MISSION', font=("Futura", 20, 'bold')).place(x=570)
                self.mission = CTkFrame(self.about_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=180, width=800).place(x=210, y=30)
                self.mission_desc = CTkLabel(self.about_frame, text=
                        'TO MAKE OUR CUSTOMERS HAPPY AND SATISFIED WITH OUR SUPPLIES AND SERVICES THROUGH OUR NOVUS\n\
                        ECONOMICAL & WORLD CLASS (NEW) INDUSTRY SOLUTIONS.\n\
                    TO PHASE-IN STATE-OF-THE-ART EQUIPMENT AND TECHNOLOGIES TO MEET CUSTOMER NEEDS IN A TIMELY MANNER.\n\
                        TO CONTINUOUSLY DEVELOP THE ORGANIZATION’S ENGINEERING CAPABILITIES AND SKILLS THROUGH\n\
                        TRAINING AND SEMINARS THAT PROMOTE A HIGHER LEVEL OF EXCELLENCE.\n\
                    TO CREATE MORE JOBS FOR OTHER FILIPINO PEOPLE EMBRACING THE VISION MINDSET, AS GOD-FEARING\n\
                        INDIVIDUALS, AND HELP BUILD A BETTER COMMUNITY WITHIN OUR REACH.', bg_color='transparent', font=("Futura", 12, 'bold')).place(x=260, y=80)
                self.about_box1 = CTkLabel(self.about_frame, bg_color='transparent', text='VISION', font=("Futura", 20, 'bold')).place(x=575, y=240)
                self.vision = CTkFrame(self.about_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=180, width=800).place(x=210, y=280)
                self.vision_desc = CTkLabel(self.about_frame, text=
                                    'TO BE THE CUSTOMER‘S PREFERRED OUTSOURCE AND SERVICE PROVIDER IN MIND',
                            bg_color='transparent', font=("Futura", 15, 'bold')).place(x=295, y=350)

            show_frame(self.about_frame)

        def contact_page():
            # Create contact frame if it doesn't exist
            if not hasattr(self, 'contact_frame'):
                self.contact_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.contact_label = CTkLabel(self.contact_frame, text='CONTACT', bg_color='transparent', font=("Futura", 20, 'bold')).place(x=550)
                self.contact_box = CTkFrame(self.contact_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=350, width=800).place(x=210, y=30)
                self.contact_info = CTkLabel(self.contact_frame, text='                      For inquiries and system troubleshoot, please reach out to us through the following channels:\n\
                            Phone: +63 992 286 5855\n\
                            Email: mheng@novus-is.com\n\
                            Address: Novus Industry Solution, Sicily, Calamba, 4027 Laguna\n\
                            Developer Contact: vamorana@ccc.edu.ph & atnarvarte@ccc.edu.ph ',
      bg_color='transparent', font=("Futura", 15, 'bold')).place(x=215, y=150)

            show_frame(self.contact_frame)

        def team_page():
            if not hasattr(self, 'team_frame'):
                miss_universe = Image.open('D:/capstone/labels/jade.png')
                miss_universe = miss_universe.resize((120, 120))
                self.miss_universe_jj = CTkImage(miss_universe, size=((120, 120)))

                rhomar = Image.open('D:/capstone/labels/r.png')
                rhomar = rhomar.resize((120, 110))
                self.rhomar_pic = CTkImage(rhomar, size=((120, 110)))

                abnoy1 = Image.open('D:/capstone/labels/cd.png')
                abnoy1 = abnoy1.resize((120, 110))
                self.abnoy1_pic = CTkImage(abnoy1, size=((120, 120)))

                highlight = Image.open('D:/capstone/labels/hl.png')
                highlight = highlight.resize((120, 110))
                self.high_light = CTkImage(highlight, size=((120, 120)))

                self.team_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.team_frame.place(y=100)


                self.member1_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=0, column=0, padx=35, pady=15, sticky='nsew')
                self.member2_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=0, column=1, padx=35, pady=15, sticky='nsew')
                self.member3_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=1, column=0, padx=35, pady=15, sticky='nsew')
                self.member4_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=1, column=1, padx=35, pady=15, sticky='nsew')

                CTkLabel(self.team_frame, image=self.miss_universe_jj, text="").place(x=230, y=20)
                CTkLabel(self.team_frame, text=
                    '             JUSTINE  JADE  A.  ABRERA\n\
                jjabrera@ccc.edu.ph\n\
                DOCUMENTATION\n\
                Oversees project documentation.',justify="center",font=("Futura", 11, 'bold'), fg_color='transparent', bg_color='transparent').place(x=150, y=150)

                CTkLabel(self.team_frame, image=self.rhomar_pic, text="").place(x=850, y=20)
                CTkLabel(self.team_frame, text=
                    '                 RHOMAR  A.  LABANDILLO\n\
                ralabandilo@ccc.edu.ph\n\
                DOCUMENTATION\n\
                Responsible for Documentatio Quality',justify="center", font=("Futura", 11, 'bold'), fg_color='transparent', bg_color='transparent').place(x=750, y=150)

                CTkLabel(self.team_frame, image=self.abnoy1_pic, text="").place(x=230, y=270)
                CTkLabel(self.team_frame, text=
                '               ABCDY  ROMER  T.  NARVARTE\n\
                atnarvarte@ccc.edu.ph\n\
                DEVELOPER\n\
                Ensures product quality', font=("Futura", 11, 'bold'),justify="center", fg_color='transparent', bg_color='transparent').place(x=170, y=400)

                CTkLabel(self.team_frame, image=self.high_light, text="").place(x=840, y=270)
                CTkLabel(self.team_frame, text=
                    '              VICTOR  EMMANUEL  A.  MORANA\n\
                vamorana@ccc.edu.ph\n\
                MAIN DEVELOPER\n\
                Software development.', font=("Futura", 11, 'bold'),justify="center",fg_color='transparent', bg_color='transparent').place(x=760, y=400)

            show_frame(self.team_frame)

        CTkButton(self.option_menu, text='HOME', font=("Futura", 15, 'bold'), fg_color='#00117F', command=home_page).pack(side='left', padx=80, pady=30)
        CTkButton(self.option_menu, text='ABOUT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=about_page).pack(side='left', padx=90, pady=30)
        CTkButton(self.option_menu, text='CONTACT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=contact_page).pack(side='right', padx=90, pady=30)
        CTkButton(self.option_menu, text='TEAM', font=("Futura", 15, 'bold'), fg_color='#00117F', command=team_page).pack(side='right', padx=80, pady=30)
        # Load logos
        user_logo = Image.open('D:/capstone/labels/user_logo.png')
        user_logo = user_logo.resize((40,40))
        self.user_photo = CTkImage(user_logo, size = ((40,40)))

        pass_logo = Image.open('D:/capstone/labels/pass_logo.png')
        pass_logo = pass_logo.resize((40,40))
        self.pass_photo = CTkImage(pass_logo, size = ((40,40)))

        novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((200, 200))
        self.novus_photo = CTkImage(novus_logo, size=(200, 200))

        CTkLabel(self, image=self.novus_photo, text="").place(x=520, y=150)
        CTkLabel(self, text='NOVUS INDUSTRY SOLUTIONS', font=('Futura', 25, 'bold'), bg_color='white').place(x=440, y=390)

        CTkLabel(self, image=self.user_photo, text="").place(x=490, y=430)
        self.username_entry = CTkEntry(self, height=35, width=200, border_width=2, border_color='black')
        self.username_entry.place(x=535, y=430)

        CTkLabel(self, image=self.pass_photo, text="").place(x=490, y=470)
        self.password_entry = CTkEntry(self, height=35, width=200, show="*", border_width=2, border_color='black')
        self.password_entry.place(x=535, y=470)

        self.loginbutton = CTkButton(self, text='LOGIN', font=("futura", 12, 'bold'), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.login)
        self.loginbutton.place(x=560, y=510)

        self.bind("<Return>", lambda event: self.login())

        CTkButton(self, text='SIGN UP', font=("futura", 12, 'bold'), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.only_owner_sign).place(x=560, y=545)
        
    
    def only_owner_sign(self, title = "Owner Verification"):
        self.only_owner = tk.Toplevel(self)
        self.only_owner.title("Owner Sign Up")
        self.only_owner.geometry("400x300")
        self.only_owner.grab_set()

        CTkLabel(self.only_owner, text="Owner Verification", font=("Futura", 20, 'bold')).pack(pady=20)
        CTkLabel(self.only_owner, text="PASSCODE").pack(pady=10)
        self.passcode_entry = CTkEntry(self.only_owner, show="*", placeholder_text="Enter Passcode", width=200)
        self.passcode_entry.pack(pady=10)

        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE user_id = 'a'")
        owner_pass = c.fetchone()
        conn.close()

        CTkButton(self.only_owner, text="Verify", command = lambda: self.controller.show_frame(FrameNames.SIGNUP) if self.passcode_entry.get() == owner_pass[0] else messagebox.showerror("Error", "Incorrect Passcode")
).pack(pady=20)


    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.locked:
            messagebox.showwarning("Account Locked", "Please wait before trying again.")
            return

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            self.attempts += 1
            print(f"DEBUG: Empty fields. Attempts={self.attempts}")
            self.login_warning.warning(f"Empty fields for login attempt {self.attempts}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
            self.check_attempts()
            return

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            # Verify credentials
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()

            if user:
                # Unpack user data (adjust indices to match your DB schema)
                # Example: (user_id, f_name, m_name, l_name, e_mail, number, username, password, confirm_pass, user_type)
                user_id = user[0]
                f_name = user[1]
                m_name = user[2]
                l_name = user[3]
                e_mail = user[4]
                number = user[5]
                username_db = user[6]
                password_db = user[7]
                confirm_pass = user[8]
                user_type = user[9]

                # Store in session using your controller's login method
                self.controller.login(
                    user_id, f_name, m_name, l_name, e_mail, number,
                    username_db, password_db, confirm_pass, user_type
                )

                self.attempts = 0  # Reset attempts on success
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)

                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                        (user_id, 'Login', timestamp))
                conn.commit()
                self.login_act.info(f"User {user_id} logged in at {timestamp}")

                
                # Check inventory after successful login/Notification
                c.execute('SELECT mat_id, mat_name, mat_volume FROM raw_mats')
                all_items = c.fetchall()
                low_items = [(id, name, vol) for id, name, vol in all_items if vol < 100]

                if low_items:
                    item_list = "\n".join([f"{name} (ID: {id}): {vol} units" for id, name, vol in low_items])
                    messagebox.showwarning(
                        'Low Volume Warning',
                        f'There are {len(low_items)} items with low volume:\n\n{item_list}'
                    )

                # Show main page or settings page as needed
                self.controller.show_frame("MainMRP")

            else:
                self.attempts += 1
                self.check_attempts()
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_warning.warning(f"Failed login attempt {self.attempts} for username: {username}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.login_error.error(f"Database error during login attempt {self.attempts}: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
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
        print("DEBUG: Unlocking account")
        self.locked = False
        self.attempts = 0
        self.loginbutton.configure(state=tk.NORMAL)
        self.timer_label.config(text="")
        messagebox.showinfo("Unlocked", "You may now attempt to login again.")
        self.login_act.info(f"Account unlocked, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
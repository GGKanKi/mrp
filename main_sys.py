import tkinter as tk
from tkinter import messagebox
import customtkinter
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import threading
import os
import logging
import sqlite3
import pytz
from datetime import datetime
import sys 
from pages_handler import FrameNames
from database import DatabaseManager
from global_func import center_window, resource_path


log_dir = resource_path('log_f')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=resource_path(os.path.join('log_f', 'app.log')), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import ssl
import certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# Override Toplevel to automatically center windows
original_toplevel = tk.Toplevel
class CenteredToplevel(original_toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wait for the window to be fully created before centering
        self.after(10, lambda: center_window(self))
tk.Toplevel = CenteredToplevel

# Override messagebox functions to center them
original_showinfo = messagebox.showinfo
original_showerror = messagebox.showerror
original_showwarning = messagebox.showwarning
original_askyesno = messagebox.askyesno
original_askokcancel = messagebox.askokcancel

def centered_messagebox(original_func, *args, **kwargs):
    result = original_func(*args, **kwargs)
    # Find and center the messagebox
    for window in tk._default_root.winfo_children():
        if isinstance(window, tk.Toplevel) and window.winfo_class() == 'TkToplevel':
            center_window(window)
    return result

messagebox.showinfo = lambda *args, **kwargs: centered_messagebox(original_showinfo, *args, **kwargs)
messagebox.showerror = lambda *args, **kwargs: centered_messagebox(original_showerror, *args, **kwargs)
messagebox.showwarning = lambda *args, **kwargs: centered_messagebox(original_showwarning, *args, **kwargs)
messagebox.askyesno = lambda *args, **kwargs: centered_messagebox(original_askyesno, *args, **kwargs)
messagebox.askokcancel = lambda *args, **kwargs: centered_messagebox(original_askokcancel, *args, **kwargs)

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)  # Borderless window
        self.attributes('-topmost', True)

        width, height = 500, 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # UI Elements
        splash_frame = customtkinter.CTkFrame(self, fg_color="#00117F", corner_radius=15)
        splash_frame.pack(fill="both", expand=True)

        # Cancel button
        cancel_btn = customtkinter.CTkButton(
            splash_frame,
            text="X",
            width=25,
            height=25,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=parent.destroy)
        cancel_btn.place(relx=0.95, rely=0.05, anchor='ne')

        logo_image = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
        self.logo_photo = CTkImage(logo_image, size=(150, 150))

        customtkinter.CTkLabel(splash_frame, image=self.logo_photo, text="").pack(pady=(30, 10))
        customtkinter.CTkLabel(splash_frame, text="NOVUS INDUSTRY SOLUTIONS", font=('Futura', 20, 'bold'), text_color='white').pack()

        self.status_label = customtkinter.CTkLabel(splash_frame, text="Initializing system...", font=('Futura', 12), text_color='#d3d3d3')
        self.status_label.pack(pady=(20, 5))

        self.progress = customtkinter.CTkProgressBar(splash_frame, width=300, height=10, corner_radius=5, progress_color="#6a9bc3")
        self.progress.set(0)
        self.progress.pack(pady=10)

    def update_status(self, text, value):
        self.status_label.configure(text=text)
        self.progress.set(value)
        self.update_idletasks()

class LoginSuccessMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        label = tk.Label(main_frame, text=message, wraplength=300, justify="center", font=("Futura", 12))
        label.pack(pady=(0, 20), expand=True)

        ok_button = CTkButton(main_frame, text="OK", command=self.destroy, width=100)
        ok_button.pack(pady=(0, 10))

        self.after(10, lambda: center_window(self))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)




class NovusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide main window initially
        self.splash = SplashScreen(self)
        self.session = {}
        self.db_manager = DatabaseManager(session=self.session)
        self._setup_ui()
        self._initialize_frames()
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def login(self, user_id, f_name, m_name, l_name, e_mail, number, username, password, confirm_pass, user_type):
        """Store user session data"""
        self.session['user_id'] = user_id
        self.session['f_name'] = f_name
        self.session['m_name'] = m_name
        self.session['l_name'] = l_name
        self.session['useremail'] = e_mail
        self.session['phonenum'] = number
        self.session['username'] = username
        self.session['password_hash'] = password
        self.session['confirm_pass'] = confirm_pass
        self.session['usertype'] = user_type

        # Determine the name to display in the welcome message
        welcome_name = f_name if f_name else username
        if e_mail and not f_name: # If it's an email login without a first name, try to use the name part of the email
            welcome_name = e_mail.split('@')[0]
        LoginSuccessMessageBox(self, "Login Successful", f"Welcome, {welcome_name}!")

    def _setup_ui(self):
        self.title("NOVUS INDUSTRY SOLUTIONS INVENTORY")
        self.geometry("1200x600")
        
        self.config(bg='white')
        self.resizable(False, False)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)    
        self.frames = {}
        self.after(10, lambda: center_window(self))

    def _initialize_frames(self):
        """Lazy import frames to prevent circular imports"""
        from audit_crud import AuditsPage
        from clients_crud import ClientsPage
        from order_crud import OrdersPage
        from inventory_crud import InventoryPage
        from product_crud import ProductsPage
        from supplier_crud import SuppliersPage
        from user_sets import UserSet
        from mails import MessagesPage
        from login_page import LoginPage
        from home_mrp import MainMRP
        from signup_page import SignupPage

        frame_classes = {
            FrameNames.CLIENTS: ClientsPage,
            FrameNames.ORDERS: OrdersPage,
            FrameNames.PRODUCTS: ProductsPage,
            FrameNames.INVENTORY: InventoryPage,
            FrameNames.SUPPLIERS: SuppliersPage,
            FrameNames.SETTINGS: UserSet,
            FrameNames.MAILS: MessagesPage,
            FrameNames.AUDITS: AuditsPage,
            FrameNames.MAIN_MRP: MainMRP,
            FrameNames.SIGNUP: SignupPage,
            FrameNames.LOGIN: LoginPage
        }

        login_frame = LoginPage(parent=self.container, controller=self)
        self.frames[FrameNames.LOGIN] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")
        threading.Thread(target=self._load_other_frames, args=(frame_classes,), daemon=True).start()
        self.show_frame(FrameNames.LOGIN)

    def _load_other_frames(self, frame_classes):
        """Load other frames in the background"""
        for frame_name, frame_class in frame_classes.items():
            if frame_name == FrameNames.LOGIN:
                continue
            
            self.splash.update_status(f"Loading {frame_name}...", (len(self.frames) / len(frame_classes)))
            frame = frame_class(parent=self.container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.splash.update_status("Loading complete!", 1.0)
        self.after(500, self.show_main_app)

    def show_main_app(self):
        self.splash.destroy()
        self.deiconify() # Show the main window
        self.show_frame(FrameNames.LOGIN) # Show the login frame


    def show_frame(self, page_name):
        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
            if hasattr(frame, 'on_show'):
                frame.on_show()
                
    def refresh_all_frames(self):
        """Refresh all frames in the application to reflect the latest database changes"""
        # Update database connection to ensure fresh data
        if hasattr(self.db_manager, 'refresh_connection'):
            self.db_manager.refresh_connection()
        else:
            # Recreate database manager if refresh method doesn't exist
            self.db_manager = DatabaseManager(session=self.session)
        
        # Refresh each frame if it has a refresh method
        for frame_name, frame in self.frames.items():
            # Skip login frame
            if frame_name == FrameNames.LOGIN:
                continue
                
            # Call frame-specific refresh methods if they exist
            if hasattr(frame, 'refresh_dashboard') and callable(frame.refresh_dashboard):
                frame.refresh_dashboard()
            elif hasattr(frame, 'load_data') and callable(frame.load_data):
                frame.load_data()
            elif hasattr(frame, 'refresh') and callable(frame.refresh):
                frame.refresh()
            elif hasattr(frame, 'on_show'):
                frame.on_show()


    def _on_app_close(self):
        confirm = messagebox.askokcancel("Quit", "Do you want to quit?")
        conn = None
        
        if confirm:
            try:
                """Handle user logout and log the action."""
                self.logout_info = logging.getLogger('logout_info')
                self.logout_info.setLevel(logging.INFO)

                if not self.logout_info.handlers:
                    logout_handler = logging.FileHandler(resource_path(os.path.join('log_f', 'login.log')))
                    logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    logout_handler.setFormatter(logout_formatter)
                    self.logout_info.addHandler(logout_handler)

                # Get user information for logging
                user_id = self.session.get('user_id')
                username = self.session.get('username')
                email = self.session.get('useremail')
                
                # Log the logout with more detailed information
                if email and username:
                    # For users who logged in with email
                    self.logout_info.info(f"User {user_id} ({username}, {email}) logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    # For regular users
                    self.logout_info.info(f"User {user_id} logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

                # Log to DB
                if user_id:
                    conn = sqlite3.connect(resource_path('main.db'))
                    c = conn.cursor()
                    timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                    c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, 'Logout', timestamp))
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during logout: {e}")
            finally:
                if conn:
                    conn.close()
                self.destroy()
        else:
            return


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = NovusApp()
    app.mainloop()
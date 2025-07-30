import tkinter as tk
from tkinter import messagebox
import customtkinter
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import multiprocessing
import threading
import os

    
from pages_handler import FrameNames

class NovusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.session = {}
        self._setup_ui()
        self._initialize_frames()

    def login(self, user_id, f_name, m_name, l_name, e_mail, number, username, password, confirm_pass, user_type):
        """Store user session data"""
        self.session['user_id'] = user_id
        self.session['f_name'] = f_name
        self.session['m_name'] = m_name
        self.session['l_name'] = l_name
        self.session['e_mail'] = e_mail
        self.session['number'] = number
        self.session['username'] = username
        self.session['password'] = password
        self.session['confirm_pass'] = confirm_pass
        self.session['user_type'] = user_type
        messagebox.showinfo(f"User {user_id}, {username} logged in as {user_type}")
        
    def _setup_ui(self):
        self.title("NOVUS INDUSTRY SOLUTIONS INVENTORY")
        self.geometry("1200x600")
        self.iconbitmap('D:/capstone/labels/novus_logo1.png')
        self.config(bg='white')
        self.resizable(False, False)
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
    
    def _initialize_frames(self):
        """Lazy import frames to prevent circular imports"""
        from clients_crud import ClientsPage
        from prod_crud import ProductPage
        from order_crud import OrdersPage
        from inventory_crud import InventoryPage
        from supplier_crud import SuppliersPage
        from user_sets import UserSet
        from mails import MessagesPage
        from login_page import LoginPage
        from user_log import LogsPage
        from home_mrp import MainMRP
        from signup_page import SignupPage

        frame_classes = {
            FrameNames.CLIENTS: ClientsPage,
            FrameNames.LOGS: LogsPage,
            FrameNames.PRODUCTS: ProductPage,
            FrameNames.ORDERS: OrdersPage,
            FrameNames.INVENTORY: InventoryPage,
            FrameNames.SUPPLIERS: SuppliersPage,
            FrameNames.SETTINGS: UserSet,
            FrameNames.MAILS: MessagesPage,
            FrameNames.MAIN_MRP: MainMRP,
            FrameNames.SIGNUP: SignupPage,
            FrameNames.LOGIN: LoginPage
            #Add Another Frame For User Settings
        }


        login_frame = LoginPage(parent=self.container, controller=self)
        self.frames[FrameNames.LOGIN] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        threading.Thread(target=self._load_other_frames, args=(frame_classes,), daemon=True).start()
        
        self.show_frame(FrameNames.LOGIN)

    def _load_other_frames(self, frame_classes):
        """Load other frames in the background"""
        for frame_name, frame_class in frame_classes.items():
            if frame_name != FrameNames.LOGIN:
                frame = frame_class(parent=self.container, controller=self)
                self.frames[frame_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
        
        # Show the login frame first
        self.show_frame(FrameNames.LOGIN)

    def show_frame(self, page_name):
        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
            if hasattr(frame, 'on_show'):
                frame.on_show()  
        else:
            available = "\n".join(self.frames.keys())
            messagebox.showerror(
                "Navigation Error",
                f"Frame '{page_name}'   t found.\n\nAvailable frames:\n{available}"
            )

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = NovusApp()
    app.mainloop()



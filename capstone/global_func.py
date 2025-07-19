from pages_handler import FrameNames
import sqlite3
import pytz
from datetime import datetime
import logging
import os
import sys
from customtkinter import CTkImage, CTkButton, CTkFrame
from PIL import Image


def on_show(self):
    for widget in self.main.winfo_children():
        widget.destroy()

    user_type = self.controller.session.get('user_type', '')
    print("DEBUG (on_show): user_type =", user_type)

    self.mrp_main = self._main_buttons(self.main, self.mrp_btn, 'MRP', command=lambda: self.controller.show_frame(FrameNames.MAIN_MRP))

    if user_type == "admin" or user_type == "owner":
        self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
        self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        self.user_logs_main = self._main_buttons(self.main, self.user_logs_btn, 'User Logs', command=lambda: self.controller.show_frame(FrameNames.LOGS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))

    elif user_type == "clerk" or user_type == "manager":
        self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
        self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))

    elif user_type == "employee":
        self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))


    self.settings_main = self._main_buttons(self.main, self.settings_btn, 'Settings', command=lambda: self.controller.show_frame(FrameNames.SETTINGS))
    self.logout_main = self._main_buttons(self.main, self.logout_btn,  'Logout', command=self.handle_logout)

def handle_logout(self):
    """Handle user logout and log the action."""
    # Log the logout action
    self.logout_info = logging.getLogger('logout_info')
    self.logout_info.setLevel(logging.INFO)
    logout_handler = logging.FileHandler('login.txt')
    logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logout_handler.setFormatter(logout_formatter)
    self.logout_info.addHandler(logout_handler)

    self.logout_info.info(f"User {self.controller.session.get('user_id')} logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
    
    user_id = self.controller.session.get('user_id')
    if user_id:
        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, 'Logout', timestamp))
        print('DEBUG: User logged out:', user_id, timestamp)
        conn.commit()
        conn.close()
    self.controller.show_frame(FrameNames.LOGIN)
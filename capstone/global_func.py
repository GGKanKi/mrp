from pages_handler import FrameNames
import sqlite3
import pytz
import re
from datetime import datetime
import logging
import os
import sys
import threading
from customtkinter import CTkImage, CTkButton, CTkFrame
from tkinter import messagebox
from PIL import Image
import re


#Data Imports
import json

#Import Functions

def on_show(self):
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
    self.logout_info = logging.getLogger('logout_info')
    self.logout_info.setLevel(logging.INFO)

    if not self.logout_info.handlers:
        logout_handler = logging.FileHandler('D:/capstone/log_f/login.log')
        logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logout_handler.setFormatter(logout_formatter)
        self.logout_info.addHandler(logout_handler)

    # Log the logout
    self.logout_info.info(f"User {self.controller.session.get('user_id')} logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    # Log to DB
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



def export_materials_to_json(db_path: str, output_file: str) -> None:
    """Exports product materials to JSON in a background thread."""

    def _export_thread():
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT product_id, product_name, materials FROM products")
                rows = cursor.fetchall()

            export_data = []

            for product_id, product_name, materials in rows:
                if materials:
                    try:
                        materials_dict = json.loads(materials)
                    except json.JSONDecodeError:
                        materials_dict = {}
                        for item in re.split(r'[;,]', materials):
                            parts = item.strip().split('-')
                            if len(parts) == 2:
                                name = parts[0].strip()
                                try:
                                    qty = int(parts[1].strip())
                                    materials_dict[name] = qty
                                except ValueError:
                                    continue
                        if not materials_dict:
                            materials_dict = {"raw": materials}
                else:
                    materials_dict = {}

                export_data.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "materials": materials_dict
                })

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=4)

            logging.info(f"✅ Exported {len(export_data)} products to {output_file}")
        except Exception as e:
            logging.error(f"❌ Export failed: {e}")

    # Start the export in a background thread
    thread = threading.Thread(target=_export_thread)
    thread.start()



#Create a JSON Decoder for Total Materials Needed  = Finish the New SCHEMA first
def export_total_amount_mats(db_path: str, output_file: str) -> None:
    """Exports product materials to JSON in a background thread."""

    def export_thread():
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT order_id, order_name, mats_need from orders")
                rows = c.fetchall()

            export_data = []

            for order_id, order_name, ttl_mats in rows:
                if ttl_mats:
                    try:
                        ttl_mats_dict = json.loads(ttl_mats)
                    except json.JSONDecodeError:
                        ttl_mats_dict = {}
                        for item in re.split(r'[;,]', ttl_mats):
                            parts = item.strip().split('-')
                            if len(parts) == 2:
                                name = parts[0].strip()
                                try:
                                    qty = int(parts[1].strip())
                                    ttl_mats_dict[name] = qty
                                except ValueError:
                                    continue
                        if not ttl_mats_dict:
                            ttl_mats_dict = {"raw": ttl_mats}
                else:
                    ttl_mats_dict = {}

                export_data.append({
                    'order_id': order_id,
                    'order_name': order_name,
                    'mats_need': ttl_mats_dict
                })

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=4)
                        
            logging.info(f"✅ Exported {len(export_data)} products to {output_file}")
        except Exception as e:
            logging.error(f"❌ Export failed: {e}")

    # Start the export in a background thread
    thread = threading.Thread(target=export_thread, daemon=True)
    thread.start()






    



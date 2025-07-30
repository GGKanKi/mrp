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
import pandas as pd
import os
import sys
sys.path.append("D:/capstone")

#File imports
from pages_handler import FrameNames
from global_func import on_show, handle_logout


class ProductPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))  # Sticks to the left, fills Y
            parent.pack_propagate(False)

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))  # Sticks to the top, fills X

            novus_logo = Image.open('D:/capstone/labels/novus_logo1.png')
            novus_logo = novus_logo.resize((50, 50))
            self.novus_photo = CTkImage(novus_logo, size=(50, 50))

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



            #Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left",anchor="n", padx=(15, 20), ipadx=100)

            # Add Approve, Cancel for Status
            '''            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2',command=self.srch_order)
                        self.add_btn = self.add_del_upd('ADD ORDER', '#2ecc71', command=self.add_orders)
                        self.approve_order_btn = self.add_del_upd('APPROVE ORDER', '#27ae60',command=self.approve_order)
                        self.cancel_order_btn = self.add_del_upd('CANCEL ORDER', '#95a5a6', command=self.cancel_order)
                        self.del_btn = self.add_del_upd('DELETE ORDER', '#e74c3c', command=self.del_order)
                        self.excel_btn = self.add_del_upd('UPDATE ORDER', '#f39c12', command=self.upd_order)'''

            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=120, y=105, width=1100, height=475)

            self.order_tree = ttk.Treeview(        
            tree_frame,
                columns=('order_id', 'order_name', 'product_id', 'order_date', 
                        'order_dl', 'order_amount', 'client_id', 'status_quo'),
                show='headings',
                style='Treeview'
            )
            self.order_tree.bind("<Double-1>", self.show_materials_popup)


            # Configure column headings (assuming _column_heads does this)
            self._column_heads('order_id', 'ORDER ID')
            self._column_heads('order_name', 'ORDER NAME')
            self._column_heads('product_id', 'PRODUCT')
            self._column_heads('order_date', 'ORDER DATE')
            self._column_heads('order_dl', 'DEADLINE')
            self._column_heads('order_amount', 'VOLUME')
            self._column_heads('client_id', 'CLIENT ID')
            self._column_heads('status_quo', 'STATUS')

            # Configure column widths and stretching
            for col in self.order_tree['columns']:
                self.order_tree.column(col, width=300, stretch=False)  # Disable stretch for proper scrolling

            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.order_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.order_tree.xview)
            self.order_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.order_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Configure weight for proper resizing
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)







    def show_materials_popup(self, event):
        selected = self.order_tree.focus()
        if not selected:
            return
        values = self.order_tree.item(selected, 'values')
        mats_used = values[6]  # Assuming 'mats_used' is the 7th column
        popup = tk.Toplevel(self)
        popup.title("Materials Used")
        popup.geometry("400x300")
        txt = tk.Text(popup, wrap="word", state="normal")
        txt.insert("1.0", mats_used)
        txt.configure(state="disabled")
        txt.pack(expand=True, fill="both", padx=10, pady=10)

    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, fg_color=fg_color, width=80, command=command)
        button.pack(side="left", anchor="n", padx=5)

    def _column_heads(self, columns, text):
        self.order_tree.heading(columns, text=text)
        self.order_tree.column(columns, width=175)
        if text == 'MATERIALS':
            self.order_tree.column(columns, width=100)

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

    def _add_order(self, label_text, y):

        label = CTkLabel(self.add_order, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.add_order, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self) 
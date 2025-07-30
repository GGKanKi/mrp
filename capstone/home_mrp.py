import tkinter as tk
from tkcalendar import Calendar
import time
from datetime import datetime
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
import sys
sys.path.append('D:/capstone')


from pages_handler import FrameNames
from global_func import on_show, handle_logout

class MainMRP(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')
        
        # Main UI setup (your existing code)
        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y")
        parent.pack_propagate(False)

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 5))  # Sticks to the top, fills X

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

        self.notification_dash = self.db_frames(label_name='LOW MATERIAL COUNT',button_name='CHECK ITEMS',command=self.refresh_low_items)  
        self.deadline_dash = self.db_frames(label_name='DEADLINES',button_name='CHECK DEADLINES',command=self.refresh_low_items)  
        self.notifs_dash = self.db_frames(label_name='NOTIFICATIONS',button_name='CHECK NOTIFICATIONS',command=self.refresh_low_items)  



    def db_frames(self, label_name, button_name, command=None):
        # Main container frame that will help with centering
        container = CTkFrame(self, fg_color='transparent')
        container.pack(expand=True, fill='both', pady=10)
        
        # Your styled frame
        db_boxes = CTkFrame(container, fg_color='#f8f9fa', border_color='#dee2e6', border_width=1.5, height=300, width=260, corner_radius=10)
        db_boxes.pack(expand=True)  # This centers the frame in its container
        
        # Content inside the frame
        boxes_label = CTkLabel(db_boxes, text=label_name, font=('Arial', 14, 'bold'), text_color='#343a40')
        boxes_label.pack(pady=(20, 10))  # More top padding
        
        separator = CTkFrame(db_boxes, height=2, fg_color='#e9ecef', border_width=0)
        separator.pack(fill='x', padx=20, pady=5)
        
        # Button with centered alignment
        boxes_btn = CTkButton(db_boxes, text=button_name, border_color='#adb5bd', border_width=1, 
                            width=120, height=45, corner_radius=8, fg_color='#ffffff', 
                            hover_color='#f1f3f5', text_color='#495057', 
                            font=('Arial', 12, 'bold'), command=command)
        boxes_btn.pack(pady=20)
        
        return container  # Return the container instead of just db_boxes
    
    def refresh_low_items(self):
        # Create or focus the low inventory window
        if not hasattr(self, 'low_inv_window') or not self.low_inv_window.winfo_exists():
            self.low_inv_window = tk.Toplevel(self)  # Key fix: Use self as parent
            self.low_inv_window.title("Low Inventory Management")
            self.low_inv_window.geometry("650x450")
            
            # Configure window close behavior
            self.low_inv_window.protocol("WM_DELETE_WINDOW", self._close_low_inv_window)
            
            # Main container using pack
            self.low_inv_container = CTkFrame(self.low_inv_window)
            self.low_inv_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Header
            self.header_label = CTkLabel(self.low_inv_container, 
                                    text="Loading low inventory items...",
                                    font=('Arial', 14, 'bold'))
            self.header_label.pack(pady=(0, 10))
            
            # Create scrollable area
            self._setup_scrollable_area()
        else:
            self.low_inv_window.lift()  # Bring to front if already exists
        
        # Load and display data
        self._load_and_display_items()

    def _setup_scrollable_area(self):
        """Create the scrollable canvas area for items"""
        self.canvas_frame = tk.Frame(self.low_inv_container)
        self.canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.items_frame = tk.Frame(self.canvas)
        
        self.items_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas.create_window((0, 0), window=self.items_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

    def _load_and_display_items(self):
        """Load data from DB and display in the window"""
        try:
            # Clear previous items
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            
            # Get data from database
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute('SELECT mat_id, mat_name, mat_volume, supplier_id FROM raw_mats')
            low_items = [row for row in cursor.fetchall() if row[2] < 100]
            conn.close()
            
            # Update header
            self.header_label.configure(
                text=f"{len(low_items)} Low Volume Items (Volume < Unit of Measurement)",
                text_color='red' if low_items else 'green'
            )
            
            if low_items:
                # Create column headers
                headers = tk.Frame(self.items_frame)
                headers.pack(fill='x', pady=(0, 5))
                
                CTkLabel(headers, text="ID", width=10, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Material Name", width=25, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Supplier", width=20, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Stock", width=15, font=('Arial', 12, 'bold')).pack(side='right', padx=5)
                
                # Add items
                for mat_id, name, vol, supplier in low_items:
                    item = tk.Frame(self.items_frame)
                    item.pack(fill='x', pady=2)
                    
                    CTkLabel(item, text=mat_id, width=10).pack(side='left', padx=5)
                    CTkLabel(item, text=name, width=25).pack(side='left', padx=5)
                    CTkLabel(item, text=supplier, width=20).pack(side='left', padx=5)
                    CTkLabel(item, text=f"{vol} units", text_color='red', width=15).pack(side='right', padx=5)
                    CTkButton(item, text="Edit", width=50,
                            command=lambda m=mat_id: self.open_edit_window(m)).pack(side='right', padx=5)
            else:
                CTkLabel(self.items_frame, 
                    text="All items are properly stocked (≥100 units)",
                    font=('Arial', 14),
                    text_color='green').pack(pady=20)
            
            # Schedule next refresh if window still exists
            if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
                self.low_inv_window.after(5000, self.refresh_low_items)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {str(e)}")

    def _close_low_inv_window(self):
        """Properly clean up the low inventory window"""
        if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
            # Cancel any pending refresh
            self.low_inv_window.after_cancel(self.refresh_low_items)
            self.low_inv_window.destroy()

    def open_edit_window(self, material_id):
        # Placeholder for your edit window function
        print(f"Editing material with ID: {material_id}")
        # Add your edit window implementation here

    def _calendar(self):
        calendar_frame = CTkFrame(self, fg_color='white',  border_color='black',  border_width=1, height=250, width=240)
        calendar_frame.pack(side='left', anchor='n', padx=5, pady=5)
        
        # Set Manila timezone
        self.manila_tz = pytz.timezone('Asia/Manila')
        
        # Time display
        self.time_label = CTkLabel(calendar_frame,text="",font=('Helvetica', 20),text_color='blue')
        self.time_label.pack(pady=(10, 0))
        
        # Date display
        self.date_label = CTkLabel(calendar_frame,text="",font=('Helvetica', 14),text_color='black')
        self.date_label.pack()
        
        # Calendar widget from tkcalendar
        self.calendar = Calendar(calendar_frame,selectmode='day', font=('Helvetica', 10), background='white', foreground='black',
            selectbackground='red', normalbackground='white', bordercolor='black', headersbackground='#f0f0f0' )
        self.calendar.pack(pady=10, padx=5, fill='both', expand=True)
        self._update_calendar_time()
        return calendar_frame

    def _update_calendar_time(self):
        # Get current Manila time
        now = datetime.now(self.manila_tz)
        
        # Update time display (e.g., "14:30:45")
        self.time_label.configure(text=now.strftime("%H:%M:%S"))
        
        # Update date display (e.g., "Monday, June 5, 2023")
        self.date_label.configure(text=now.strftime("%A, %B %d, %Y"))
        
        # Update calendar selection
        self.calendar.selection_set(now.date())
        
        # Schedule next update in 1 second
        self.after(1000, self._update_calendar_time)
        
    def _low_items(self):
        low_item_frame = CTkFrame(self, fg_color='white', border_color='black', border_width=1, height=270, width=600)
        low_item_frame.pack(side='left', anchor='n', padx=5, pady=5)

        # Create container for dynamic content
        self.content_container = tk.Frame(low_item_frame, bg='white')
        self.content_container.pack(fill='both', expand=True)

        # Initial load
        self._refresh_low_items()

    def _refresh_low_items(self):
        pass
            
    def _deadlines(self):
        dl_frame = CTkFrame(self, fg_color='white', border_color='black', border_width=1, height=270, width=600)
        dl_frame.place(relx = 0.27, rely = 0.54)

        # Create container for dynamic content
        self.dl_container = tk.Frame(dl_frame, bg='white')
        self.dl_container.pack(fill='both', expand=True)

        self._dl_report_refresh()

    def _dl_report_refresh(self):

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            today = datetime.today().date()
            today_str = today.strftime("%Y-%m-%d")

            c.execute("SELECT order_id, order_name, order_dl FROM orders") 
            all_orders = c.fetchall()  

            dl_info = [(ord_id, ord_name, ord_dl) for ord_id, ord_name, ord_dl in all_orders if ord_dl == today_str]

            for widget in self.dl_container.winfo_children():
                widget.destroy()

            tk.Label(self.dl_container, 
            text=f"{len(dl_info)} Deadline(s) Today", 
            font=('Arial', 9), bg='white', fg='red').pack(anchor='n', pady=(0, 15))

            canvas = tk.Canvas(self.dl_container, bg='white', 
                            highlightthickness=0, height=180, width=450)
            scrollbar = tk.Scrollbar(self.dl_container, orient='vertical', command=canvas.yview, width=5, bg='#404040', troughcolor='#e0e0e0')
            scroll_frame = tk.Frame(canvas, bg='white')
            scroll_frame.bind('<Configure>', lambda e: canvas.configure(
                scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            if dl_info:
                for ord_id, ord_name, ord_dl in dl_info:
                        item_frame = tk.Frame(scroll_frame, bg='white')
                        item_frame.pack(fill='x', pady=2)
                        
                        tk.Label(item_frame, text=ord_id, bg='white', anchor='w', width=15).pack(side='left')
                        tk.Label(item_frame, text=ord_name, bg='white', anchor='w', width=15).pack(side='left')
                        tk.Label(item_frame, text=ord_dl, bg='white', anchor='w').pack(side='right')
            else:
                tk.Label(self.dl_container, text="No Deadlines Today",font=('Arial', 12), bg='white', fg='green').pack(anchor='w',pady=20)
                        

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        # Schedule next refresh (5000ms = 5 seconds)
        self.dl_container.after(5000, self._dl_report_refresh)

    def _to_excel(self):
        to_excel = CTkFrame(self, fg_color='white',  border_color='black',  border_width=1, height=270, width=240)
        to_excel.pack(side='left', padx=5)

    def excel_btn(self, parent, text):
        pass

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def _column_heads(self, columns, text):
        self.client_tree.heading(columns, text=text)
        self.client_tree.column(columns, width=100)

    def _images_buttons(self, image_path, size=(40, 40)):

        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
#Global Functions

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self) 

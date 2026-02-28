import tkinter as tk
import time
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.relativedelta import relativedelta
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel, CTkComboBox, CTkScrollableFrame
from PIL import Image
import sqlite3
import csv
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import time
from datetime import datetime
import sys

# --- Pathing Setup ---
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from pages_handler import FrameNames
from global_func import on_show, handle_logout, get_credentials, product_logs_to_sheets, settings_logs_to_sheets, action_logs_to_sheets, user_logs_to_sheets
from product import ProductManagementSystem
from global_func import resource_path

class MainMRP(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.analytics_fig = None
        self.analytics_canvas_widget = None
        self.materials_fig = None
        self.materials_canvas_widget = None
        self._after_ids = set() # Use a set to store all scheduled .after() jobs to avoid duplicates
        self.config(bg='white')


        novus_logo = Image.open(resource_path(os.path.join('labels', 'novus_logo1.png')))
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        #Buttons Images
        self.clients_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'client_btn.png'), size=(100,100))
        self.inv_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'inventory.png'), size=(100,100))
        self.product_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'product.png'), size=(100,100))
        self.order_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'order.png'), size=(100,100))
        self.supply_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'supply.png'), size=(100,100))
        self.logout_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'logout.png'), size=(100,100))
        self.mrp_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'mrp_btn.png'), size=(100,100))
        self.settings_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'settings.png'), size=(100,100))
        self.user_logs_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'action.png'), size=(100,100))
        self.mails_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'mail.png'), size=(100,100))
        self.audit_btn = self._images_buttons(os.path.join(BASE_DIR, 'labels', 'audit.png'), size=(100,100))

        # --- Main Layout ---
        self.main = CTkFrame(self, fg_color="#6a9bc3", width=120, corner_radius=0)
        self.main.pack(side="left", fill="y")

        # --- Content Area (Right side) ---
        self.content_area = CTkFrame(self, fg_color="white", corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.main_desc = CTkFrame(self.content_area, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 5))

        self.scrollable_content = CTkScrollableFrame(self.content_area, fg_color="white", corner_radius=0)
        self.scrollable_content.pack(side="top", fill="both", expand=True)

        # --- REFRESH BUTTON ---_
        self.refresh_icon = CTkImage(Image.open(resource_path(os.path.join('labels', 'refresh.png'))), size=(22, 22))
        self.refresh_btn = CTkButton(
            self.main_desc,
            text="",
            image=self.refresh_icon,
            fg_color="white",
            hover_color="#f0f0f0",
            text_color="#2a4d69", 
            font=('Roboto', 15, 'bold'),
            width=36,
            height=36,
            command=self.refresh_dashboard
        )
        self.refresh_btn.pack(side="right", padx=20, pady=10)

        # --- LOW COUNT NOTIFICATIONS BUTTON ---
        self.low_count_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.low_count_btn_frame.pack(side="right", padx=10)
        self.low_count_btn = CTkButton(
            self.low_count_btn_frame,
            text="Low Count Notifications",
            fg_color="white",
            hover_color="#f0f0f0",
            text_color="#2a4d69", 
            font=('Roboto', 15, 'bold'),
            command=self.show_low_count_window,
            width=180,
            height=36,
            corner_radius=8
        )
        self.low_count_btn.pack(side="left", padx=(0, 8), pady=8)
        # Reposition badge on layout changes
        try:
            self.low_count_btn_frame.bind("<Configure>", self._position_low_count_badge)
            self.low_count_btn.bind("<Configure>", self._position_low_count_badge)
        except Exception:
            pass
        self.update_low_count_dot()
        # Re-run after layout to ensure geometry is ready for badge placement
        try:
            self._after_ids.add(self.after(0, self.update_low_count_dot))
            self._after_ids.add(self.after(150, self._position_low_count_badge))
            self._after_ids.add(self.after_idle(self._position_low_count_badge))
            self._after_ids.add(self.after_idle(self.update_low_count_dot))
        except Exception:
            pass

        # --- DASHBOARD & ANALYTICS ---
        self._dashboard_row()


    def destroy(self):
        """Override destroy to cancel all pending after() jobs."""
        # Explicitly close matplotlib figures and destroy their canvas widgets
        if self.analytics_fig:
            plt.close(self.analytics_fig)
            self.analytics_fig = None
        if self.analytics_canvas_widget and self.analytics_canvas_widget.winfo_exists():
            self.analytics_canvas_widget.destroy()
            self.analytics_canvas_widget = None
        if self.materials_fig:
            plt.close(self.materials_fig)
            self.materials_fig = None
        if self.materials_canvas_widget and self.materials_canvas_widget.winfo_exists():
            self.materials_canvas_widget.destroy()
            self.materials_canvas_widget = None
        # Cancel all scheduled tasks to prevent errors on shutdown
        for after_id in self._after_ids:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass # Ignore errors if the job or widget is already gone
        self._close_low_inv_window() # Ensure the low inventory window and its tasks are closed
        super().destroy()

    def refresh_dashboard(self):
        """Refresh all dashboard cards with latest DB values."""
        if hasattr(self, 'dashboard_container_frame') and self.dashboard_container_frame.winfo_exists():
            self.dashboard_container_frame.destroy()
        self._dashboard_row()

        self._create_materials_graph()
        self._create_analytics_graph()

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
                                    font=('Arial', 17, 'bold'))
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
            cursor.execute('SELECT mat_id, mat_name, current_stock, supplier_id, min_stock_level FROM raw_mats WHERE is_active = 1')
            rows = cursor.fetchall()
            # Determine low items based on dynamic minimum stock level
            low_items = [row for row in rows if row[2] < row[4]]
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
                
                CTkLabel(headers, text="ID", width=10, font=('Arial', 15, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Material Name", width=25, font=('Arial', 15, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Supplier", width=20, font=('Arial', 15, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Stock", width=15, font=('Arial', 15, 'bold')).pack(side='right', padx=5)
                
                # Add items with red background for entire row
                for mat_id, name, vol, supplier, min_level in low_items:
                    # Use CTkFrame so child CTkLabels render nicely over the background
                    item = CTkFrame(self.items_frame, fg_color='#f8d7da')  # deeper light red background
                    item.pack(fill='x', pady=2)

                    CTkLabel(item, text=mat_id, width=10, fg_color='transparent', font=('Arial', 13)).pack(side='left', padx=5)
                    CTkLabel(item, text=name, width=25, fg_color='transparent', font=('Arial', 13)).pack(side='left', padx=5)
                    CTkLabel(item, text=supplier, width=20, fg_color='transparent', font=('Arial', 13)).pack(side='left', padx=5)
                    CTkLabel(item, text=f"{vol} units", text_color='red', width=15, fg_color='transparent', font=('Arial', 13, 'bold')).pack(side='right', padx=5)
                    CTkButton(item, text="Edit", width=50,
                              command=lambda m=mat_id: self.open_edit_window(m)).pack(side='right', padx=5)
            else:
                CTkLabel(self.items_frame, 
                    text="All items are properly stocked (≥100 units)",
                    font=('Arial', 17),
                    text_color='green').pack(pady=20)
            
            # Schedule next refresh if window still exists
            if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
                after_id = self.low_inv_window.after(5000, self.refresh_low_items)
                self._low_inv_after_id = after_id # Store for cancellation
                self._after_ids.add(self._low_inv_after_id) # Also add to the main set for global cancellation
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {str(e)}")

    def _close_low_inv_window(self):
        """Properly clean up the low inventory window"""
        if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
            # Cancel any pending refresh
            if hasattr(self, '_low_inv_after_id') and self._low_inv_after_id:
                self.low_inv_window.after_cancel(self._low_inv_after_id)
                self._after_ids.discard(self._low_inv_after_id) # Remove from the main set
            self.low_inv_window.destroy()

    def open_edit_window(self, material_id):
        # Placeholder for your edit window function
        print(f"Editing material with ID: {material_id}")
        # Add your edit window implementation here

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
            
    def _to_excel(self):
        to_excel = CTkFrame(self, fg_color='white',  border_color='black',  border_width=1, height=270, width=240)
        to_excel.pack(side='left', padx=5)

    def excel_btn(self, parent, text):
        pass

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, 
                           image=image, 
                           text=text, 
                           font=('Futura', 15, 'bold'),
                           text_color="black",
                           bg_color="#6a9bc3", 
                           fg_color="#6a9bc3", 
                           hover_color="white",
                           width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15, fill='x')

    def _column_heads(self, columns, text):
        self.client_tree.heading(columns, text=text)
        self.client_tree.column(columns, width=100)

    def _images_buttons(self, image_path, size=(40, 40)):

        image = Image.open(resource_path(image_path))
        size = size
        return CTkImage(image)
    
    def _dashboard_row(self):
        """Create a horizontal row for product, order, and raw materials dashboards, centered."""
        # Main container to hold all dashboard content
        self.dashboard_container_frame = tk.Frame(self.scrollable_content, bg='white')
        self.dashboard_container_frame.pack(pady=10, padx=20, fill="x")

        # Center the content within the container
        self.dashboard_container_frame.grid_columnconfigure(0, weight=1)

        # --- First Row (3 cards) ---
        self.dashboard_row1_frame = tk.Frame(self.dashboard_container_frame, bg='white')
        self.dashboard_row1_frame.grid(row=0, column=0, pady=(0, 10))

        self._cancelled_orders_dashboard(parent=self.dashboard_row1_frame)
        self._rawmats_dashboard(parent=self.dashboard_row1_frame)
        self._orders_dashboard(parent=self.dashboard_row1_frame) # Delivered Orders

        # --- Second Row (2 cards) ---
        self.dashboard_row2_frame = tk.Frame(self.dashboard_container_frame, bg='white')
        self.dashboard_row2_frame.grid(row=1, column=0, pady=10)

        self._pending_orders_dashboard(parent=self.dashboard_row2_frame)
        self._done_orders_dashboard(parent=self.dashboard_row2_frame)
        self._deadlines_dashboard_button(parent=self.dashboard_row2_frame)

    def _cancelled_orders_dashboard(self, parent):
        """Dashboard card for cancelled orders."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Cancelled Orders",
            font=('Roboto', 17, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status_quo = 'Cancelled'")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Roboto', 33, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(6, 10))

        # Accent bar for visual emphasis
        accent_bar = CTkFrame(dashboard_frame, fg_color='#cfe2f3', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
            accent_bar.configure(fg_color='#4b86b4')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
            accent_bar.configure(fg_color='#cfe2f3')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_cancelled_orders_page(event=None):
            if self.controller:
                try:
                    orders_page = self.controller.frames.get(FrameNames.ORDERS)
                    if orders_page:
                        orders_page.set_status_filter("Cancelled")
                        self.controller.show_frame(FrameNames.ORDERS)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open Cancelled Orders page: {e}")

        dashboard_frame.bind("<Button-1>", open_cancelled_orders_page)
        title.bind("<Button-1>", open_cancelled_orders_page)
        value_label.bind("<Button-1>", open_cancelled_orders_page)

    def _orders_dashboard(self, parent):
        """Dashboard card for total orders, same size and style as product dashboard."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Delivered Orders",
            font=('Roboto', 17, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders WHERE is_active = 1 AND status_quo = 'Delivered'")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Roboto', 33, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        # Accent bar for visual emphasis
        accent_bar = CTkFrame(dashboard_frame, fg_color='#cfe2f3', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
            accent_bar.configure(fg_color='#4b86b4')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
            accent_bar.configure(fg_color='#cfe2f3')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_delivered_orders_page(event=None):
            if self.controller:
                orders_page = self.controller.frames.get(FrameNames.ORDERS)
                if orders_page:
                    orders_page.set_status_filter("Delivered")
                    self.controller.show_frame(FrameNames.ORDERS)

        dashboard_frame.bind("<Button-1>", open_delivered_orders_page)
        title.bind("<Button-1>", open_delivered_orders_page)
        value_label.bind("<Button-1>", open_delivered_orders_page)

    def _rawmats_dashboard(self, parent):
        """Dashboard card for total raw materials, same size and style as others."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Raw Materials",
            font=('Roboto', 17, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM raw_mats WHERE is_active = 1")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Roboto', 33, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        # Accent bar for visual emphasis
        accent_bar = CTkFrame(dashboard_frame, fg_color='#cfe2f3', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
            accent_bar.configure(fg_color='#4b86b4')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
            accent_bar.configure(fg_color='#cfe2f3')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_rawmats_page(event=None):
            if self.controller:
                self.controller.show_frame(FrameNames.INVENTORY)

        dashboard_frame.bind("<Button-1>", open_rawmats_page)
        title.bind("<Button-1>", open_rawmats_page)
        value_label.bind("<Button-1>", open_rawmats_page)

    def _pending_orders_dashboard(self, parent):
        """Dashboard card for pending orders."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Pending Orders",
            font=('Roboto', 17, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders WHERE is_active = 1 AND status_quo = 'Pending'")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Roboto', 33, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        accent_bar = CTkFrame(dashboard_frame, fg_color='#cfe2f3', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
            accent_bar.configure(fg_color='#4b86b4')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
            accent_bar.configure(fg_color='#cfe2f3')

        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_pending_orders_page(event=None):
            if self.controller:
                orders_page = self.controller.frames.get(FrameNames.ORDERS)
                if orders_page:
                    orders_page.set_status_filter("Pending")
                    self.controller.show_frame(FrameNames.ORDERS)

        dashboard_frame.bind("<Button-1>", open_pending_orders_page)
        title.bind("<Button-1>", open_pending_orders_page)
        value_label.bind("<Button-1>", open_pending_orders_page)

    def _done_orders_dashboard(self, parent):
        """Dashboard card for done orders."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(dashboard_frame, text="Done Orders", font=('Roboto', 17, 'bold'), text_color='#2a4d69')
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders WHERE is_active = 1 AND status_quo = 'Done'")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(dashboard_frame, text=str(count), font=('Roboto', 33, 'bold'), text_color='#4b86b4')
        value_label.pack(pady=(4, 10))

        accent_bar = CTkFrame(dashboard_frame, fg_color='#cfe2f3', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e): dashboard_frame.configure(fg_color='#f5faff'); accent_bar.configure(fg_color='#4b86b4')
        def on_leave(e): dashboard_frame.configure(fg_color='white'); accent_bar.configure(fg_color='#cfe2f3')

        for widget in [dashboard_frame, title, value_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.controller.frames.get(FrameNames.ORDERS).set_status_filter("Done") or self.controller.show_frame(FrameNames.ORDERS))

    def _deadlines_dashboard_button(self, parent):
        """Dashboard card that shows 'Done' orders due within 7 days."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(dashboard_frame, text="Upcoming Deadlines", font=('Roboto', 17, 'bold'), text_color='#2a4d69')
        title.pack(pady=(16, 0))

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            query = """
                SELECT deadline
                FROM orders
                WHERE is_active = 1 AND status_quo NOT IN ('Delivered', 'Cancelled')
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            conn.close()

            today = datetime.now().date()
            upcoming_count = 0
            for (deadline_str,) in orders:
                try:
                    if deadline_str:
                        deadline_date_part = deadline_str.split(' ')[0]
                        try:
                            deadline_date = datetime.strptime(deadline_date_part, '%Y-%m-%d').date()
                        except ValueError:
                            deadline_date = datetime.strptime(deadline_date_part, '%m/%d/%Y').date()

                        if 0 <= (deadline_date - today).days <= 7:
                            upcoming_count += 1
                except (ValueError, TypeError):
                    continue
            count = upcoming_count
        except Exception as e:
            print(f"Error counting deadlines: {e}")
            count = "?"

        value_label = CTkLabel(dashboard_frame, text=str(count), font=('Roboto', 33, 'bold'), text_color='#e74c3c')
        value_label.pack(pady=(4, 10))

        accent_bar = CTkFrame(dashboard_frame, fg_color='#f8d7da', height=4)
        accent_bar.pack(side='bottom', fill='x', padx=12, pady=(0, 10))

        def on_enter(e): dashboard_frame.configure(fg_color='#fff5f5'); accent_bar.configure(fg_color='#e74c3c')
        def on_leave(e): dashboard_frame.configure(fg_color='white'); accent_bar.configure(fg_color='#f8d7da')

        for widget in [dashboard_frame, title, value_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.show_deadlines_window())

    def show_deadlines_window(self):
        """Shows a Toplevel window with 'Done' orders due within 7 days."""
        win = tk.Toplevel(self)
        win.title("Upcoming Order Deadlines")
        win.geometry("900x500")
        win.resizable(False, False)
        win.configure(bg='white')

        frame = CTkFrame(win, fg_color="white")
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        header = CTkLabel(frame, text="Orders Due Within 7 Days", font=('Roboto', 19, 'bold'), text_color='#2a4d69')
        header.pack(pady=(0, 12))

        style = ttk.Style(win)
        # Use a custom style name to avoid affecting other Treeviews in the app
        style.configure("Deadlines.Treeview", rowheight=28, font=('Roboto', 13))
        style.configure("Deadlines.Treeview.Heading", font=('Roboto', 14, 'bold'))

        tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Client', 'Deadline', 'Days Left'), show='headings', style="Deadlines.Treeview")
        tree.heading('ID', text='Order ID'); tree.column('ID', width=150, anchor='center')
        tree.heading('Name', text='Order Name'); tree.column('Name', width=250)
        tree.heading('Client', text='Client'); tree.column('Client', width=200)
        tree.heading('Deadline', text='Deadline Date'); tree.column('Deadline', width=120, anchor='center')
        tree.heading('Days Left', text='Days Left'); tree.column('Days Left', width=100, anchor='center')
        tree.pack(fill='both', expand=True)

        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            query = """
                SELECT o.order_id, o.order_name, c.client_name, o.deadline
                FROM orders o JOIN clients c ON o.client_id = c.client_id
                WHERE o.is_active = 1 AND o.status_quo NOT IN ('Delivered', 'Cancelled')
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            conn.close()

            today = datetime.now().date()
            for order_id, order_name, client_name, deadline_str in orders:
                if deadline_str:
                    # Split the string to handle cases where time is included (e.g., 'YYYY-MM-DD HH:MM:SS')
                    deadline_date_part = deadline_str.split(' ')[0] # Get only the date part
                    try:
                        # First, try the standard YYYY-MM-DD format
                        deadline_date = datetime.strptime(deadline_date_part, '%Y-%m-%d').date()
                    except ValueError:
                        # If that fails, try the MM/DD/YYYY format as a fallback
                        deadline_date = datetime.strptime(deadline_date_part, '%m/%d/%Y').date()

                    days_left = (deadline_date - today).days
                    if 0 <= days_left <= 7:
                        tree.insert('', 'end', values=(order_id, order_name, client_name, deadline_str, days_left))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load deadlines: {e}")

    def _create_analytics_graph(self):
        """Creates and embeds the client order analytics graph."""
        # Clean up previous graph resources if they exist
        if self.analytics_fig:
            plt.close(self.analytics_fig)
            self.analytics_fig = None
        if self.analytics_canvas_widget and self.analytics_canvas_widget.winfo_exists():
            self.analytics_canvas_widget.destroy()
            self.analytics_canvas_widget = None

        # Destroy the container frame if it exists to clear old widgets
        if hasattr(self, 'analytics_frame') and self.analytics_frame.winfo_exists():
            self.analytics_frame.destroy()

        self.analytics_frame = CTkFrame(self.scrollable_content, fg_color="white", border_color='#e0e0e0', border_width=2, corner_radius=16)
        self.analytics_frame.pack(pady=20, padx=20, fill="x")

        # --- Header and Navigation ---
        header_frame = CTkFrame(self.analytics_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.analytics_title = CTkLabel(header_frame, text="", font=('Roboto', 14, 'bold'), text_color='#2a4d69')
        self.analytics_title.pack(side="left", expand=True)

        # --- Group navigation buttons together ---
        nav_frame = CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        self.prev_month_btn = CTkButton(nav_frame, text="< Prev", width=80, command=self.prev_month_analytics)
        self.prev_month_btn.pack(side="left", padx=(0, 5))
        self.next_month_btn = CTkButton(nav_frame, text="Next >", width=80, command=self.next_month_analytics)
        self.next_month_btn.pack(side="left")

        # --- Graph Canvas ---
        self.graph_canvas_frame = CTkFrame(self.analytics_frame, fg_color="white")
        self.graph_canvas_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.update_analytics_graph()

    def update_analytics_graph(self):
        """Fetches data and updates the analytics graph for the current month."""
        month_str = self.current_analytics_month.strftime("%B %Y")
        self.analytics_title.configure(text=f"Top 5 clients: {month_str}")

        # Disable 'Next' button if viewing the current or a future month
        now = datetime.now().date().replace(day=1)
        if self.current_analytics_month >= now:
            self.next_month_btn.configure(state="disabled")
        else:
            self.next_month_btn.configure(state="normal")

        # Fetch data
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()

            start_date = self.current_analytics_month
            end_date = self.current_analytics_month + relativedelta(months=1)

            query = """
                SELECT c.client_name, COUNT(o.order_id) as order_count
                FROM order_history oh
                JOIN orders o ON oh.order_id = o.order_id
                JOIN clients c ON o.client_id = c.client_id
                WHERE oh.status = 'Delivered'
                  AND oh.timestamp >= ? AND oh.timestamp < ?
                GROUP BY c.client_name
                ORDER BY order_count DESC
                LIMIT 5
            """
            cursor.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            data = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to load analytics data: {e}")
            return

        # Clear previous graph
        for widget in self.graph_canvas_frame.winfo_children():
            widget.destroy()

        if not data:
            CTkLabel(self.graph_canvas_frame, text="No delivered orders for this month.", font=('Roboto', 12), text_color="gray").pack(pady=50)
            return

        clients = [row[0] for row in data]
        counts = [row[1] for row in data]

        # Create plot
        fig, ax = plt.subplots(figsize=(7, 2)) # Adjusted figsize for shorter height
        bars = ax.barh(clients, counts, color='#4b86b4')
        ax.set_xlabel('Number of Delivered Orders', fontdict={'fontsize': 10})
        ax.set_title('Top 5 clients by Delivered Orders', fontdict={'fontsize': 12, 'fontweight': 'bold'})
        ax.invert_yaxis() # Top client at the top
        ax.tick_params(axis='y', labelsize=9)
        ax.tick_params(axis='x', labelsize=9)

        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height()/2., f'{int(width)}', va='center', ha='left', fontsize=6)

        plt.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas_frame)
        self.analytics_fig = fig  # Store the figure reference
        canvas.draw()
        self.analytics_canvas_widget = canvas.get_tk_widget() # Store the Tkinter widget reference
        self.analytics_canvas_widget.pack(fill="both", expand=True)

    def prev_month_analytics(self):
        self.current_analytics_month -= relativedelta(months=1)
        self.update_analytics_graph()

    def next_month_analytics(self):
        self.current_analytics_month += relativedelta(months=1)
        self.update_analytics_graph()

    def _create_materials_graph(self):
        """Creates and embeds the most used materials analytics graph."""
        # Clean up previous graph resources if they exist
        if self.materials_fig:
            plt.close(self.materials_fig)
            self.materials_fig = None
        if self.materials_canvas_widget and self.materials_canvas_widget.winfo_exists():
            self.materials_canvas_widget.destroy()
            self.materials_canvas_widget = None

        # Destroy the container frame if it exists to clear old widgets
        if hasattr(self, 'materials_analytics_frame') and self.materials_analytics_frame.winfo_exists():
            self.materials_analytics_frame.destroy()

        self.materials_analytics_frame = CTkFrame(self.scrollable_content, fg_color="white", border_color='#e0e0e0', border_width=2, corner_radius=16)
        self.materials_analytics_frame.pack(pady=20, padx=20, fill="x")

        # --- Header and Navigation ---
        header_frame = CTkFrame(self.materials_analytics_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.materials_analytics_title = CTkLabel(header_frame, text="", font=('Roboto', 14, 'bold'), text_color='#2a4d69')
        self.materials_analytics_title.pack(side="left", expand=True)

        nav_frame = CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        self.materials_prev_month_btn = CTkButton(nav_frame, text="< Prev", width=80, command=self.prev_month_materials)
        self.materials_prev_month_btn.pack(side="left", padx=(0, 5))
        self.materials_next_month_btn = CTkButton(nav_frame, text="Next >", width=80, command=self.next_month_materials)
        self.materials_next_month_btn.pack(side="left")

        # --- Graph Canvas ---
        self.materials_graph_canvas_frame = CTkFrame(self.materials_analytics_frame, fg_color="white")
        self.materials_graph_canvas_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.update_materials_graph()

    def update_materials_graph(self):
        """Fetches data and updates the materials analytics graph for the current month."""
        month_str = self.current_materials_month.strftime("%B %Y")
        self.materials_analytics_title.configure(text=f"Top 5 Most Used Materials (Approved Orders): {month_str}")

        now = datetime.now().date().replace(day=1)
        self.materials_next_month_btn.configure(state="disabled" if self.current_materials_month >= now else "normal")

        material_usage = {}
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            start_date = self.current_materials_month
            end_date = self.current_materials_month + relativedelta(months=1)

            query = "SELECT mats_need FROM orders WHERE status_quo = 'Approved' AND order_date >= ? AND order_date < ?"
            cursor.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            for (mats_need_json,) in cursor.fetchall():
                if mats_need_json:
                    try:
                        mats = json.loads(mats_need_json)
                        for mat, qty in mats.items():
                            material_usage[mat] = material_usage.get(mat, 0) + float(qty)
                    except (json.JSONDecodeError, ValueError):
                        continue
            conn.close()
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to load material usage data: {e}")
            return

        for widget in self.materials_graph_canvas_frame.winfo_children():
            widget.destroy()

        if not material_usage:
            CTkLabel(self.materials_graph_canvas_frame, text="No material usage data for this month.", font=('Roboto', 12), text_color="gray").pack(pady=50)
            return

        sorted_materials = sorted(material_usage.items(), key=lambda item: item[1], reverse=True)[:5]
        materials = [item[0] for item in sorted_materials]
        counts = [item[1] for item in sorted_materials]

        fig, ax = plt.subplots(figsize=(7, 2))
        ax.barh(materials, counts, color='#27ae60')
        ax.set_xlabel('Total Quantity Used', fontdict={'fontsize': 10})
        ax.set_title('Top 5 Most Used Materials', fontdict={'fontsize': 12, 'fontweight': 'bold'})
        ax.invert_yaxis()
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, f'{v:,.2f}', color='blue', va='center', fontweight='bold', fontsize=6)

        plt.tight_layout(pad=2.0)
        canvas = FigureCanvasTkAgg(fig, master=self.materials_graph_canvas_frame)
        self.materials_fig = fig  # Store the figure reference
        canvas.draw()
        self.materials_canvas_widget = canvas.get_tk_widget() # Store the Tkinter widget reference
        self.materials_canvas_widget.pack(fill="both", expand=True)

    def prev_month_materials(self):
        self.current_materials_month -= relativedelta(months=1)
        self.update_materials_graph()

    def next_month_materials(self):
        self.current_materials_month += relativedelta(months=1)
        self.update_materials_graph()

    def parse_log_line(self, line):
        """Parse a single log line and return a dict or None."""
        pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s*-\s*'
            r'(?P<level>\w+)\s*-\s*'
            r'User\s*ID:\s*(?P<user_id>[^|]+)\|\s*'
            r'Username:\s*(?P<username>[^|]+)\|\s*'
            r'Feature:\s*(?P<feature>[^|]+)\|\s*'
            r'Operation:\s*(?P<operation>[^|]+)\|\s*'
            r'Action:\s*(?P<action>[^|]+)\|\s*'
            r'Details:\s*(?P<details>[^|]+)\|\s*'
            r'Time:\s*(?P<time>.+)'
        )

#Global Functions

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic
        # Defer graph creation until the frame is shown to ensure it runs on the main thread
        if not hasattr(self, 'analytics_frame') or not self.analytics_frame.winfo_exists():
            self.current_analytics_month = datetime.now().date().replace(day=1)
            self.current_materials_month = datetime.now().date().replace(day=1)
            self._create_materials_graph()
            self._create_analytics_graph()
        self.update_low_count_dot()


    def handle_logout(self):
        handle_logout(self)

    def update_low_count_dot(self):
        """Show/hide red dot if there are low count materials."""
        try: #This path is also in product.py, will fix it there too
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT current_stock, min_stock_level FROM raw_mats WHERE is_active = 1")
            low_items = [row for row in cursor.fetchall() if row[0] < row[1]]
            conn.close()
        except Exception:
            low_items = []

        # Update button background based on low count presence
        if hasattr(self, 'low_count_btn') and self.low_count_btn.winfo_exists():
            if low_items:
                self.low_count_btn.configure(fg_color="#e74c3c", hover_color="#c0392b", text_color="white")
            else:
                self.low_count_btn.configure(fg_color="white", hover_color="#f0f0f0", text_color="#2a4d69")

        # Update or create numeric badge showing count of low items
        count = len(low_items)
        try:
            if count > 0:
                if not hasattr(self, 'low_count_badge') or not getattr(self, 'low_count_badge', None) or not self.low_count_badge.winfo_exists():
                    self.low_count_badge = tk.Label(
                        self.low_count_btn_frame,
                        text=str(count),
                        bg="#e74c3c",
                        fg="white",
                        font=('Roboto', 9, 'bold'),
                        padx=6,
                        pady=1,
                        bd=0,
                        relief='flat'
                    )
                else:
                    self.low_count_badge.configure(text=str(count))
                # Position after geometry is ready
                try:
                    self._position_low_count_badge()
                    self.after(0, self._position_low_count_badge)
                except Exception:
                    pass
                self.low_count_badge.lift()
            else:
                if hasattr(self, 'low_count_badge') and self.low_count_badge and self.low_count_badge.winfo_exists():
                    self.low_count_badge.place_forget()
        except Exception:
            pass

    def _position_low_count_badge(self, event=None):
        # Check if the relevant frames still exist before trying to access them
        if not hasattr(self, 'low_count_btn_frame') or not self.low_count_btn_frame.winfo_exists():
            return # Exit if the frame is already destroyed
        try:
            if hasattr(self, 'low_count_badge') and self.low_count_badge and self.low_count_badge.winfo_exists():
                btn = self.low_count_btn
                # Position near top-right of the button
                x = btn.winfo_x() + btn.winfo_width() - 10
                y = btn.winfo_y() - 6
                self.low_count_badge.place(x=x, y=y)
        except Exception:
            pass

    def show_low_count_window(self):
        """Show a neat window with info about low count materials, with both scrollbars."""
        win = tk.Toplevel(self)
        win.title("Low Count Materials")
        win.geometry("1200x700")
        win.resizable(False, False)
        frame = CTkFrame(win, fg_color="white")
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        header = CTkLabel(frame, text="Materials Below Low Count", font=('Roboto', 16, 'bold'), text_color='#e74c3c')
        header.pack(pady=(0, 12))

        # Scrollable area for table (vertical only)
        table_canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(frame, orient="vertical", command=table_canvas.yview)
        table_canvas.configure(yscrollcommand=v_scrollbar.set)
        table_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        table_frame = tk.Frame(table_canvas, bg="white")
        table_canvas.create_window((0, 0), window=table_frame, anchor="nw")

        # Table headers (fit within expanded window width)
        headers = ["ID", "Material Name", "Volume", "Low Count", "Need", "Supplier"]
        col_widths = [10, 28, 12, 12, 14, 28]
        for col, (text, w) in enumerate(zip(headers, col_widths)):
            tk.Label(
                table_frame,
                text=text,
                font=('Roboto', 12, 'bold'),
                bg="white",
                fg="#2980b9",
                width=w,
                anchor="center",
                relief='flat',
                bd=0,
                highlightthickness=0,
            ).grid(row=0, column=col, padx=4, pady=6)

        # Data
        try:
            conn = sqlite3.connect(resource_path('main.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT mat_id, mat_name, current_stock, min_stock_level, supplier_id FROM raw_mats WHERE is_active = 1")
            rows = cursor.fetchall()
            low_items = [row for row in rows if int(row[2]) < int(row[3])]
            conn.close()
        except Exception as e:
            print("Error fetching low count items:", e)
            low_items = []

        if low_items:
            for r, (mat_id, name, vol, low, supplier) in enumerate(low_items, start=1):
                row_bg = '#f8d7da' 
                tk.Label(table_frame, text=mat_id, bg=row_bg, font=('Roboto', 14), width=10, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=0, padx=0, pady=0, sticky="nsew")
                tk.Label(table_frame, text=name, bg=row_bg, font=('Roboto', 14), width=20, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=1, padx=0, pady=0, sticky="nsew")
                tk.Label(table_frame, text=str(vol), bg=row_bg, font=('Roboto', 14), fg="#e74c3c", width=10, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=2, padx=0, pady=0, sticky="nsew")
                tk.Label(table_frame, text=str(low), bg=row_bg, font=('Roboto', 14), fg="#e74c3c", width=10, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=3, padx=0, pady=0, sticky="nsew")
                # Required to meet minimum stock level
                try:
                    req = max(int(low) - int(vol), 0)
                except Exception:
                    req = "-"
                tk.Label(table_frame, text=str(req), bg=row_bg, font=('Roboto', 14), fg="#c0392b", width=10, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=4, padx=0, pady=0, sticky="nsew")
                tk.Label(table_frame, text=supplier, bg=row_bg, font=('Roboto', 14), width=20, anchor="center", relief='flat', bd=0, highlightthickness=0).grid(row=r, column=5, padx=0, pady=0, sticky="nsew")
        else:
            tk.Label(table_frame, text="No materials are below their low count.", font=('Roboto', 12), bg="white", fg="green").grid(row=1, column=0, columnspan=6, pady=18)

        # Make table scrollable
        def _on_frame_configure(event):
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
        table_frame.bind("<Configure>", _on_frame_configure)

        win.protocol("WM_DELETE_WINDOW", lambda: [win.destroy(), self.update_low_count_dot()])

    def open_logs_modal(self):
        """Open a centered, fixed-size popup with 4 log action buttons (single-instance)."""
        # If already open, bring to front instead of creating another
        if hasattr(self, 'logs_modal') and self.logs_modal and self.logs_modal.winfo_exists():
            try:
                self.logs_modal.lift()
                self.logs_modal.focus_force()
            except Exception:
                pass
            return

        win = CTkToplevel(self)
        self.logs_modal = win
        win.title("Logs")
        win.resizable(False, False)
        width, height = 420, 240

        # Center on parent
        try:
            parent = self.winfo_toplevel()
            parent.update_idletasks()
            px = parent.winfo_x(); py = parent.winfo_y()
            pw = parent.winfo_width() or 1000; ph = parent.winfo_height() or 700
            x = px + (pw - width) // 2; y = py + (ph - height) // 2
        except Exception:
            win.update_idletasks()
            sw = win.winfo_screenwidth(); sh = win.winfo_screenheight()
            x = (sw - width) // 2; y = (sh - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

        # Modal behavior (consistent with system)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        # Root container
        container = CTkFrame(win, fg_color="white")
        container.pack(fill="both", expand=True)

        # Title bar (blue) to match section headers
        title_bar = tk.Frame(container, bg='#2a72c9')
        title_bar.pack(fill='x')
        tk.Label(title_bar, text="Logs", font=('Roboto', 15, 'bold'), fg='white', bg='#2a72c9').pack(anchor='w', padx=16, pady=6)

        body = CTkFrame(container, fg_color='white')
        body.pack(fill='both', expand=True, padx=16, pady=12)

        # Buttons grid (2x2)
        grid = tk.Frame(body, bg='white')
        grid.pack(expand=True)

        def mk_btn(text, cmd, r, c):
            btn = CTkButton(
                grid,
                text=text,
                fg_color="#ffffff",
                hover_color="#f0f0f0",
                text_color="#2a4d69",
                font=('Roboto', 12, 'bold'),
                width=160,
                height=40,
                corner_radius=8,
                command=cmd,
            )
            btn.grid(row=r, column=c, padx=10, pady=8, sticky='nsew')

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # Use existing log actions (unchanged)
        mk_btn("Product Logs", product_logs_to_sheets, 0, 0)
        mk_btn("Settings Logs", settings_logs_to_sheets, 0, 1)
        mk_btn("User Activity Logs", action_logs_to_sheets, 1, 0)
        mk_btn("User Logs", user_logs_to_sheets, 1, 1)

        # Footer
        CTkButton(body, text="Close", fg_color="#2980b9", hover_color="#3498db", text_color="white", width=100, command=win.destroy).pack(pady=(8, 0))

        def _on_close():
            try:
                win.grab_release()
            except Exception:
                pass
            try:
                win.destroy()
            finally:
                self.logs_modal = None
        win.protocol("WM_DELETE_WINDOW", _on_close)
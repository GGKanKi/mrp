import sqlite3
import uuid
import tkinter as tk
from tkinter import messagebox, ttk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
import customtkinter as ctk
import sys
sys.path.append("D:/capstone")

# Create a single-screen inventory management app
class SimpleInventory(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.title("Products and Orders Management System")
        self.geometry("1000x800")
        
        # Connect to existing database
        self.conn = sqlite3.connect('main.db')
        self.cursor = self.conn.cursor()
        
        # Create main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="Products and Orders Management System", 
                              font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Create two sections in a grid layout
        self.grid_frame = tk.Frame(self.main_frame)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns to be equal width
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        
        # Create section frames with borders
        self.products_frame = tk.LabelFrame(self.grid_frame, text="Products Management", 
                                          font=("Arial", 12, "bold"), padx=10, pady=10)
        self.products_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.orders_frame = tk.LabelFrame(self.grid_frame, text="Orders Management", 
                                        font=("Arial", 12, "bold"), padx=10, pady=10)
        self.orders_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Create UI elements for each section
        self.create_products_widgets()
        self.create_orders_widgets()
        
        # Load initial data
        self.refresh_products_list()
        self.refresh_orders_list()
        
        # Current product materials (for UI only, not stored in database)
        self.product_materials = []
        
        # Dictionary to store material requirements for current order
        self.order_material_requirements = {}
        
        # Create status bar
        self.status_bar = tk.Label(self.main_frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_products_widgets(self):
        # Configure products frame to expand properly
        self.products_frame.rowconfigure(3, weight=1)
        self.products_frame.columnconfigure(0, weight=1)
        
        # Product input frame
        product_input_frame = tk.Frame(self.products_frame)
        product_input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Product Name
        tk.Label(product_input_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.product_name_entry = tk.Entry(product_input_frame, width=20)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Product ID (hidden)
        self.product_id_var = tk.StringVar()
        
        # Material selection frame
        material_frame = tk.Frame(self.products_frame)
        material_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Material dropdown
        tk.Label(material_frame, text="Select Material:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.material_var = tk.StringVar()
        self.material_dropdown = ttk.Combobox(material_frame, textvariable=self.material_var, width=15)
        self.material_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Quantity
        tk.Label(material_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.quantity_entry = tk.Entry(material_frame, width=8)
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Add material button
        self.add_material_btn = tk.Button(material_frame, text="Add Material", command=self.add_material_to_product, bg="#4CAF50", fg="white")
        self.add_material_btn.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        # Current product materials frame
        product_materials_frame = tk.Frame(self.products_frame)
        product_materials_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        product_materials_frame.rowconfigure(1, weight=1)
        product_materials_frame.columnconfigure(0, weight=1)
        
        tk.Label(product_materials_frame, text="Materials for this product:").grid(row=0, column=0, sticky=tk.W)
        
        # Create scrollbar and listbox for product materials
        pm_scrollbar = tk.Scrollbar(product_materials_frame)
        pm_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.product_materials_list = tk.Listbox(product_materials_frame, width=40, height=5, yscrollcommand=pm_scrollbar.set)
        self.product_materials_list.grid(row=1, column=0, sticky="nsew")
        pm_scrollbar.config(command=self.product_materials_list.yview)
        
        # Product buttons frame
        product_button_frame = tk.Frame(self.products_frame)
        product_button_frame.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.add_product_btn = tk.Button(product_button_frame, text="Add Product", command=self.add_product, bg="#4CAF50", fg="white")
        self.add_product_btn.pack(side=tk.LEFT, padx=2)
        
        self.update_product_btn = tk.Button(product_button_frame, text="Update Product", command=self.update_product, state=tk.DISABLED, bg="#2196F3", fg="white")
        self.update_product_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_product_btn = tk.Button(product_button_frame, text="Delete Product", command=self.delete_product, state=tk.DISABLED, bg="#F44336", fg="white")
        self.delete_product_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_product_btn = tk.Button(product_button_frame, text="Clear", command=self.clear_product_form, bg="#607D8B", fg="white")
        self.clear_product_btn.pack(side=tk.LEFT, padx=2)
        
        # Products list with scrollbar
        products_list_frame = tk.Frame(self.products_frame)
        products_list_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        products_list_frame.rowconfigure(1, weight=1)
        products_list_frame.columnconfigure(0, weight=1)
        
        tk.Label(products_list_frame, text="Available Products:").grid(row=0, column=0, sticky=tk.W)
        
        # Create scrollbar and listbox for products
        p_scrollbar = tk.Scrollbar(products_list_frame)
        p_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.products_list = tk.Listbox(products_list_frame, width=40, height=10, yscrollcommand=p_scrollbar.set)
        self.products_list.grid(row=1, column=0, sticky="nsew")
        p_scrollbar.config(command=self.products_list.yview)
        
        self.products_list.bind('<<ListboxSelect>>', self.on_product_select)
        
        # Update material dropdown
        self.update_material_dropdown()
    
    def create_orders_widgets(self):
        # Configure orders frame to expand properly
        self.orders_frame.rowconfigure(5, weight=1)
        self.orders_frame.columnconfigure(0, weight=1)
        
        # Order form frame
        order_form_frame = tk.Frame(self.orders_frame)
        order_form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Order Name
        tk.Label(order_form_frame, text="Order Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_name_var = tk.StringVar()
        self.order_name_entry = tk.Entry(order_form_frame, textvariable=self.order_name_var, width=20)
        self.order_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Product Selection
        tk.Label(order_form_frame, text="Select Product:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_product_var = tk.StringVar()
        self.order_product_dropdown = ttk.Combobox(order_form_frame, textvariable=self.order_product_var, width=20)
        self.order_product_dropdown.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Client Selection
        tk.Label(order_form_frame, text="Select Client:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_client_var = tk.StringVar()
        self.order_client_dropdown = ttk.Combobox(order_form_frame, textvariable=self.order_client_var, width=20)
        self.order_client_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Order Amount/Quantity
        tk.Label(order_form_frame, text="Quantity:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_quantity_var = tk.StringVar()
        self.order_quantity_entry = tk.Entry(order_form_frame, textvariable=self.order_quantity_var, width=10)
        self.order_quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Materials Display
        materials_frame = tk.Frame(self.orders_frame)
        materials_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        tk.Label(materials_frame, text="Materials Required:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_materials_text = tk.Text(materials_frame, width=30, height=5, state=tk.DISABLED)
        self.order_materials_text.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Inventory Status
        inventory_frame = tk.Frame(self.orders_frame)
        inventory_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        tk.Label(inventory_frame, text="Inventory Status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.inventory_status_text = tk.Text(inventory_frame, width=30, height=5, state=tk.DISABLED)
        self.inventory_status_text.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        
        # Order buttons
        order_button_frame = tk.Frame(self.orders_frame)
        order_button_frame.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.create_order_btn = tk.Button(order_button_frame, text="Create Order", 
                                        command=self.create_order, bg="#4CAF50", fg="white")
        self.create_order_btn.pack(side=tk.LEFT, padx=2)
        
        self.calculate_btn = tk.Button(order_button_frame, text="Calculate Materials", 
                                     command=self.calculate_order_materials, bg="#2196F3", fg="white")
        self.calculate_btn.pack(side=tk.LEFT, padx=2)

        self.clear_order_btn = tk.Button(order_button_frame, text="Clear Form", 
                                       command=self.clear_order_form, bg="#607D8B", fg="white")
        self.clear_order_btn.pack(side=tk.LEFT, padx=2)
        
        # Orders list
        orders_list_frame = tk.Frame(self.orders_frame)
        orders_list_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        orders_list_frame.rowconfigure(1, weight=1)
        orders_list_frame.columnconfigure(0, weight=1)
        
        tk.Label(orders_list_frame, text="Existing Orders:").grid(row=0, column=0, sticky=tk.W)
        
        # Create treeview for orders
        columns = ("ID", "Name", "Product", "Quantity", "Date")
        self.orders_tree = ttk.Treeview(orders_list_frame, columns=columns, show="headings", height=8)
        
        # Define headings
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=70)
        
        self.orders_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(orders_list_frame, orient="vertical", command=self.orders_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_selected)
        
        # Order management buttons
        order_manage_frame = tk.Frame(self.orders_frame)
        order_manage_frame.grid(row=5, column=0, sticky="ew", pady=5)
        
        self.delete_order_btn = tk.Button(order_manage_frame, text="Delete Order", 
                                        command=self.delete_order, bg="#F44336", fg="white")
        self.delete_order_btn.pack(side=tk.LEFT, padx=2)
        
        self.refresh_orders_btn = tk.Button(order_manage_frame, text="Refresh List", 
                                          command=self.refresh_orders_list, bg="#607D8B", fg="white")
        self.refresh_orders_btn.pack(side=tk.LEFT, padx=2)
        
        # Hidden variables
        self.order_id_var = tk.StringVar()
        self.order_materials_data = ""

        
        # Update product dropdown for orders
        self.update_order_product_dropdown()
        self.update_client_dropdown()
    
    def update_material_dropdown(self):
        # Clear existing items
        self.material_dropdown['values'] = []
        
        # Fetch all materials
        self.cursor.execute("SELECT mat_id, mat_name FROM raw_mats")
        materials = self.cursor.fetchall()
        
        # Create a dictionary for easy lookup
        self.material_dict = {f"{name} (ID: {mat_id})": mat_id for mat_id, name in materials}
        
        # Set dropdown values
        self.material_dropdown['values'] = list(self.material_dict.keys())

    def update_client_dropdown(self):
        self.order_client_dropdown['values'] = []

        self.cursor.execute('SELECT client_id, client_name FROM clients')
        clients = self.cursor.fetchall()

        self.client_dict = {f"{client_name} (ID: {client_id})": client_id for client_id, client_name in clients}

        self.order_client_dropdown['values'] = list(self.client_dict.keys())

    def add_material_to_product(self):
        material = self.material_var.get()
        quantity = self.quantity_entry.get()
        
        if not material or not quantity:
            messagebox.showerror("Error", "Please select a material and enter quantity")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero")
                return
            
            # Get material ID from the dictionary
            mat_id = self.material_dict.get(material)
            if not mat_id:
                messagebox.showerror("Error", "Invalid material selection")
                return
            
            # Get material name
            material_name = material.split(" (ID:")[0]
            
            # Add to product materials list (for UI only)
            self.product_materials.append((mat_id, material_name, quantity))
            
            # Update the listbox
            self.product_materials_list.insert(tk.END, f"{material_name} - Quantity: {quantity}")
            
            # Clear the inputs
            self.material_var.set("")
            self.quantity_entry.delete(0, tk.END)
            
            self.status_bar.config(text=f"Material '{material_name}' added to product")
            
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
    
    def add_product(self):
        product_name = self.product_name_entry.get()
        
        if not product_name:
            messagebox.showerror("Error", "Please enter a product name")
            return
        
        if not self.product_materials:
            messagebox.showerror("Error", "Please add at least one material to the product")
            return
        
        try:
            # Generate a unique ID
            product_id = str(uuid.uuid4())[:8]
            
            # Convert product materials to string format for storage
            materials_str = ";".join([f"{mat_id},{name},{qty}" for mat_id, name, qty in self.product_materials])
            
            # Insert product into database
            self.cursor.execute("INSERT INTO products (product_id, product_name, materials) VALUES (?, ?, ?)",
                              (product_id, product_name, materials_str))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_product_form()
            self.refresh_products_list()
            self.update_order_product_dropdown()
            self.status_bar.config(text=f"Product '{product_name}' added successfully")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    
    def update_product(self):
        product_id = self.product_id_var.get()
        product_name = self.product_name_entry.get()
        
        if not product_id or not product_name:
            messagebox.showerror("Error", "Please enter a product name")
            return
        
        if not self.product_materials:
            messagebox.showerror("Error", "Please add at least one material to the product")
            return
        
        try:
            # Convert product materials to string format for storage
            materials_str = ";".join([f"{mat_id},{name},{qty}" for mat_id, name, qty in self.product_materials])
            
            # Update product in database
            self.cursor.execute("UPDATE products SET product_name = ?, materials = ? WHERE product_id = ?",
                              (product_name, materials_str, product_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product updated successfully")
            self.clear_product_form()
            self.refresh_products_list()
            self.update_order_product_dropdown()
            self.status_bar.config(text=f"Product '{product_name}' updated successfully")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_product(self):
        product_id = self.product_id_var.get()
        product_name = self.product_name_entry.get()
        
        if not product_id:
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
        if confirm:
            try:
                # Delete product
                self.cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Product deleted successfully")
                self.clear_product_form()
                self.refresh_products_list()
                self.update_order_product_dropdown()
                self.status_bar.config(text=f"Product '{product_name}' deleted successfully")
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
    
    def clear_product_form(self):
        self.product_id_var.set("")
        self.product_name_entry.delete(0, tk.END)
        self.material_var.set("")
        self.quantity_entry.delete(0, tk.END)
        self.product_materials_list.delete(0, tk.END)
        self.product_materials = []
        
        self.add_product_btn.config(state=tk.NORMAL)
        self.update_product_btn.config(state=tk.DISABLED)
        self.delete_product_btn.config(state=tk.DISABLED)
    
    def on_product_select(self, event):
        try:
            index = self.products_list.curselection()[0]
            selected_item = self.products_list.get(index)
            
            # Parse the selected item to get ID and name
            # Format is "ID: xxx | Name: xxx"
            parts = selected_item.split(" | ")
            product_id = parts[0].split(": ")[1]
            product_name = parts[1].split(": ")[1]
            
            # Fill form with selected product
            self.product_id_var.set(product_id)
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, product_name)
            
            # Clear product materials list
            self.product_materials_list.delete(0, tk.END)
            self.product_materials = []
            
            # Get materials for this product
            self.cursor.execute("SELECT materials FROM products WHERE product_id = ?", (product_id,))
            result = self.cursor.fetchone()
            
            if result and result[0]:
                materials_str = result[0]
                materials_list = materials_str.split(";")
                
                for material in materials_list:
                    parts = material.split(",")
                    if len(parts) == 3:
                        mat_id, name, qty = parts
                        self.product_materials.append((mat_id, name, int(qty)))
                        self.product_materials_list.insert(tk.END, f"{name} - Quantity: {qty}")
            
            # Enable update and delete buttons
            self.update_product_btn.config(state=tk.NORMAL)
            self.delete_product_btn.config(state=tk.NORMAL)
            self.add_product_btn.config(state=tk.DISABLED)
            
            self.status_bar.config(text=f"Product '{product_name}' selected")
            
        except IndexError:
            pass
    
    def refresh_products_list(self):
        # Clear existing items
        self.products_list.delete(0, tk.END)
        
        # Fetch all products
        self.cursor.execute("SELECT product_id, product_name FROM products")
        products = self.cursor.fetchall()
        
        # Insert into listbox
        for product_id, name in products:
            self.products_list.insert(tk.END, f"ID: {product_id} | Name: {name}")
    
    def update_order_product_dropdown(self):
        # Clear existing items
        self.order_product_dropdown['values'] = []
        
        # Fetch all products
        self.cursor.execute("SELECT product_id, product_name FROM products")
        products = self.cursor.fetchall()
        
        # Create a dictionary for easy lookup
        self.order_product_dict = {f"{name} (ID: {product_id})": product_id for product_id, name in products}
        
        # Set dropdown values
        self.order_product_dropdown['values'] = list(self.order_product_dict.keys())
    
    def calculate_order_materials(self):
        product_selection = self.order_product_var.get()
        quantity = self.order_quantity_var.get()
        
        if not product_selection:
            messagebox.showerror("Error", "Please select a product")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero")
                return
            
            # Get product ID from the dictionary
            product_id = self.order_product_dict.get(product_selection)
            if not product_id:
                messagebox.showerror("Error", "Invalid product selection")
                return
            
            # Get materials for this product
            self.cursor.execute("SELECT materials FROM products WHERE product_id = ?", (product_id,))
            result = self.cursor.fetchone()
            
            if not result or not result[0]:
                messagebox.showerror("Error", "No materials defined for this product")
                return
            
            materials_str = result[0]
            materials_list = materials_str.split(";")
            
            # Calculate materials needed
            self.order_materials_text.config(state=tk.NORMAL)
            self.order_materials_text.delete(1.0, tk.END)
            self.order_materials_text.insert(tk.END, f"Materials needed for {quantity} units:\n\n")
            
            # Clear previous requirements
            self.order_material_requirements = {}
            
            # Check inventory status
            self.inventory_status_text.config(state=tk.NORMAL)
            self.inventory_status_text.delete(1.0, tk.END)
            
            all_materials_available = True
            total_materials = []
            
            for material in materials_list:
                parts = material.split(",")
                if len(parts) == 3:
                    mat_id, name, mat_qty = parts
                    total_qty = int(mat_qty) * quantity

                    # Store in requirements dictionary
                    self.order_material_requirements[mat_id] = {
                        'name': name,
                        'required': total_qty
                    }
                    
                    # Check current inventory
                    self.cursor.execute("SELECT mat_volume FROM raw_mats WHERE mat_id = ?", (mat_id,))
                    inventory_result = self.cursor.fetchone()
                    
                    if inventory_result:
                        current_volume = inventory_result[0]
                        self.order_material_requirements[mat_id]['available'] = current_volume
                        
                        if current_volume >= total_qty:
                            status = "Available"
                        else:
                            status = f"Insufficient (short by {total_qty - current_volume})"
                            all_materials_available = False
                            
                        self.inventory_status_text.insert(tk.END, f"{name}: {current_volume} available, {total_qty} needed - {status}\n")
                    else:
                        self.inventory_status_text.insert(tk.END, f"{name}: Not found in inventory\n")
                        all_materials_available = False
                    
                    total_materials.append(f"{name}: {total_qty} units")
                    self.order_materials_text.insert(tk.END, f"{name}: {total_qty} units\n")
                
                self.order_materials_text.config(state=tk.DISABLED)
                self.inventory_status_text.config(state=tk.DISABLED)
                
                # Store materials data for order creation
                self.order_materials_data = ", ".join(total_materials)
                
                # Enable or disable create order button based on inventory status
                if all_materials_available:
                    self.create_order_btn.config(state=tk.NORMAL)
                    self.status_bar.config(text="Materials calculation complete. Ready to create order.")
                else:
                    self.create_order_btn.config(state=tk.DISABLED)
                    messagebox.showwarning("Inventory Warning", "Not enough materials in inventory to fulfill this order.")
                    self.status_bar.config(text="Insufficient materials for order.")
                
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def create_order(self):
        try:
            # Get all values directly
            order_id = str(uuid.uuid4())[:8]
            order_name = self.order_name_var.get()
            quantity = int(self.order_quantity_var.get()) 
            product_id = self.order_product_dict.get(self.order_product_var.get())
            client_id = self.client_dict.get(self.order_client_var.get())

            # Simple validation
            if not all([order_name, product_id, client_id]):
                messagebox.showerror("Input Error", "All fields are required!")
                return

            if quantity <= 0:
                messagebox.showerror("Input Error", "Quantity must be greater than 0")
                return
            
            # Deduct materials from inventory
            for mat_id, details in self.order_material_requirements.items():
                required_qty = details['required']
                
                # Update material volume in database
                self.cursor.execute(
                    "UPDATE raw_mats SET mat_volume = mat_volume - ? WHERE mat_id = ?",
                    (required_qty, mat_id)
                )

            self.cursor.execute(
                "INSERT INTO orders (order_id, order_name, order_amount, product_id, mats_used, client_id) VALUES (?, ?, ?, ?, ?, ?)",
                (order_id, order_name, quantity, product_id, self.order_materials_data, client_id)
            )
            self.conn.commit()

            messagebox.showinfo("Success", "Order created successfully")
            self.clear_order_form()
            self.refresh_orders_list()
            self.status_bar.config(text=f"Order '{order_name}' created successfully")

        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a valid number")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create order: {str(e)}")
            self.conn.rollback()

    def clear_order_form(self):
        self.order_id_var.set("")
        self.order_name_var.set("")
        self.order_product_var.set("")
        self.order_client_var.set("")
        self.order_quantity_var.set("")
    
    def refresh_orders_list(self):
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        try:
            # Fetch all orders with product names
            self.cursor.execute("""
                SELECT o.order_id, o.order_name, p.product_name, o.order_amount, o.order_date
                FROM orders o
                LEFT JOIN products p ON o.product_id = p.product_id
                ORDER BY o.order_date DESC
            """)
            orders = self.cursor.fetchall()
            
            # Insert into treeview
            for order in orders:
                self.orders_tree.insert("", tk.END, values=order)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading orders: {str(e)}")
    
    def on_order_selected(self, event):
        selected_items = self.orders_tree.selection()
        if not selected_items:
            return
        
        # Get the selected order
        item = selected_items[0]
        order_id = self.orders_tree.item(item, "values")[0]
        order_name = self.orders_tree.item(item, "values")[1]
        
        # Store the order ID
        self.order_id_var.set(order_id)
        self.status_bar.config(text=f"Order '{order_name}' selected")
    
    def delete_order(self):
        order_id = self.order_id_var.get()
        
        if not order_id:
            messagebox.showerror("Error", "Please select an order to delete")
            return
        
        # Get order name for status bar update
        selected_items = self.orders_tree.selection()
        if selected_items:
            item = selected_items[0]
            order_name = self.orders_tree.item(item, "values")[1]
        else:
            order_name = "Unknown"
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this order?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Order deleted successfully")
                self.refresh_orders_list()
                self.status_bar.config(text=f"Order '{order_name}' deleted successfully")
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))

        def open_inventory(self):
            # Open the inventory system as a top-level window
            inventory_window = SimpleInventory(self)
            inventory_window.focus_set() 

# Create a main window with a button to open the inventory system
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Inventory System Launcher")
        self.geometry("400x300")
        
        # Create a frame to center the button
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)
        
        # Create a button to open the inventory system
        self.inventory_btn = tk.Button(
            center_frame, 
            text="Open Inventory System", 
            command=self.open_inventory,
            font=("Arial", 14),
            bg="#4CAF50", 
            fg="white",
            padx=20,
            pady=10
        )
        self.inventory_btn.pack(padx=20, pady=20)
        
    def open_inventory(self):
        # Open the inventory system as a top-level window
        inventory_window = SimpleInventory(self)
        inventory_window.focus_set()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
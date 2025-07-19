import tkinter as tk
from tkinter import ttk, messagebox
import re
import logging
from datetime import datetime
from database import DatabaseManager

class ProductManagementSystem:
    def __init__(self, parent, controller):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Product Management System")
        self.window.geometry("800x800")
        self.window.minsize(600, 600)
        self.window.transient(parent)
        self.window.grab_set()
        
        #Logger Files
        logging.basicConfig(filename='orders.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.order_act = logging.getLogger('ORDER_ACT')
        self.order_act.setLevel(logging.INFO)

        self.order_warn = logging.getLogger('ORDER_WARNING')
        self.order_warn.setlevel(logging.WARNING)

        self.order_error = logging.getLogger('ORDER_ERROR')
        self.order_error.setLevel(logging.ERROR)


        # Configure window style
        self.window.configure(bg='#f8f9fa')
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        

        # Initialize materials list for product creation
        self.current_materials = []
        
        # Create widgets
        self.create_widgets()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Handle window closing"""
        self.window.grab_release()
        self.window.destroy()
    
    def create_widgets(self):
        """Create the main interface widgets"""
        # Main container with padding
        main_container = tk.Frame(self.window, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Title
        title_label = tk.Label(main_container, 
                              text="Product Management System", 
                              font=('Segoe UI', 22, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 25))
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TNotebook', background='#f8f9fa', borderwidth=0)
        style.configure('Custom.TNotebook.Tab', padding=[25, 12], font=('Segoe UI', 12, 'bold'))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create Product Management tab
        self.product_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(self.product_frame, text='📦 Product Management')
        
        # Create Order Management tab
        self.order_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(self.order_frame, text='📋 Order Management')
        
        # Setup tabs
        self.setup_product_tab()
        self.setup_order_tab()
    
    def setup_product_tab(self):
        """Setup the Product Management tab"""
        # Create main scrollable canvas
        main_canvas = tk.Canvas(self.product_frame, bg='#ffffff', highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.product_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Main content container
        content_container = tk.Frame(scrollable_frame, bg='#ffffff')
        content_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Product Information Section
        product_section = tk.LabelFrame(content_container, 
                                       text="  📝 Product Information  ", 
                                       font=('Segoe UI', 16, 'bold'),
                                       bg='#ffffff',
                                       fg='#2c3e50',
                                       relief='solid',
                                       bd=2,
                                       padx=25,
                                       pady=20)
        product_section.pack(fill='x', pady=(0, 25))
        
        # Product name input
        tk.Label(product_section, 
                text="Product Name:",
                                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 8))
        
        self.product_name_var = tk.StringVar()
        product_entry = tk.Entry(product_section, 
                               textvariable=self.product_name_var, 
                               font=('Segoe UI', 12),
                               relief='solid',
                               bd=2,
                               width=60)
        product_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Materials Management Section
        materials_section = tk.LabelFrame(content_container, 
                                         text="  🔧 Materials Management  ", 
                                         font=('Segoe UI', 16, 'bold'),
                                         bg='#ffffff',
                                         fg='#2c3e50',
                                         relief='solid',
                                         bd=2,
                                         padx=25,
                                         pady=20)
        materials_section.pack(fill='both', expand=True, pady=(0, 25))
        
        # Material input section
        input_frame = tk.Frame(materials_section, bg='#ffffff')
        input_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(input_frame, 
                text="Add New Material:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 12))
        
        # Material input grid
        input_grid = tk.Frame(input_frame, bg='#ffffff')
        input_grid.pack(fill='x')
        
        input_grid.columnconfigure(1, weight=3)
        input_grid.columnconfigure(3, weight=1)
        
        tk.Label(input_grid, 
                text="Material Name:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#2c3e50').grid(row=0, column=0, sticky='w', padx=(0, 15), pady=8)
        
        self.material_name_var = tk.StringVar()
        material_entry = tk.Entry(input_grid, 
                                 textvariable=self.material_name_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2)
        material_entry.grid(row=0, column=1, sticky='ew', padx=(0, 25), pady=8, ipady=6)
        
        tk.Label(input_grid, 
                text="Quantity:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#2c3e50').grid(row=0, column=2, sticky='w', padx=(0, 15), pady=8)
        
        self.material_quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(input_grid, 
                                 textvariable=self.material_quantity_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2,
                                 width=18)
        quantity_entry.grid(row=0, column=3, sticky='ew', padx=(0, 25), pady=8, ipady=6)
        
        add_btn = tk.Button(input_grid, 
                           text="➕ Add Material", 
                           command=self.add_material,
                           font=('Segoe UI', 11, 'bold'),
                           bg='#27ae60',
                           fg='white',
                           relief='flat',
                           cursor='hand2',
                           padx=20,
                           pady=8)
        add_btn.grid(row=0, column=4, padx=(15, 0), pady=8)
        
        # Materials list section
        list_frame = tk.Frame(materials_section, bg='#ffffff')
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(list_frame, 
                text="Current Materials List:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 12))
        
        # Listbox with scrollbar
        listbox_container = tk.Frame(list_frame, bg='#ffffff', relief='solid', bd=2)
        listbox_container.pack(fill='both', expand=True)
        
        self.materials_listbox = tk.Listbox(listbox_container, 
                                           font=('Segoe UI', 11),
                                           relief='flat',
                                           bd=0,
                                           selectmode=tk.SINGLE,
                                           height=10,
                                           bg='#f8f9fa')
        materials_scrollbar = ttk.Scrollbar(listbox_container, orient="vertical", command=self.materials_listbox.yview)
        self.materials_listbox.configure(yscrollcommand=materials_scrollbar.set)
        
        self.materials_listbox.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        materials_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Action buttons section
        action_section = tk.Frame(content_container, bg='#ffffff')
        action_section.pack(fill='x', pady=25)
        
        button_style = {
            'font': ('Segoe UI', 12, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 25,
            'pady': 12
        }
        
        remove_btn = tk.Button(action_section, 
                              text="🗑️ Remove Selected", 
                              command=self.remove_material,
                              bg='#e74c3c',
                              fg='white',
                              **button_style)
        remove_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        create_btn = tk.Button(action_section, 
                              text="✅ Create Product", 
                              command=self.create_product,
                              bg='#3498db',
                              fg='white',
                              **button_style)
        create_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        view_btn = tk.Button(action_section, 
                            text="📋 View All Products", 
                            command=self.show_product_list,
                            bg='#9b59b6',
                            fg='white',
                            **button_style)
        view_btn.pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_order_tab(self):
        """Setup the Order Management tab"""
        # Create main scrollable canvas
        main_canvas = tk.Canvas(self.order_frame, bg='#ffffff', highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.order_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Main content container
        content_container = tk.Frame(scrollable_frame, bg='#ffffff')
        content_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Order Information Section
        order_section = tk.LabelFrame(content_container, 
                                     text="  📋 Order Information  ",
                                     font=('Segoe UI', 16, 'bold'),
                                     bg='#ffffff',
                                     fg='#2c3e50',
                                     relief='solid',
                                     bd=2,
                                     padx=25,
                                     pady=20)
        order_section.pack(fill='x', pady=(0, 25))
        
        # Order name input
        tk.Label(order_section, 
                text="Order Name:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 8))
        
        self.order_name_var = tk.StringVar()
        order_entry = tk.Entry(order_section, 
                              textvariable=self.order_name_var, 
                              font=('Segoe UI', 12),
                              relief='solid',
                              bd=2,
                              width=60)
        order_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Selection Section
        selection_section = tk.LabelFrame(content_container, 
                                         text="  🎯 Product & Client Selection  ",
                                         font=('Segoe UI', 16, 'bold'),
                                         bg='#ffffff',
                                         fg='#2c3e50',
                                         relief='solid',
                                         bd=2,
                                         padx=25,
                                         pady=20)
        selection_section.pack(fill='x', pady=(0, 25))
        
        # Product selection
        tk.Label(selection_section, 
                text="Select Product:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 8))
        
        self.selected_product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(selection_section, 
                                         textvariable=self.selected_product_var, 
                                         state="readonly", 
                                         font=('Segoe UI', 11),
                                         width=70)
        self.product_combo.pack(fill='x', pady=(0, 15), ipady=6)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        # Client selection
        tk.Label(selection_section, 
                text="Select Client:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 8))
        
        self.selected_client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(selection_section, 
                                        textvariable=self.selected_client_var, 
                                        state="readonly", 
                                        font=('Segoe UI', 11),
                                        width=70)
        self.client_combo.pack(fill='x', pady=(0, 15), ipady=6)
        
        # Order Details Section
        details_section = tk.LabelFrame(content_container, 
                                       text="  📊 Order Details  ",
                                       font=('Segoe UI', 16, 'bold'),
                                       bg='#ffffff',
                                       fg='#2c3e50',
                                       relief='solid',
                                       bd=2,
                                       padx=25,
                                       pady=20)
        details_section.pack(fill='x', pady=(0, 25))
        
        # Details grid
        details_grid = tk.Frame(details_section, bg='#ffffff')
        details_grid.pack(fill='x', pady=(0, 15))
        
        # Configure grid weights
        details_grid.columnconfigure(1, weight=1)
        details_grid.columnconfigure(3, weight=1)
        
        tk.Label(details_grid, 
                text="Quantity:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').grid(row=0, column=0, sticky='w', padx=(0, 15), pady=8)
        
        self.order_quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(details_grid, 
                                 textvariable=self.order_quantity_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2,
                                 width=25)
        quantity_entry.grid(row=0, column=1, sticky='ew', padx=(0, 30), pady=8, ipady=6)
        quantity_entry.bind('<KeyRelease>', self.on_quantity_changed)
        
        tk.Label(details_grid, 
                text="Deadline:", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').grid(row=0, column=2, sticky='w', padx=(0, 15), pady=8)
        
        self.order_deadline_var = tk.StringVar()
        deadline_entry = tk.Entry(details_grid, 
                                 textvariable=self.order_deadline_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2,
                                 width=25)
        deadline_entry.grid(row=0, column=3, sticky='ew', padx=(0, 20), pady=8, ipady=6)
        
        # Calculate button
        calc_btn = tk.Button(details_grid, 
                            text="🧮 Calculate Materials", 
                            command=self.calculate_materials,
                            font=('Segoe UI', 11, 'bold'),
                            bg='#f39c12',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=8)
        calc_btn.grid(row=0, column=4, padx=(15, 0), pady=8)
        
        # Materials Calculation Section
        calc_section = tk.LabelFrame(content_container, 
                                    text="  🔬 Materials Calculation  ",
                                    font=('Segoe UI', 16, 'bold'),
                                    bg='#ffffff',
                                    fg='#2c3e50',
                                    relief='solid',
                                    bd=2,
                                    padx=25,
                                    pady=20)
        calc_section.pack(fill='both', expand=True, pady=(0, 25))
        
        # Product materials display
        tk.Label(calc_section, 
                text="Product Materials (per unit):", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 8))
        
        product_materials_container = tk.Frame(calc_section, bg='#ffffff', relief='solid', bd=2)
        product_materials_container.pack(fill='x', pady=(0, 20))
        
        self.product_materials_text = tk.Text(product_materials_container, 
                                             height=5, 
                                             state='disabled', 
                                             bg='#f8f9fa',
                                             font=('Segoe UI', 10),
                                             relief='flat',
                                             bd=0,
                                             wrap=tk.WORD)
        
        product_scrollbar = ttk.Scrollbar(product_materials_container, orient="vertical", command=self.product_materials_text.yview)
        self.product_materials_text.configure(yscrollcommand=product_scrollbar.set)
        
        self.product_materials_text.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Required materials display
        tk.Label(calc_section, 
                text="Required Materials (total):", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(10, 8))
        
        required_materials_container = tk.Frame(calc_section, bg='#ffffff', relief='solid', bd=2)
        required_materials_container.pack(fill='both', expand=True)
        
        self.required_materials_text = tk.Text(required_materials_container, 
                                              height=5, 
                                              state='disabled', 
                                              bg='#e8f5e8',
                                              font=('Segoe UI', 10),
                                              relief='flat',
                                              bd=0,
                                              wrap=tk.WORD)
        
        required_scrollbar = ttk.Scrollbar(required_materials_container, orient="vertical", command=self.required_materials_text.yview)
        self.required_materials_text.configure(yscrollcommand=required_scrollbar.set)
        
        self.required_materials_text.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        required_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Action buttons section
        order_action_section = tk.Frame(content_container, bg='#ffffff')
        order_action_section.pack(fill='x', pady=25)
        
        button_style = {
            'font': ('Segoe UI', 12, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 25,
            'pady': 12
        }
        
        create_order_btn = tk.Button(order_action_section, 
                                    text="✅ Create Order", 
                                    command=self.create_order,
                                    bg='#27ae60',
                                    fg='white',
                                    **button_style)
        create_order_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        view_orders_btn = tk.Button(order_action_section, 
                                   text="📋 View All Orders", 
                                   command=self.show_order_list,
                                   bg='#8e44ad',
                                   fg='white',
                                   **button_style)
        view_orders_btn.pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel_order(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel_order)
        
        # Load products and clients for dropdowns
        self.load_products_and_clients()
    
    def on_product_selected(self, event=None):
        """Handle product selection change"""
        self.display_product_materials()
        self.calculate_materials()
    
    def on_quantity_changed(self, event=None):
        """Handle quantity change"""
        self.calculate_materials()
    
    def display_product_materials(self):
        """Display the materials for the selected product"""
        selected_product = self.selected_product_var.get().strip()
        if not selected_product:
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.config(state='disabled')
            return
        
        try:
            # Extract product ID from selection
            product_id = selected_product.split('(')[-1].strip(')')
            materials = self.db_manager.get_product_materials(product_id)
            
            if materials:
                self.product_materials_text.config(state='normal')
                self.product_materials_text.delete(1.0, tk.END)
                self.product_materials_text.insert(1.0, materials)
                self.product_materials_text.config(state='disabled')
            else:
                self.product_materials_text.config(state='normal')
                self.product_materials_text.delete(1.0, tk.END)
                self.product_materials_text.insert(1.0, "No materials found for this product.")
                self.product_materials_text.config(state='disabled')
                
        except Exception as e:
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.insert(1.0, f"Error loading materials: {str(e)}")
            self.product_materials_text.config(state='disabled')
    
    def parse_materials(self, materials_string):
        """Parse materials string and extract material names and quantities"""
        if not materials_string:
            return []
        
        materials = []
        # Split by semicolon or comma
        items = re.split(r'[;,]', materials_string)
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # Try to extract material name and quantity
            # Format: "Material Name - Quantity" or "Material Name: Quantity"
            match = re.search(r'(.+?)\s*[-:]\s*([0-9]+)', item)
            if match:
                material_name = match.group(1).strip()
                try:
                    quantity = int(match.group(2))
                    materials.append((material_name, quantity))
                except ValueError:
                    # If quantity parsing fails, treat as text
                    materials.append((item, 0))
            else:
                # If no quantity found, treat as text with 0 quantity
                materials.append((item, 0))
        
        return materials

    def calculate_materials(self):
        """Calculate required materials based on quantity"""
        selected_product = self.selected_product_var.get().strip()
        quantity_str = self.order_quantity_var.get().strip()
        
        if not selected_product or not quantity_str:
            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.insert(1.0, "Please select a product and enter quantity to calculate materials.")
            self.required_materials_text.config(state='disabled')
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.insert(1.0, "Please enter a valid positive whole number for quantity.")
            self.required_materials_text.config(state='disabled')
            return
        
        try:
            # Extract product ID from selection
            product_id = selected_product.split('(')[-1].strip(')')
            materials_string = self.db_manager.get_product_materials(product_id)
            
            if materials_string:
                materials_list = self.parse_materials(materials_string)
                
                if materials_list:
                    calculation_text = f"For {quantity} units:\n\n"
                    
                    for material_name, unit_quantity in materials_list:
                        if unit_quantity > 0:
                            total_needed = unit_quantity * quantity
                            calculation_text += f"• {material_name}: {unit_quantity} × {quantity} = {total_needed}\n"
                        else:
                            calculation_text += f"• {material_name}: (quantity not specified)\n"
                    
                    self.required_materials_text.config(state='normal')
                    self.required_materials_text.delete(1.0, tk.END)
                    self.required_materials_text.insert(1.0, calculation_text)
                    self.required_materials_text.config(state='disabled')
                else:
                    self.required_materials_text.config(state='normal')
                    self.required_materials_text.delete(1.0, tk.END)
                    self.required_materials_text.insert(1.0, "No materials found or materials format not recognized.")
                    self.required_materials_text.config(state='disabled')
            else:
                self.required_materials_text.config(state='normal')
                self.required_materials_text.delete(1.0, tk.END)
                self.required_materials_text.insert(1.0, "No materials found for this product.")
                self.required_materials_text.config(state='disabled')
                
        except Exception as e:
            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.insert(1.0, f"Error calculating materials: {str(e)}")
            self.required_materials_text.config(state='disabled')
    
    def add_material(self):
        """Add material to the current materials list"""
        material_name = self.material_name_var.get().strip()
        material_quantity = self.material_quantity_var.get().strip()
        
        if not material_name or not material_quantity:
            messagebox.showerror("Error", "Please enter both material name and quantity.")
            return
        
        try:
            int(material_quantity)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid whole number.")
            return
        
        material_entry = f"{material_name} - {material_quantity}"
        self.current_materials.append(material_entry)
        self.materials_listbox.insert(tk.END, material_entry)
        
        self.material_name_var.set("")
        self.material_quantity_var.set("")
        
        messagebox.showinfo("Success", f"Material '{material_name}' added successfully!")
    
    def remove_material(self):
        """Remove selected material from the list"""
        selection = self.materials_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a material to remove.")
            return
        
        index = selection[0]
        removed_material = self.current_materials.pop(index)
        self.materials_listbox.delete(index)
        
        messagebox.showinfo("Success", f"Material '{removed_material}' removed successfully!")
    
    def create_product(self):
        """Create a new product"""
        product_name = self.product_name_var.get().strip()
        
        if not product_name:
            messagebox.showerror("Error", "Please enter a product name.")
            return
        
        if not self.current_materials:
            messagebox.showerror("Error", "Please add at least one material.")
            return
        
        try:
            product_id = self.db_manager.create_product(product_name, self.current_materials)
            
            # Clear form
            self.product_name_var.set("")
            self.current_materials.clear()
            self.materials_listbox.delete(0, tk.END)
            
            # Refresh product dropdown
            self.load_products_and_clients()
            
            messagebox.showinfo("Success", f"Product '{product_name}' created successfully!\nProduct ID: {product_id}")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error creating product: {str(e)}")
    
    def edit_product(self, product_id, product_name, materials):
        """Edit an existing product"""
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Product")
        edit_window.geometry("800x600")
        edit_window.minsize(700, 500)
        edit_window.transient(self.window)
        edit_window.grab_set()
        edit_window.configure(bg='#f8f9fa')
        
        # Main container
        main_frame = tk.Frame(edit_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="✏️ Edit Product", 
                              font=('Segoe UI', 16, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Product name section
        name_frame = tk.LabelFrame(main_frame, 
                                  text="Product Information", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#ffffff',
                                  fg='#2c3e50',
                                  relief='solid',
                                  bd=1,
                                  padx=20,
                                  pady=15)
        name_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(name_frame, 
                text="Product Name:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 5))
        
        edit_name_var = tk.StringVar(value=product_name)
        name_entry = tk.Entry(name_frame, 
                             textvariable=edit_name_var, 
                             font=('Segoe UI', 11),
                             relief='solid',
                             bd=2,
                             width=60)
        name_entry.pack(fill='x', pady=(0, 10), ipady=6)
        
        # Materials section
        materials_frame = tk.LabelFrame(main_frame, 
                                       text="Materials", 
                                       font=('Segoe UI', 12, 'bold'),
                                       bg='#ffffff',
                                       fg='#2c3e50',
                                       relief='solid',
                                       bd=1,
                                       padx=20,
                                       pady=15)
        materials_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        tk.Label(materials_frame, 
                text="Materials (one per line, format: Material Name - Quantity):", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 5))
        
        # Text area for materials
        text_container = tk.Frame(materials_frame, bg='#ffffff', relief='solid', bd=2)
        text_container.pack(fill='both', expand=True)
        
        edit_materials_text = tk.Text(text_container, 
                                     font=('Segoe UI', 10),
                                     relief='flat',
                                     bd=0,
                                     wrap=tk.WORD,
                                     bg='#f8f9fa')
        
        materials_scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=edit_materials_text.yview)
        edit_materials_text.configure(yscrollcommand=materials_scrollbar.set)
        
        # Convert materials string to readable format
        if materials:
            formatted_materials = materials.replace('; ', '\n')
            edit_materials_text.insert(1.0, formatted_materials)
        
        edit_materials_text.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        materials_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=20)
        
        def save_changes():
            new_name = edit_name_var.get().strip()
            new_materials = edit_materials_text.get(1.0, tk.END).strip()
            
            if not new_name:
                messagebox.showerror("Error", "Please enter a product name.")
                return
            
            if not new_materials:
                messagebox.showerror("Error", "Please enter materials.")
                return
            
            # Convert back to semicolon format
            materials_list = [line.strip() for line in new_materials.split('\n') if line.strip()]
            formatted_materials = '; '.join(materials_list)
            
            try:
                self.db_manager.update_product(product_id, new_name, formatted_materials)
                
                # Refresh product dropdown
                self.load_products_and_clients()
                
                messagebox.showinfo("Success", "Product updated successfully!")
                edit_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating product: {str(e)}")
        
        save_btn = tk.Button(button_frame, 
                            text="💾 Save Changes", 
                            command=save_changes,
                            font=('Segoe UI', 11, 'bold'),
                            bg='#27ae60',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=8)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel", 
                              command=edit_window.destroy,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#95a5a6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=20,
                              pady=8)
        cancel_btn.pack(side=tk.LEFT)
    
    def delete_product(self, product_id, product_name):
        """Delete a product"""
        # Check if product is used in any orders
        try:
            order_count = self.db_manager.check_product_in_orders(product_id)
            
            if order_count > 0:
                messagebox.showwarning("Cannot Delete", 
                                     f"Cannot delete product '{product_name}' because it is used in {order_count} order(s).\n\n"
                                     "Please delete or update the related orders first.")
                return
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Deletion", 
                                 f"Are you sure you want to delete the product '{product_name}'?\n\n"
                                 "This action cannot be undone."):
                
                self.db_manager.delete_product(product_id)
                
                # Refresh product dropdown
                self.load_products_and_clients()
                
                messagebox.showinfo("Success", f"Product '{product_name}' deleted successfully!")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error deleting product: {str(e)}")
    
    def show_product_list(self):
        """Show product list in a popup window with edit and delete functionality"""
        popup = tk.Toplevel(self.window)
        popup.title("Product List")
        popup.geometry("1200x700")
        popup.minsize(1000, 600)
        popup.transient(self.window)
        popup.grab_set()
        popup.configure(bg='#f8f9fa')
        
        # Main container
        main_frame = tk.Frame(popup, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📦 Product List", 
                              font=('Segoe UI', 16, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Treeview frame
        tree_frame = tk.Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        tree_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create Treeview for product display
        columns = ('ID', 'Name', 'Materials', 'Created Date')
        product_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure headings
        product_tree.heading('ID', text='Product ID')
        product_tree.heading('Name', text='Product Name')
        product_tree.heading('Materials', text='Materials')
        product_tree.heading('Created Date', text='Created Date')
        
        # Configure columns
        product_tree.column('ID', width=150, minwidth=120)
        product_tree.column('Name', width=200, minwidth=150)
        product_tree.column('Materials', width=400, minwidth=300)
        product_tree.column('Created Date', width=150, minwidth=120)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=product_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=product_tree.xview)
        product_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        product_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Load products
        def load_products():
            # Clear existing items
            for item in product_tree.get_children():
                product_tree.delete(item)
                
            try:
                products = self.db_manager.get_all_products()
                
                for product in products:
                    product_id, name, materials, created_date = product
                    
                    if created_date:
                        try:
                            dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S.%f')
                            formatted_date = dt.strftime('%m/%d/%Y')
                        except:
                            try:
                                dt = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                                formatted_date = dt.strftime('%m/%d/%Y')
                            except:
                                formatted_date = created_date
                    else:
                        formatted_date = 'N/A'
                    
                    display_materials = materials[:50] + "..." if materials and len(materials) > 50 else materials or 'N/A'
                    
                    product_tree.insert('', 'end', values=(
                        product_id or 'N/A',
                        name or 'N/A',
                        display_materials,
                        formatted_date
                    ))
                    
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading products: {str(e)}")
        
        load_products()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=10)
        
        def edit_selected_product():
            selection = product_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a product to edit.")
                return
            
            item = product_tree.item(selection[0])
            values = item['values']
            product_id = values[0]
            product_name = values[1]
            
            # Get full materials from database
            try:
                materials = self.db_manager.get_product_materials(product_id)
                self.edit_product(product_id, product_name, materials)
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading product details: {str(e)}")
        
        def delete_selected_product():
            selection = product_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a product to delete.")
                return
            
            item = product_tree.item(selection[0])
            values = item['values']
            product_id = values[0]
            product_name = values[1]
            
            self.delete_product(product_id, product_name)
            load_products()  # Refresh the list
        
        def refresh_products():
            load_products()
        
        # Action buttons
        edit_btn = tk.Button(button_frame, 
                            text="✏️ Edit Selected", 
                            command=edit_selected_product,
                            font=('Segoe UI', 11, 'bold'),
                            bg='#f39c12',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=8)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = tk.Button(button_frame, 
                              text="🗑️ Delete Selected", 
                              command=delete_selected_product,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#e74c3c',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=20,
                              pady=8)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(button_frame, 
                               text="🔄 Refresh", 
                               command=refresh_products,
                               font=('Segoe UI', 11, 'bold'),
                               bg='#3498db',
                               fg='white',
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(button_frame, 
                             text="❌ Close", 
                             command=popup.destroy,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#95a5a6',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             padx=20,
                             pady=8)
        close_btn.pack(side=tk.LEFT)
    
    def load_products_and_clients(self):
        """Load products and clients for the order form dropdowns"""
        try:
            # Load products
            product_options = self.db_manager.get_products_for_dropdown()
            self.product_combo['values'] = product_options
            
            # Load clients
            client_options = self.db_manager.get_clients_for_dropdown()
            self.client_combo['values'] = client_options
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading products and clients: {str(e)}")
    
    def create_order(self):
        """Create a new order"""
        order_name = self.order_name_var.get().strip()
        selected_product = self.selected_product_var.get().strip()
        selected_client = self.selected_client_var.get().strip()
        quantity = self.order_quantity_var.get().strip()
        deadline = self.order_deadline_var.get().strip()
        
        # Validation
        if not order_name:
            messagebox.showerror("Error", "Please enter an order name.")
            return
        
        if not selected_product:
            messagebox.showerror("Error", "Please select a product.")
            return
        
        if not selected_client:
            messagebox.showerror("Error", "Please select a client.")
            return
        
        if not quantity:
            messagebox.showerror("Error", "Please enter quantity.")
            return
        
        try:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.")
            return
        
        if not deadline:
            messagebox.showerror("Error", "Please enter a deadline.")
            return
        
        try:
            # Extract product ID from selection
            product_id = selected_product.split('(')[-1].strip(')')
            
            # Extract client ID from selection
            client_id = selected_client.split('(')[-1].strip(')')
            
            # Create order
            order_id = self.db_manager.create_order(order_name, product_id, client_id, quantity_int, deadline)
            
            # Clear form
            self.order_name_var.set("")
            self.selected_product_var.set("")
            self.selected_client_var.set("")
            self.order_quantity_var.set("")
            self.order_deadline_var.set("")
            
            # Clear calculation displays
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.config(state='disabled')
            
            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.config(state='disabled')
            
            messagebox.showinfo("Success", f"Order '{order_name}' created successfully!\nOrder ID: {order_id}")
                        
        except Exception as e:
            messagebox.showerror("Database Error", f"Error creating order: {str(e)}")
    
    def edit_order(self, order_id, order_name, product_id, client_id, quantity, deadline):
        """Edit an existing order"""
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Order")
        edit_window.geometry("700x500")
        edit_window.minsize(600, 400)
        edit_window.transient(self.window)
        edit_window.grab_set()
        edit_window.configure(bg='#f8f9fa')
        
        # Main container
        main_frame = tk.Frame(edit_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="✏️ Edit Order", 
                              font=('Segoe UI', 16, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Order information section
        info_frame = tk.LabelFrame(main_frame, 
                                  text="Order Information", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#ffffff',
                                  fg='#2c3e50',
                                  relief='solid',
                                  bd=1,
                                  padx=20,
                                  pady=15)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Order name
        tk.Label(info_frame, 
                text="Order Name:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 5))
        
        edit_order_name_var = tk.StringVar(value=order_name)
        order_name_entry = tk.Entry(info_frame, 
                                   textvariable=edit_order_name_var, 
                                   font=('Segoe UI', 11),
                                   relief='solid',
                                   bd=2,
                                   width=50)
        order_name_entry.pack(fill='x', pady=(0, 15), ipady=6)
        
        # Product selection
        tk.Label(info_frame, 
                text="Select Product:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 5))
        
        edit_product_var = tk.StringVar()
        edit_product_combo = ttk.Combobox(info_frame, 
                                         textvariable=edit_product_var, 
                                         state="readonly", 
                                         font=('Segoe UI', 10),
                                         width=60)
        edit_product_combo.pack(fill='x', pady=(0, 15), ipady=6)
        
        # Client selection
        tk.Label(info_frame, 
                text="Select Client:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').pack(anchor='w', pady=(0, 5))
        
        edit_client_var = tk.StringVar()
        edit_client_combo = ttk.Combobox(info_frame, 
                                        textvariable=edit_client_var, 
                                        state="readonly", 
                                        font=('Segoe UI', 10),
                                        width=60)
        edit_client_combo.pack(fill='x', pady=(0, 15), ipady=6)
        
        # Details section
        details_frame = tk.LabelFrame(main_frame, 
                                     text="Order Details", 
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#ffffff',
                                     fg='#2c3e50',
                                     relief='solid',
                                     bd=1,
                                     padx=20,
                                     pady=15)
        details_frame.pack(fill='x', pady=(0, 20))
        
        # Quantity and deadline in grid
        details_grid = tk.Frame(details_frame, bg='#ffffff')
        details_grid.pack(fill='x')
        details_grid.columnconfigure(1, weight=1)
        details_grid.columnconfigure(3, weight=1)
        
        tk.Label(details_grid, 
                text="Quantity:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').grid(row=0, column=0, sticky='w', padx=(0, 15), pady=8)
        
        edit_quantity_var = tk.StringVar(value=str(quantity))
        quantity_entry = tk.Entry(details_grid, 
                                 textvariable=edit_quantity_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2,
                                 width=20)
        quantity_entry.grid(row=0, column=1, sticky='ew', padx=(0, 30), pady=8, ipady=6)
        
        tk.Label(details_grid, 
                text="Deadline:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#ffffff',
                fg='#34495e').grid(row=0, column=2, sticky='w', padx=(0, 15), pady=8)
        
        edit_deadline_var = tk.StringVar(value=deadline)
        deadline_entry = tk.Entry(details_grid, 
                                 textvariable=edit_deadline_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid',
                                 bd=2,
                                 width=20)
        deadline_entry.grid(row=0, column=3, sticky='ew', pady=8, ipady=6)
        
        # Load products and clients for dropdowns
        try:
            # Load products
            product_options = self.db_manager.get_products_for_dropdown()
            edit_product_combo['values'] = product_options
            
            # Set current product
            for option in product_options:
                if product_id in option:
                    edit_product_var.set(option)
                    break
            
            # Load clients
            client_options = self.db_manager.get_clients_for_dropdown()
            edit_client_combo['values'] = client_options
            
            # Set current client
            for option in client_options:
                if client_id in option:
                    edit_client_var.set(option)
                    break
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=20)
        
        def save_order_changes():
            new_order_name = edit_order_name_var.get().strip()
            new_product = edit_product_var.get().strip()
            new_client = edit_client_var.get().strip()
            new_quantity = edit_quantity_var.get().strip()
            new_deadline = edit_deadline_var.get().strip()
            
            # Validation
            if not new_order_name:
                messagebox.showerror("Error", "Please enter an order name.")
                return
            
            if not new_product:
                messagebox.showerror("Error", "Please select a product.")
                return
            
            if not new_client:
                messagebox.showerror("Error", "Please select a client.")
                return
            
            if not new_quantity:
                messagebox.showerror("Error", "Please enter quantity.")
                return
            
            try:
                quantity_int = int(new_quantity)
                if quantity_int <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive whole number.")
                return
            
            if not new_deadline:
                messagebox.showerror("Error", "Please enter a deadline.")
                return
            
            try:
                # Extract IDs from selections
                new_product_id = new_product.split('(')[-1].strip(')')
                new_client_id = new_client.split('(')[-1].strip(')')
                
                self.db_manager.update_order(order_id, new_order_name, new_product_id, new_client_id, quantity_int, new_deadline)
                
                messagebox.showinfo("Success", "Order updated successfully!")
                edit_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating order: {str(e)}")
        
        save_btn = tk.Button(button_frame, 
                            text="💾 Save Changes", 
                            command=save_order_changes,
                            font=('Segoe UI', 11, 'bold'),
                            bg='#27ae60',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=8)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel", 
                              command=edit_window.destroy,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#95a5a6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=20,
                              pady=8)
        cancel_btn.pack(side=tk.LEFT)
    
    def delete_order(self, order_id, order_name):
        """Delete an order"""
        if messagebox.askyesno("Confirm Deletion", 
                             f"Are you sure you want to delete the order '{order_name}'?\n\n"
                             "This action cannot be undone."):
            try:
                self.db_manager.delete_order(order_id)
                messagebox.showinfo("Success", f"Order '{order_name}' deleted successfully!")
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting order: {str(e)}")
    
    def show_order_list(self):
        """Show order list in a popup window with edit and delete functionality"""
        popup = tk.Toplevel(self.window)
        popup.title("Order List")
        popup.geometry("1300x700")
        popup.minsize(1100, 600)
        popup.transient(self.window)
        popup.grab_set()
        popup.configure(bg='#f8f9fa')
        
        # Main container
        main_frame = tk.Frame(popup, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📋 Order List", 
                              font=('Segoe UI', 16, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Treeview frame
        tree_frame = tk.Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        tree_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create Treeview for order display
        columns = ('ID', 'Name', 'Product', 'Client', 'Quantity', 'Deadline', 'Order Date')
        order_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure headings
        order_tree.heading('ID', text='Order ID')
        order_tree.heading('Name', text='Order Name')
        order_tree.heading('Product', text='Product')
        order_tree.heading('Client', text='Client')
        order_tree.heading('Quantity', text='Quantity')
        order_tree.heading('Deadline', text='Deadline')
        order_tree.heading('Order Date', text='Order Date')
        
        # Configure columns
        order_tree.column('ID', width=120, minwidth=100)
        order_tree.column('Name', width=150, minwidth=120)
        order_tree.column('Product', width=150, minwidth=120)
        order_tree.column('Client', width=150, minwidth=120)
        order_tree.column('Quantity', width=80, minwidth=60)
        order_tree.column('Deadline', width=120, minwidth=100)
        order_tree.column('Order Date', width=120, minwidth=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=order_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=order_tree.xview)
        order_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        order_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Load orders
        def load_orders():
            # Clear existing items
            for item in order_tree.get_children():
                order_tree.delete(item)
                
            try:
                orders = self.db_manager.get_all_orders()
                
                for order in orders:
                    order_id, name, product_name, client_name, quantity, deadline, order_date, product_id, client_id = order
                    
                    if order_date:
                        try:
                            dt = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S.%f')
                            formatted_date = dt.strftime('%m/%d/%Y')
                        except:
                            try:
                                dt = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
                                formatted_date = dt.strftime('%m/%d/%Y')
                            except:
                                formatted_date = order_date
                    else:
                        formatted_date = 'N/A'
                    
                    # Store additional data in tags for edit/delete operations
                    item_id = order_tree.insert('', 'end', values=(
                        order_id or 'N/A',
                        name or 'N/A',
                        product_name or 'N/A',
                        client_name or 'N/A',
                        quantity or 'N/A',
                        deadline or 'N/A',
                        formatted_date
                    ), tags=(product_id, client_id))
                    
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading orders: {str(e)}")
        
        load_orders()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(pady=10)
        
        def edit_selected_order():
            selection = order_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an order to edit.")
                return
            
            item = order_tree.item(selection[0])
            values = item['values']
            tags = item['tags']
            
            order_id = values[0]
            order_name = values[1]
            quantity = values[4]
            deadline = values[5]
            product_id = tags[0] if tags else ""
            client_id = tags[1] if len(tags) > 1 else ""
            
            self.edit_order(order_id, order_name, product_id, client_id, quantity, deadline)
            load_orders()  # Refresh the list
        
        def delete_selected_order():
            selection = order_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an order to delete.")
                return
            
            item = order_tree.item(selection[0])
            values = item['values']
            order_id = values[0]
            order_name = values[1]
            
            self.delete_order(order_id, order_name)
            load_orders()  # Refresh the list
        
        def refresh_orders():
            load_orders()
        
        # Action buttons
        edit_btn = tk.Button(button_frame, 
                            text="✏️ Edit Selected", 
                            command=edit_selected_order,
                            font=('Segoe UI', 11, 'bold'),
                            bg='#f39c12',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=8)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = tk.Button(button_frame, 
                              text="🗑️ Delete Selected", 
                              command=delete_selected_order,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#e74c3c',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=20,
                              pady=8)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(button_frame, 
                               text="🔄 Refresh", 
                               command=refresh_orders,
                               font=('Segoe UI', 11, 'bold'),
                               bg='#3498db',
                               fg='white',
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(button_frame, 
                             text="❌ Close", 
                             command=popup.destroy,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#95a5a6',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             padx=20,
                             pady=8)
        close_btn.pack(side=tk.LEFT)


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Management System")
        self.root.geometry("500x400")
        self.root.minsize(400, 300)
        self.root.configure(bg='#f8f9fa')
        
        # Center the window
        self.center_window()
        
        # Create main menu interface
        self.create_main_menu()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_main_menu(self):
        """Create the main menu interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title section
        title_frame = tk.Frame(main_container, bg='#f8f9fa')
        title_frame.pack(pady=(20, 40))
        
        # App icon/logo placeholder
        icon_label = tk.Label(title_frame, 
                             text="📦", 
                             font=('Segoe UI', 48),
                             bg='#f8f9fa')
        icon_label.pack(pady=(0, 10))
        
        title_label = tk.Label(title_frame, 
                              text="Product Management System", 
                              font=('Segoe UI', 20, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Manage Products, Orders & Materials", 
                                 font=('Segoe UI', 12),
                                 bg='#f8f9fa',
                                 fg='#7f8c8d')
        subtitle_label.pack(pady=(5, 0))
        
        # Buttons section
        buttons_frame = tk.Frame(main_container, bg='#f8f9fa')
        buttons_frame.pack(pady=30, fill='x')
        
        # Product Management System button
        product_btn = tk.Button(buttons_frame,
                               text="🚀 Open Product Management",
                               font=('Segoe UI', 14, 'bold'),
                               bg='#3498db',
                               fg='white',
                               width=30,
                               height=2,
                               relief='flat',
                               bd=0,
                               cursor='hand2',
                               command=self.open_product_management)
        product_btn.pack(pady=15)
        
        # Add hover effects
        def on_enter(e):
            product_btn.config(bg='#2980b9')
        
        def on_leave(e):
            product_btn.config(bg='#3498db')
        
        product_btn.bind("<Enter>", on_enter)
        product_btn.bind("<Leave>", on_leave)
        
        # Info section
        info_frame = tk.LabelFrame(main_container, 
                                  text="Features", 
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#ffffff',
                                  fg='#2c3e50',
                                  relief='solid',
                                  bd=1,
                                  padx=20,
                                  pady=15)
        info_frame.pack(fill='x', pady=(20, 30))
        
        features = [
            "📦 Create and manage products with materials",
            "📋 Process orders with automatic material calculation",
            "👥 Client management system",
            "📊 View comprehensive reports and lists",
            "✏️ Edit and update existing products and orders",
            "🗑️ Delete products and orders with safety checks"
        ]
        
        for feature in features:
            feature_label = tk.Label(info_frame, 
                                   text=feature, 
                                   font=('Segoe UI', 10),
                                   bg='#ffffff',
                                   fg='#34495e',
                                   anchor='w')
            feature_label.pack(fill='x', pady=2)
        
        # Footer section
        footer_frame = tk.Frame(main_container, bg='#f8f9fa')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        # Exit button
        exit_btn = tk.Button(footer_frame,
                            text="❌ Exit Application",
                            font=('Segoe UI', 11),
                            bg='#e74c3c',
                            fg='white',
                            width=20,
                            relief='flat',
                            bd=0,
                            cursor='hand2',
                            command=self.root.quit)
        exit_btn.pack(pady=10)
        
        def on_exit_enter(e):
            exit_btn.config(bg='#c0392b')
        
        def on_exit_leave(e):
            exit_btn.config(bg='#e74c3c')
        
        exit_btn.bind("<Enter>", on_exit_enter)
        exit_btn.bind("<Leave>", on_exit_leave)
        
        # Version info
        version_label = tk.Label(footer_frame, 
                               text="Version 2.0 - External Database Module", 
                               font=('Segoe UI', 9),
                               bg='#f8f9fa',
                               fg='#95a5a6')
        version_label.pack()
        
    def open_product_management(self):
        """Open the Product Management System"""
        try:
            ProductManagementSystem(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Product Management System: {str(e)}")


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()






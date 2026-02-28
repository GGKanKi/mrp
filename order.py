import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
import json
import traceback

# --- Pathing Setup ---
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class OrderManagementUI:
    def __init__(self, parent_frame, db_manager, session=None, controller=None, parent_window=None):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.session = session or {}
        self.controller = controller
        self.parent_window = parent_window

        # Tk variables and widgets initialized in setup
        self.order_name_var = None
        self.selected_product_var = None
        self.product_combo = None
        self.selected_client_var = None
        self.client_combo = None
        self.order_quantity_var = None
        self.deadline_var = None
        self.product_materials_text = None
        self.required_materials_text = None

        # Calculation state
        self.order_materials_data = {}
        self.shortage_report = {}
        self.schedule_info = {}


    # UI setup
    def setup(self):
        main_canvas = tk.Canvas(self.parent_frame, bg='#ffffff', highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')

        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        content_container = tk.Frame(scrollable_frame, bg='#ffffff')
        content_container.pack(fill='both', expand=True, padx=10, pady=5)

        order_section = tk.LabelFrame(content_container, text="  📋 Order Information  ", font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#2c3e50', relief='solid', bd=2, padx=10, pady=10)
        order_section.pack(fill='x', pady=(0, 10))

        selection_section = tk.LabelFrame(content_container, text="  🎯 Product & Client Selection  ", font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#2c3e50', relief='solid', bd=2, padx=10, pady=10)
        selection_section.pack(fill='x', pady=(0, 10))

        tk.Label(selection_section, text="Select Product:", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').pack(anchor='w', pady=(0, 5))

        self.selected_product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(selection_section, textvariable=self.selected_product_var, state="readonly", font=('Segoe UI', 9), width=40)
        self.product_combo.pack(fill='x', pady=(0, 8), ipady=3)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)

        tk.Label(selection_section, text="Select Client:", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').pack(anchor='w', pady=(0, 5))

        self.selected_client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(selection_section, textvariable=self.selected_client_var, state="readonly", font=('Segoe UI', 9), width=40)
        self.client_combo.pack(fill='x', pady=(0, 8), ipady=3)

        details_section = tk.LabelFrame(content_container, text="  📊 Order Details  ", font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#2c3e50', relief='solid', bd=2, padx=10, pady=10)
        details_section.pack(fill='x', pady=(0, 10))

        details_grid = tk.Frame(details_section, bg='#ffffff')
        details_grid.pack(fill='x', pady=(0, 8))
        details_grid.columnconfigure(1, weight=1)
        details_grid.columnconfigure(3, weight=1)

        tk.Label(details_grid, text="Quantity:", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').grid(row=0, column=0, sticky='w', padx=(0, 8), pady=4)
        self.order_quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(details_grid, textvariable=self.order_quantity_var, font=('Segoe UI', 9), relief='solid', bd=2, width=12)
        quantity_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=4, ipady=3)
        quantity_entry.bind('<KeyRelease>', self.on_quantity_changed)

        tk.Label(details_grid, text="Deadline:", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').grid(row=0, column=3, sticky='w', padx=(10, 8), pady=4, ipady=3)
        self.deadline_var = tk.StringVar()
        deadline_label = tk.Label(details_grid, textvariable=self.deadline_var, font=('Segoe UI', 9), bg='#f0f0f0', relief='solid', bd=1, anchor='w', padx=5)
        deadline_label.grid(row=0, column=4, sticky='ew', padx=(0, 10), pady=4, ipady=3)

        # Schedule Calculation Section
        schedule_frame = tk.Frame(details_section, bg='#ffffff')
        schedule_frame.pack(fill='x', pady=(10, 5))

        self.schedule_button = tk.Button(details_grid, text="Calculate Schedule", command=self.calculate_and_display_schedule, bg='#5dade2', fg='white', font=('Segoe UI', 9, 'bold'), relief='flat')
        self.schedule_button.grid(row=0, column=2, padx=(5, 5), pady=4, ipady=2)

        self.schedule_result_label = tk.Label(schedule_frame, text="", font=('Segoe UI', 10), bg='#ffffff', justify=tk.LEFT)
        self.schedule_result_label.pack(pady=5)

        calc_section = tk.LabelFrame(content_container, text="  🔬 Materials Calculation  ", font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#2c3e50', relief='solid', bd=2, padx=10, pady=10)
        calc_section.pack(fill='both', expand=True, pady=(0, 10))


        tk.Label(calc_section, text="Product Materials (per unit):", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').pack(anchor='w', pady=(0, 5))
        product_materials_container = tk.Frame(calc_section, bg='#ffffff', relief='solid', bd=2)
        product_materials_container.pack(fill='x', pady=(0, 10))
        self.product_materials_text = tk.Text(product_materials_container, height=3, state='disabled', bg='#f8f9fa', font=('Segoe UI', 9), relief='flat', bd=0, wrap=tk.WORD, width=40)
        product_scrollbar = ttk.Scrollbar(product_materials_container, orient="vertical", command=self.product_materials_text.yview)
        self.product_materials_text.configure(yscrollcommand=product_scrollbar.set)
        self.product_materials_text.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        tk.Label(calc_section, text="Required Materials (total):", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#34495e').pack(anchor='w', pady=(5, 5))
        required_materials_container = tk.Frame(calc_section, bg='#ffffff', relief='solid', bd=2)
        required_materials_container.pack(fill='both', expand=True)
        self.required_materials_text = tk.Text(required_materials_container, height=5, state='disabled', bg='#e8f5e8', font=('Segoe UI', 9), relief='flat', bd=0, wrap=tk.WORD, width=40)
        required_scrollbar = ttk.Scrollbar(required_materials_container, orient="vertical", command=self.required_materials_text.yview)
        self.required_materials_text.configure(yscrollcommand=required_scrollbar.set)
        self.required_materials_text.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        required_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        order_action_section = tk.Frame(content_container, bg='#ffffff')
        order_action_section.pack(fill='x', pady=10)
        button_style = {'font': ('Segoe UI', 10, 'bold'), 'relief': 'flat', 'cursor': 'hand2', 'padx': 10, 'pady': 6}

        create_order_btn = tk.Button(order_action_section, text="✅ Create Order", command=self.create_order, bg='#27ae60', fg='white', **button_style)
        create_order_btn.pack(side=tk.LEFT, padx=(0, 8))

        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")

        def _on_mousewheel_order(event):
            try:
                main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        main_canvas.bind("<MouseWheel>", _on_mousewheel_order)

        self.load_products_and_clients()

    # Event handlers and helpers
    def on_product_selected(self, event=None):
        self.display_product_materials()
        self.calculate_materials()

    def on_quantity_changed(self, event=None):
        self.calculate_materials()

    def display_product_materials(self):
        selected_product = self.selected_product_var.get().strip()
        if not selected_product:
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.config(state='disabled')
            return

        try:
            product_id = selected_product.split('(')[-1].strip(')')
            materials = self.db_manager.get_product_materials(product_id)
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.insert(1.0, materials or "No materials found for this product.")
            self.product_materials_text.config(state='disabled')
        except Exception as e:
            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.insert(1.0, f"Error loading materials: {str(e)}")
            self.product_materials_text.config(state='disabled')

    def parse_materials(self, materials_string):
        if not materials_string:
            return {}
        import re
        materials = {}
        items = re.split(r'[;,]', materials_string)
        for item in items:
            item = item.strip()
            if not item:
                continue
            match = re.match(r'(.+?)\s*[-:]\s*(\d+)', item)
            if match:
                material_name = match.group(1).strip()
                quantity = int(match.group(2))
                materials[material_name] = quantity
            else:
                materials[item] = 0
        return materials

    def calculate_materials(self):
        try:
            selected_product = self.selected_product_var.get().strip()
            quantity_str = self.order_quantity_var.get().strip()
            if not selected_product:
                raise ValueError("Please select a product")
            if not quantity_str:
                raise ValueError("Please enter quantity")
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            product_id = selected_product.split('(')[-1].strip(')')
            materials_string = self.db_manager.get_product_materials(product_id)
            if not materials_string:
                raise ValueError("No materials found for this product")
            materials_dict = self.parse_materials(materials_string)
            if not materials_dict:
                raise ValueError("Materials format not recognized")
            self.order_materials_data = {}
            
            # Calculate total needed for each material
            for material_name, unit_quantity in materials_dict.items():
                try:
                    unit_qty = float(unit_quantity)
                    total_needed = unit_qty * quantity
                    self.order_materials_data[material_name] = total_needed
                except (TypeError, ValueError):
                    self.order_materials_data[material_name] = '(invalid)'

            # Check availability and build display text
            self.shortage_report = self.db_manager.check_material_availability(self.order_materials_data)
            
            calculation_text = f"For {quantity} units:\n\n"
            has_shortfall = bool(self.shortage_report.get('insufficient'))

            for item in self.shortage_report.get('sufficient', []):
                calculation_text += f"• {item['name']}: {item['required']} needed, {item['available']} available [OK]\n"
            
            for item in self.shortage_report.get('insufficient', []):
                calculation_text += f"• {item['name']}: {item['required']} needed, {item['available']} available [SHORTFALL: {item['shortfall']}]\n"

            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.insert(1.0, calculation_text)

            # Add color coding and tags
            self.required_materials_text.tag_remove("shortfall", "1.0", tk.END)
            if has_shortfall:
                self.required_materials_text.config(bg='#ffebee') # Light red
                self.required_materials_text.tag_config("shortfall", foreground="red", font=('Segoe UI', 9, 'bold'))
                start_index = "1.0"
                while True:
                    start_index = self.required_materials_text.search("[SHORTFALL", start_index, stopindex=tk.END)
                    if not start_index:
                        break
                    end_index = f"{start_index} lineend"
                    self.required_materials_text.tag_add("shortfall", start_index, end_index)
                    start_index = end_index
            else:
                self.required_materials_text.config(bg='#e8f5e8') # Light green

            self.required_materials_text.config(state='disabled')
        except ValueError as e:
            self._show_materials_error(str(e))
        except Exception as e:
            self._show_materials_error(f"Calculation error: {str(e)}")
            print(f"Error trace: {traceback.format_exc()}")

    def _show_materials_error(self, message):
        self.required_materials_text.config(state='normal')
        self.required_materials_text.delete(1.0, tk.END)
        self.required_materials_text.insert(1.0, message)
        self.required_materials_text.config(state='disabled')

    # Data loading
    def load_products_and_clients(self):
        try:
            product_options = self.db_manager.get_products_for_dropdown()
            self.product_combo['values'] = product_options
            client_options = self.db_manager.get_clients_for_dropdown()
            self.client_combo['values'] = client_options
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading products and clients: {str(e)}")

    def calculate_and_display_schedule(self):
        """Calculates the production schedule and displays it in the UI."""
        from datetime import datetime, timedelta

        def add_workdays(start_date, days_to_add):
            """Adds business days to a given start date, skipping weekends."""
            business_days_to_add = int(days_to_add)
            current_date = start_date
            while business_days_to_add > 0:
                current_date += timedelta(days=1)
                weekday = current_date.weekday()
                if weekday < 5:  # Monday to Friday are 0-4
                    business_days_to_add -= 1
            return current_date

        try:
            selected_product = self.selected_product_var.get().strip()
            quantity_str = self.order_quantity_var.get().strip()

            if not all([selected_product, quantity_str]):
                messagebox.showerror("Input Error", "Please select a product and enter a quantity first.", parent=self.parent_window)
                return
            quantity = int(quantity_str)
            product_id = selected_product.split('(')[-1].strip(')')

            # 1. Get manufacturing time and calculate total production days
            product_details = self.db_manager.execute_custom_query("SELECT manufacturing_time_hours FROM products WHERE product_id = ?", (product_id,))
            if not product_details or not product_details[0][0]:
                raise ValueError("Manufacturing time not set for this product.")
            mfg_time_per_unit = float(product_details[0][0])
            total_prod_hours = quantity * mfg_time_per_unit
            prod_workdays = (total_prod_hours / 8) # Assuming 8-hour workdays

            # 2. Determine Production Start and End Dates (Deadline)
            prod_start_date = datetime.now().date()
            effective_workdays = max(prod_workdays, 7)  # Minimum 7 working days for deadline
            deadline_date = add_workdays(prod_start_date, effective_workdays)
            self.deadline_var.set(deadline_date.strftime('%Y-%m-%d'))

            # 4. Check Material Availability (re-use existing check)
            self.calculate_materials()
            has_shortfall = bool(self.shortage_report.get('insufficient'))
            feasibility = "Feasible" if not has_shortfall else "Infeasible (Material Shortage)"
            color = 'green' if not has_shortfall else 'red'
            notes = "All materials are available." if not has_shortfall else "Material shortfall detected. Procurement needed."

            schedule_summary = (
                f"Feasibility: {feasibility}\n"
                f"Estimated Deadline: {deadline_date.strftime('%Y-%m-%d')}\n"
                f"Required Production Time: {total_prod_hours:.1f} hours ({prod_workdays:.1f} workdays)\n"
                f"Production Must Start: {prod_start_date.strftime('%Y-%m-%d')}\n\n"
                f"Notes: {notes}"
            )

            # Store for order creation
            self.schedule_info = {'feasibility': feasibility, 'prod_start': prod_start_date, 'prod_end': deadline_date, 'deadline': deadline_date, 'notes': notes, 'material_order': None}
            self.schedule_result_label.config(text=schedule_summary, fg=color)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e), parent=self.parent_window)
        except Exception as e:
            messagebox.showerror("Scheduling Error", f"Failed to generate schedule: {str(e)}", parent=self.parent_window)

    # CRUD: Orders
    def create_order(self):
        from global_func import export_total_amount_mats
        self.calculate_materials() # Ensure latest data is checked
        selected_product = self.selected_product_var.get().strip()
        selected_client = self.selected_client_var.get().strip()
        quantity = self.order_quantity_var.get().strip()
        deadline = self.deadline_var.get().strip()

        if not selected_product:
            messagebox.showerror("Error", "Please select a product.", parent=self.parent_window)
            return
        if not selected_client:
            messagebox.showerror("Error", "Please select a client.", parent=self.parent_window)
            return

        client_name = selected_client.split('(')[0].strip()
        product_name = selected_product.split('(')[0].strip()
        order_name = f"{client_name}_{product_name}"

        if not quantity:
            messagebox.showerror("Error", "Please enter quantity.", parent=self.parent_window)
            return
        try:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.", parent=self.parent_window)
            return
        if not deadline:
            messagebox.showerror("Error", "Please calculate a schedule to set the deadline.", parent=self.parent_window)
            return
        if not hasattr(self, "order_materials_data") or not self.order_materials_data:
            self.calculate_materials()
            if not self.order_materials_data:
                messagebox.showerror("Error", "Could not calculate required materials.", parent=self.parent_window)
                return
        
        # Ensure schedule has been calculated and is feasible
        if not self.schedule_info or self.schedule_info.get('feasibility') == 'Infeasible':
             if not messagebox.askyesno("Confirm Order", "The calculated schedule is infeasible or has not been calculated. Do you want to create the order anyway?", parent=self.parent_window):
                return

        # Check for material shortage before creating the order
        if self.shortage_report.get('insufficient'):
            self._show_procurement_plan(self.shortage_report['insufficient'], deadline)
        else:
            self._finalize_order_creation() # This now handles success messages

    def _show_procurement_plan(self, insufficient_items, deadline):
        from global_func import create_email, send_email_with_attachment, load_credentials_if_logged_in, resource_path

        plan_window = tk.Toplevel(self.parent_window)
        plan_window.title("Procurement Action Required")
        plan_window.geometry("700x450")
        plan_window.grab_set()

        # --- Data processing ---
        suppliers_to_contact = {}
        for item in insufficient_items:
            supplier_id = item.get('supplier_id', 'N/A')
            supplier_info = self.db_manager.execute_custom_query("SELECT supplier_name, supplier_mail FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier_name = supplier_info[0][0] if supplier_info else "Unknown"
            supplier_email = supplier_info[0][1] if supplier_info else ""
            
            # This tree insertion is now done after the tree is created.
            
            if supplier_email:
                if supplier_email not in suppliers_to_contact:
                    suppliers_to_contact[supplier_email] = {'name': supplier_name, 'items': []}
                suppliers_to_contact[supplier_email]['items'].append(f"• {item['name']}: {item['shortfall']} units")

        def send_emails_directly():
            creds = load_credentials_if_logged_in()
            if not creds:
                messagebox.showerror('Email Error', 'Please login with Google first to send emails directly.', parent=plan_window)
                return

            sent_count = 0
            for email, data in suppliers_to_contact.items():
                subject = f"Purchase Order Request - {datetime.now().strftime('%Y-%m-%d')}"
                body = (
                    f"Dear {data['name']},\n\n"
                    f"We would like to place a purchase order for the following materials which are required for a customer order.\n"
                    + "\n".join(data['items']) +
                    f"\n\nWe need these materials to be delivered within the order's deadline of {deadline}.\n\n"
                    f"\n\nPlease provide a quote and estimated delivery date at your earliest convenience.\n\n"
                    f"Thank you,\n{self.session.get('f_name', 'Procurement Team')}"
                )
                
                try:
                    if send_email_with_attachment(creds, email, subject, body, []):
                        sent_count += 1
                except Exception as e:
                    messagebox.showerror("Email Error", f"Failed to send email to {email}: {e}", parent=plan_window)
            
            if sent_count > 0:
                messagebox.showinfo("Email Sent", f"{sent_count} purchase order email(s) have been sent directly.", parent=plan_window)

        # --- UI Layout ---
        top_button_frame = tk.Frame(plan_window)
        top_button_frame.pack(pady=(10, 5), fill='x')
        
        if suppliers_to_contact:
            tk.Button(top_button_frame, text="Email Supplier", command=send_emails_directly, bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold')).pack()

        tk.Label(plan_window, text="Material Shortage Detected!", font=('Segoe UI', 14, 'bold'), fg='red').pack(pady=10)
        tk.Label(plan_window, text="The following materials are required but are not in stock.").pack(pady=(0,10))

        tree_frame = ttk.Frame(plan_window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ("Material", "Required", "Available", "Shortfall", "Supplier")
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill='both', expand=True)

        for item in insufficient_items:
            supplier_id = item.get('supplier_id', 'N/A')
            supplier_info = self.db_manager.execute_custom_query("SELECT supplier_name FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier_name = supplier_info[0][0] if supplier_info else "Unknown"
            tree.insert("", "end", values=(item['name'], item['required'], item['available'], item['shortfall'], supplier_name))

        def generate_emails():
            # This function is now only for the "Review" button
            # The logic is the same as before, just defined later in the method
            for email, data in suppliers_to_contact.items():
                subject = f"Purchase Order Request - {datetime.now().strftime('%Y-%m-%d')}"
                body = (
                    f"Dear {data['name']},\n\n"
                    f"We would like to place a purchase order for the following materials which are required for a customer order.\n"
                    + "\n".join(data['items']) +
                    f"\n\nWe need these materials to be delivered within the order's deadline of {deadline}.\n\n"
                    f"\n\nPlease provide a quote and estimated delivery date at your earliest convenience.\n\n"
                    f"Thank you,\n{self.session.get('f_name', 'Procurement Team')}"
                )
                create_email(self.controller, to=email, subject=subject, body=body)
            messagebox.showinfo("Email Generation", "Purchase order email drafts have been generated for review.", parent=plan_window)

        def proceed_with_shortage():
            self._finalize_order_creation(status="Pending Materials")
            plan_window.destroy()

        button_frame = tk.Frame(plan_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Proceed (Pending Materials)", command=proceed_with_shortage, bg='#f39c12', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        if suppliers_to_contact: # Only show email buttons if there are suppliers to contact
            tk.Button(button_frame, text="Review & Email", command=generate_emails, bg='#3498db', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
            tk.Button(button_frame, text="Email Supplier", command=send_emails_directly, bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel Order", command=plan_window.destroy, bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5)

    def _finalize_order_creation(self, status="Pending"):
        try:
            selected_product = self.selected_product_var.get().strip()
            selected_client = self.selected_client_var.get().strip()
            quantity_int = int(self.order_quantity_var.get().strip())
            
            # Use the deadline from the calculated schedule if available
            deadline = self.schedule_info.get('deadline').strftime('%Y-%m-%d') if self.schedule_info and self.schedule_info.get('deadline') else self.deadline_var.get().strip()
            if not deadline:
                raise ValueError("Deadline is not set. Please calculate a schedule first.")
            client_name = selected_client.split('(')[0].strip()
            product_name = selected_product.split('(')[0].strip()
            order_name = f"{client_name}_{product_name}"

            materials_json = json.dumps(self.order_materials_data)
            product_id = selected_product.split('(')[-1].strip(')')
            client_id = selected_client.split('(')[-1].strip(')')
            order_id = self.db_manager.create_order(order_name, product_id, client_id, quantity_int, deadline, materials_json, status)

            # Save schedule and show success message after order creation
            if self.schedule_info:
                try:
                    self.db_manager.save_schedule(order_id, self.schedule_info)
                    schedule_summary = (
                        f"Order '{order_name}' created successfully with status '{status}'!\n"
                        f"Order ID: {order_id}\n\n"
                        f"--- Production Schedule Saved ---\n"
                        f"Feasibility: {self.schedule_info['feasibility']}"
                    )
                    messagebox.showinfo("Success & Schedule Saved", schedule_summary, parent=self.parent_window)
                except Exception as e:
                    messagebox.showwarning("Scheduling Error", f"Order created, but failed to save schedule: {str(e)}", parent=self.parent_window)
            else:
                messagebox.showinfo("Success", f"Order '{order_name}' created successfully with status '{status}'!\nOrder ID: {order_id}", parent=self.parent_window)

            self.selected_product_var.set("")
            self.selected_client_var.set("")
            self.order_quantity_var.set("")
            self.deadline_var.set("")

            self.product_materials_text.config(state='normal')
            self.product_materials_text.delete(1.0, tk.END)
            self.product_materials_text.config(state='disabled')
            self.required_materials_text.config(state='normal')
            self.required_materials_text.delete(1.0, tk.END)
            self.required_materials_text.config(bg='#e8f5e8')
            self.required_materials_text.config(state='disabled')

            # Optional logging to product logger if present in caller
            try:
                import logging
                product_logger = logging.getLogger('product_logger')
                if self.session and 'user_id' in self.session:
                    user_id = self.session.get('user_id')
                    user_name = self.session.get('f_name', self.session.get('username', 'Unknown'))
                    product_logger.info(f"User {user_name} (ID: {user_id}) created order '{order_name}' (ID: {order_id}) for product ID: {product_id}, client ID: {client_id}, quantity: {quantity_int}")
            except Exception:
                pass

        except (TypeError, json.JSONDecodeError) as e:
            messagebox.showerror("Format Error", f"Invalid materials data format: {str(e)}", parent=self.parent_window)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error creating order: {str(e)}", parent=self.parent_window)
        
        from global_func import export_total_amount_mats
        export_total_amount_mats('main.db', os.path.join(BASE_DIR, 'json_f', 'order_mats_ttl.json'))

import sqlite3

# Connect to the database
conn = sqlite3.connect('main.db')
c = conn.cursor()

# Enable foreign key constraints
c.execute("PRAGMA foreign_keys = ON;")

# Clients Table
c.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        client_name TEXT NOT NULL,
        client_email TEXT,
        client_address TEXT,
        client_contactnum TEXT
    )
""")


#User Activity Logs Table
c.execute("""
    CREATE TABLE IF NOT EXISTS user_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
                  ON DELETE CASCADE
                  ON UPDATE CASCADE
          )""")

# Suppliers Table



c.execute('DROP TABLE suppliers')


# Products Table (created before orders for FK reference)
c.execute('''
    CREATE TABLE IF NOT EXISTS products(
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        materials TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status_quo TEXT DEFAULT 'Pending'
    )
''')



# Raw Materials Table
# Add unit of measurements = Column (Amount, Unit of Measurement)
# Amount is amount per unit of measurement = Amount x Unit of Measurement
c.execute("""
    CREATE TABLE IF NOT EXISTS raw_mats (
        mat_id TEXT PRIMARY KEY,
        mat_name TEXT UNIQUE,
        unit_measurement TEXT,
        mat_volume INTEGER,
        low_count INTEGER,
        mat_order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        supplier_id TEXT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            ON DELETE CASCADE 
            ON UPDATE CASCADE
    )
""")



# Orders Table
c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        order_name TEXT NOT NULL,
        product_id TEXT NOT NULL,
        client_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        deadline TEXT NOT NULL,
        order_date TEXT NOT NULL,
        mats_need TEXT,
        status_quo TEXT DEFAULT 'Pending',
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (client_id) REFERENCES clients(client_id)
    )
""")

c.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_orders_client ON orders(client_id)")

# Commit changes and close the connection
conn.commit()
conn.close()
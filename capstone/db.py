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

# Users Table
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        f_name TEXT,
        l_name TEXT,
        m_name TEXT,
        useremail TEXT UNIQUE,
        phonenum TEXT,
        username TEXT,
        password TEXT,
        confirmpass TEXT,
        usertype TEXT,
        userimage BLOB
    )
""")



#Mails Table
c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT NOT NULL,
        receiver_id TEXT NOT NULL,
        subject TEXT,
        body TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY (sender_id) REFERENCES users(user_id),
        FOREIGN KEY (receiver_id) REFERENCES users(user_id)
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
c.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id TEXT PRIMARY KEY,
        supplier_add TEXT,
        supplier_num TEXT,
        supplier_mail TEXT,
        delivered_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Products Table (created before orders for FK reference)
c.execute('''
    CREATE TABLE IF NOT EXISTS products(
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        materials TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status_quo TEXT DEFAULT 'Pending',
    )
''')


# Raw Materials Table
c.execute("""
    CREATE TABLE IF NOT EXISTS raw_mats (
        mat_id TEXT PRIMARY KEY,
        mat_name TEXT UNIQUE,
        mat_volume INTEGER,
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
        order_name TEXT,
        product_id TEXT,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        order_dl TEXT,
        order_amount REAL,
        client_id TEXT NOT NULL,
        status_quo TEXT DEFAULT 'Pending',
        FOREIGN KEY (product_id) REFERENCES products(product_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY (client_id) REFERENCES clients(client_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
""")


# Commit changes and close the connection
conn.commit()
conn.close()

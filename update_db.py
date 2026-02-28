import sqlite3
from datetime import datetime
import os
import hashlib

DB_NAME = "main.db"

def get_connection():
    """Always return a connection with PRAGMA foreign_keys enabled."""
    conn = sqlite3.connect(f"file:{DB_NAME}?mode=rwc", uri=True)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def create_database():
    conn = get_connection()
    c = conn.cursor()

    # ---- Clients Table (long version) ----
    #DONE
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            client_name TEXT NOT NULL,
            client_email TEXT UNIQUE CHECK(client_email LIKE '%@%.%'),
            client_address TEXT,
            client_contactnum TEXT CHECK(LENGTH(client_contactnum) >= 10),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            notes TEXT
        )
    """)

    # ---- Users Table (long version) ----
    #DONE
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            f_name TEXT NOT NULL,
            l_name TEXT NOT NULL,
            m_name TEXT,
            useremail TEXT UNIQUE NOT NULL CHECK(useremail LIKE '%@%.%'),
            phonenum TEXT CHECK(LENGTH(phonenum) >= 10),
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            usertype TEXT NOT NULL CHECK(usertype IN ('admin', 'manager', 'staff', 'supplier')),
            userimage BLOB,
            last_login DATETIME,
            failed_login_attempts INTEGER DEFAULT 0,
            account_locked INTEGER DEFAULT 0 CHECK(account_locked IN (0, 1)),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            reset_token TEXT,
            reset_token_expiry DATETIME
        )
    """)

    # === User details ===
    user_id = 'nick'
    f_name = "Nick"
    l_name = "Diaz"
    m_name = "Robert"
    useremail = "victor.morana02@gmail.com"
    phonenum = "09123456788"
    username = "nick"

    # === Password setup ===
    password = "karen"  # default password
    salt = os.urandom(16).hex()
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    # === Account metadata ===
    usertype = "admin"
    userimage = None
    last_login = None
    failed_login_attempts = 0
    account_locked = 0
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_updated = date_created
    reset_token = None
    reset_token_expiry = None

    # === SQL Insert ===
    sql = """
    INSERT OR IGNORE INTO users (
        user_id, f_name, l_name, m_name, useremail, phonenum, username, 
        password_hash, salt, usertype, userimage, last_login, 
        failed_login_attempts, account_locked, date_created, last_updated,
        reset_token, reset_token_expiry
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        user_id, f_name, l_name, m_name, useremail, phonenum, username,
        password_hash, salt, usertype, userimage, last_login,
        failed_login_attempts, account_locked, date_created, last_updated,
        reset_token, reset_token_expiry
    )

    # Execute insert
    c.execute(sql, values)
    conn.commit()



    # ---- User Logs Table (long version) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_user_logs_user_id ON user_logs(user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_user_logs_timestamp ON user_logs(timestamp);")

    # ---- Suppliers Table (long version) ----
    #DONE
    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            supplier_add TEXT NOT NULL,
            supplier_num TEXT NOT NULL CHECK(LENGTH(supplier_num) >= 10),
            supplier_mail TEXT NOT NULL CHECK(supplier_mail LIKE '%@%.%'),
            contact_person TEXT,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            delivered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---- Products Table (short version + is_active) ----
    #DONE
    c.execute("""
        CREATE TABLE IF NOT EXISTS products(
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            materials TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            manufacturing_time_hours REAL,
            status_quo TEXT DEFAULT 'Pending',            
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1))
        )
    """)

    # --- Add manufacturing_time_hours column to products if it doesn't exist ---
    try:
        c.execute("ALTER TABLE products ADD COLUMN manufacturing_time_hours REAL;")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise # Re-raise error if it's not about a duplicate column
    # ---- Orders Table (short version + is_active) ----
    #DONE
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
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_orders_client ON orders(client_id)")

    # ---- Order History (long version, still useful) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS order_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            changed_by TEXT NOT NULL,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (changed_by) REFERENCES users(user_id)
        )
    """)

    # ---- Production Schedule Table ----
    # Drop the table to ensure the schema is updated with the UNIQUE constraint.
    c.execute("DROP TABLE IF EXISTS production_schedule;")
    c.execute("""
        CREATE TABLE IF NOT EXISTS production_schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            production_start_date DATETIME,
            production_end_date DATETIME,
            material_order_by_date DATETIME,
            feasibility_status TEXT CHECK(feasibility_status IN ('Feasible', 'At Risk', 'Infeasible')),
            notes TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            UNIQUE(order_id)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_production_schedule_order_id ON production_schedule(order_id);")

    # ---- Raw Materials Table (long version) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS raw_mats (
            mat_id TEXT PRIMARY KEY,
            mat_name TEXT UNIQUE NOT NULL,
            mat_description TEXT,
            mat_volume TEXT NOT NULL REFERENCES material_volumes(volume_name) ON UPDATE CASCADE,
            current_stock INTEGER NOT NULL CHECK(current_stock >= 0),
            unit_of_measure TEXT NOT NULL REFERENCES unit_of_measures(unit_name) ON UPDATE CASCADE,
            min_stock_level INTEGER DEFAULT 50 CHECK(min_stock_level >= 0),
            mat_order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            supplier_id TEXT NOT NULL,
            last_restocked DATETIME,
            shelf_life_days INTEGER,
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
        )
    """)

    # ---- Material Volumes Table ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS material_volumes (
            volume_name TEXT PRIMARY KEY
        )
    """)
    # Add some default values if the table is empty
    c.execute("INSERT OR IGNORE INTO material_volumes (volume_name) VALUES ('250ml'), ('500ml'), ('1L'), ('5L')")

    # ---- Unit of Measures Table ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS unit_of_measures (
            unit_name TEXT PRIMARY KEY
        )
    """)
    # Add some default values if the table is empty
    c.execute("INSERT OR IGNORE INTO unit_of_measures (unit_name) VALUES ('pcs'), ('kg'), ('g'), ('L'), ('ml')")


    # ---- Messages (long version) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0 CHECK(is_read IN (0, 1)),
            is_archived INTEGER DEFAULT 0 CHECK(is_archived IN (0, 1)),
            priority INTEGER DEFAULT 2 CHECK(priority BETWEEN 1 AND 3),
            FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS message_attachments (
            attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_data BLOB NOT NULL,
            FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
        )
    """)

    # ---- Notifications (long version) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0 CHECK(is_read IN (0, 1)),
            notification_type TEXT NOT NULL,
            related_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # ---- Inventory Transactions (long version) ----
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mat_id TEXT,
            product_id TEXT,
            quantity INTEGER NOT NULL,
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('purchase', 'sale', 'adjustment', 'transfer', 'waste')),
            reference_id TEXT,
            notes TEXT,
            performed_by TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mat_id) REFERENCES raw_mats(mat_id) ON DELETE SET NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL,
            FOREIGN KEY (performed_by) REFERENCES users(user_id)
        )
    """)

    # ---- Triggers for auto timestamps ----
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS update_client_timestamp
        AFTER UPDATE ON clients
        FOR EACH ROW
        BEGIN
            UPDATE clients SET last_updated = CURRENT_TIMESTAMP WHERE client_id = OLD.client_id;
        END;
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS update_user_timestamp
        AFTER UPDATE ON users
        FOR EACH ROW
        BEGIN
            UPDATE users SET last_updated = CURRENT_TIMESTAMP WHERE user_id = OLD.user_id;
        END;
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()

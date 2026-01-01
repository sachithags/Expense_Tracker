import sqlite3
import os

def fix_time_column():
    """Fix the time column if it's NOT NULL"""
    db_path = 'data/user_expenses.db'
    
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(expenses)")
        columns = cursor.fetchall()
        
        for col in columns:
            if col[1] == 'time' and col[3] == 1:  # 1 means NOT NULL
                print("🔧 Fixing time column constraint...")
                
                # Remove NOT NULL constraint by recreating table
                cursor.execute("ALTER TABLE expenses RENAME TO expenses_old")
                
                # Create new table without NOT NULL constraint for time
                cursor.execute('''
                    CREATE TABLE expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        time TEXT,
                        amount REAL NOT NULL,
                        category TEXT,
                        subcategory TEXT,
                        description TEXT,
                        payment_method TEXT,
                        merchant TEXT,
                        location TEXT,
                        is_weekend INTEGER,
                        is_month_end INTEGER,
                        day_of_week INTEGER,
                        month INTEGER,
                        predicted_category TEXT,
                        is_essential INTEGER,
                        confidence REAL,
                        user_id INTEGER NOT NULL DEFAULT 1
                    )
                ''')
                
                # Copy data
                cursor.execute('''
                    INSERT INTO expenses 
                    SELECT * FROM expenses_old
                ''')
                
                # Drop old table
                cursor.execute("DROP TABLE expenses_old")
                
                print("✅ Fixed time column constraint")
                break
        
        conn.commit()
    except Exception as e:
        print(f"⚠️ Could not fix time column: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_database():
    """Migrate database to add user_id column and create users table"""
    
    db_path = 'data/expenses.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print("🔧 Starting database migration...")
    
    fix_time_column()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if expenses table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        if not cursor.fetchone():
            print("❌ Expenses table doesn't exist!")
            return
        
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("📋 Adding user_id column to expenses table...")
            
            # Create a backup of the old table
            cursor.execute("ALTER TABLE expenses RENAME TO expenses_old")
            
            # Create new expenses table with user_id
            cursor.execute('''
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT,
                    description TEXT,
                    payment_method TEXT,
                    merchant TEXT,
                    location TEXT,
                    is_weekend INTEGER,
                    is_month_end INTEGER,
                    day_of_week INTEGER,
                    month INTEGER,
                    predicted_category TEXT,
                    is_essential INTEGER,
                    confidence REAL,
                    user_id INTEGER DEFAULT 1
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO expenses 
                (id, date, amount, category, description, payment_method, merchant, 
                 location, is_weekend, is_month_end, day_of_week, month, 
                 predicted_category, is_essential, confidence)
                SELECT id, date, amount, category, description, payment_method, merchant, 
                       location, is_weekend, is_month_end, day_of_week, month, 
                       predicted_category, is_essential, confidence
                FROM expenses_old
            ''')
            
            # Drop the old table
            cursor.execute("DROP TABLE expenses_old")
            
            print("✅ Added user_id column to expenses table!")
        else:
            print("✅ user_id column already exists")
        
        # Create users table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("📋 Creating users table...")
            
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    session_token TEXT
                )
            ''')
            
            # Create a default admin user (password: admin123)
            import hashlib
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name)
                VALUES (?, ?, ?)
            ''', ('admin', password_hash, 'Administrator'))
            
            print("✅ Created users table with default admin user")
        else:
            print("✅ Users table already exists")
        
        # Create categories table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        if not cursor.fetchone():
            print("📋 Creating categories table...")
            
            cursor.execute('''
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    budget REAL DEFAULT 0,
                    color TEXT DEFAULT '#6366f1',
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, name)
                )
            ''')
            
            print("✅ Created categories table")
        else:
            print("✅ Categories table already exists")
        
        conn.commit()
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
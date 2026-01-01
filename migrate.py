import sqlite3
import os
import hashlib
import secrets
from pathlib import Path

def get_column_names(cursor, table_name):
    """Get column names for a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [col[1] for col in cursor.fetchall()]

def migrate_database():
    """Migrate database to multi-user schema"""
    
    db_path = 'data/user_expenses.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    print("🔧 Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Found tables: {tables}")
        
        # 2. Create users table if not exists
        if 'users' not in tables:
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
            
            # Create default admin user
            password = 'admin123'
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            session_token = secrets.token_hex(32)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, session_token)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'Administrator', session_token))
            
            print("✅ Created users table with admin user")
            print("   👤 Username: admin, Password: admin123")
        else:
            print("✅ Users table already exists")
        
        # 3. Check expenses table columns
        if 'expenses' in tables:
            print("\n📋 Checking expenses table structure...")
            cursor.execute("PRAGMA table_info(expenses)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Existing columns: {columns}")
            
            # Add missing columns
            required_columns = [
                'user_id', 'merchant', 'location', 'is_weekend',
                'is_month_end', 'day_of_week', 'month', 
                'predicted_category', 'is_essential', 'confidence'
            ]
            
            for column in required_columns:
                if column not in columns:
                    try:
                        if column == 'user_id':
                            cursor.execute(f"ALTER TABLE expenses ADD COLUMN {column} INTEGER DEFAULT 1")
                        elif column in ['amount', 'confidence']:
                            cursor.execute(f"ALTER TABLE expenses ADD COLUMN {column} REAL DEFAULT 0")
                        elif column in ['is_weekend', 'is_month_end', 'day_of_week', 'month', 'is_essential']:
                            cursor.execute(f"ALTER TABLE expenses ADD COLUMN {column} INTEGER DEFAULT 0")
                        else:
                            cursor.execute(f"ALTER TABLE expenses ADD COLUMN {column} TEXT DEFAULT ''")
                        print(f"   ✅ Added column: {column}")
                    except Exception as e:
                        print(f"   ⚠️ Could not add {column}: {e}")
        
        # 4. Create categories table
        if 'categories' not in tables:
            print("\n📋 Creating categories table...")
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
            
            # Add default categories for admin user
            default_categories = [
                ('Food', '#10b981'),
                ('Transport', '#3b82f6'),
                ('Entertainment', '#8b5cf6'),
                ('Shopping', '#f59e0b'),
                ('Bills', '#ef4444'),
                ('Healthcare', '#ec4899'),
                ('Education', '#06b6d4'),
                ('Other', '#64748b')
            ]
            
            for category_name, color in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (user_id, name, color)
                    VALUES (?, ?, ?)
                ''', (1, category_name, color))
            
            print("✅ Created categories table with default categories")
        
        conn.commit()
        print("\n🎉 DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("✅ Multi-user system ready")
        print("✅ Existing data preserved")
        print("✅ Default admin user created")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
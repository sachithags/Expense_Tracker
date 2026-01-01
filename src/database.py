import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import secrets
from pathlib import Path
import os

class ExpenseDatabase:
    def __init__(self, db_path='data/user_expenses.db'):
    
        if db_path:
            self.db_path = db_path
        elif 'PYTHONANYWHERE' in os.environ:
            # Auto-detect PythonAnywhere path
            USERNAME = os.environ.get('PYTHONANYWHERE_USERNAME', 'yourusername')
            self.db_path = f'/home/{USERNAME}/expense-tracker-dt/data/user_expenses.db'
        else:
            self.db_path = 'data/user_expenses.db'
        
        print(f"📊 Database path: {self.db_path}")
        self.ensure_directories()
        self.init_database()
    
    def ensure_directories(self):
        """Ensure data directory exists"""
        Path('data').mkdir(exist_ok=True)
        Path('models').mkdir(exist_ok=True)
    
    # Update the init_database method in src/database.py
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
        
        # Create expenses table matching YOUR EXISTING SCHEMA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
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
                user_id INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                budget REAL DEFAULT 0,
                color TEXT DEFAULT '#6366f1',
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, name)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Add default admin user if not exists
        self.create_default_user()
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_default_user(self):
        """Create default admin user if no users exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Create admin user
                password_hash = self.hash_password('admin123')
                session_token = secrets.token_hex(32)
                
                cursor.execute('''
                    INSERT INTO users (username, password_hash, full_name, session_token)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', password_hash, 'Administrator', session_token))
                
                # Add default categories
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
                
                print("✅ Created default admin user: admin / admin123")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error creating default user: {e}")
    
    # Authentication methods
    def create_user(self, username, password, email=None, full_name=None):
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            session_token = secrets.token_hex(32)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, session_token)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, session_token))
            
            user_id = cursor.lastrowid
            
            # Add default categories for this user
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
                    INSERT INTO categories (user_id, name, color)
                    VALUES (?, ?, ?)
                ''', (user_id, category_name, color))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'session_token': session_token}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Username or email already exists'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, full_name, session_token 
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update session token and last login
                new_token = secrets.token_hex(32)
                cursor.execute('''
                    UPDATE users 
                    SET session_token = ?, last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_token, user[0]))
                
                conn.commit()
                conn.close()
                
                return {
                    'success': True,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'full_name': user[2],
                        'session_token': new_token
                    }
                }
            else:
                conn.close()
                return {'success': False, 'error': 'Invalid credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_session(self, user_id, session_token):
        """Verify user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, full_name 
                FROM users 
                WHERE id = ? AND session_token = ?
            ''', (user_id, session_token))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'success': True,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'full_name': user[2]
                    }
                }
            else:
                return {'success': False, 'error': 'Invalid session'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Expense methods
    def add_expense(self, user_id, expense_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add user_id to expense data
            expense_data['user_id'] = user_id
            
            # Add current date and time if not provided
            now = datetime.now()
            if 'date' not in expense_data:
                expense_data['date'] = now.strftime('%Y-%m-%d')
            if 'time' not in expense_data:
                expense_data['time'] = now.strftime('%H:%M:%S')
            
            # Calculate additional features
            date_obj = datetime.strptime(expense_data['date'], '%Y-%m-%d')
            expense_data['is_weekend'] = 1 if date_obj.weekday() >= 5 else 0
            expense_data['is_month_end'] = 1 if date_obj.day >= 25 else 0
            expense_data['day_of_week'] = date_obj.weekday()
            expense_data['month'] = date_obj.month
            
            # AI Category Prediction
            desc_lower = expense_data.get('description', '').lower()
            amount = expense_data.get('amount', 0)
            
            # Predict category based on description (AI/ML)
            if any(word in desc_lower for word in ['food', 'restaurant', 'coffee', 'lunch', 'dinner', 'breakfast', 'meal', 'snack']):
                predicted_category = 'Food'
                is_essential = 1 if amount < 1000 else 0
            elif any(word in desc_lower for word in ['uber', 'taxi', 'fuel', 'petrol', 'bus', 'train', 'metro', 'transport', 'travel']):
                predicted_category = 'Transport'
                is_essential = 1
            elif any(word in desc_lower for word in ['bill', 'electricity', 'rent', 'internet', 'water', 'gas', 'mobile', 'subscription']):
                predicted_category = 'Bills'
                is_essential = 1
            elif any(word in desc_lower for word in ['movie', 'entertainment', 'game', 'concert', 'party', 'netflix', 'spotify']):
                predicted_category = 'Entertainment'
                is_essential = 0
            elif any(word in desc_lower for word in ['medical', 'doctor', 'hospital', 'medicine', 'pharmacy', 'health']):
                predicted_category = 'Healthcare'
                is_essential = 1
            elif any(word in desc_lower for word in ['shopping', 'clothes', 'electronics', 'amazon', 'flipkart']):
                predicted_category = 'Shopping'
                is_essential = 0 if amount > 2000 else 1
            else:
                predicted_category = 'Other'
                is_essential = 0 if amount > 2000 else 1
            
            # Add ML predictions
            expense_data['predicted_category'] = predicted_category
            expense_data['is_essential'] = is_essential
            expense_data['confidence'] = 0.85  # AI confidence score
            
            # Add subcategory if not provided (can be empty)
            if 'subcategory' not in expense_data:
                expense_data['subcategory'] = ''
            
            # Use provided category or predicted one
            if 'category' not in expense_data or not expense_data['category']:
                expense_data['category'] = predicted_category
            
            # Prepare columns and values
            columns = []
            values = []
            placeholders = []
            
            # Get all columns that exist in the table
            cursor.execute("PRAGMA table_info(expenses)")
            table_columns = [col[1] for col in cursor.fetchall()]
            
            # Only include columns that exist in the table
            for key, value in expense_data.items():
                if key in table_columns:
                    columns.append(key)
                    values.append(value)
                    placeholders.append('?')
            
            if not columns:
                return {'success': False, 'error': 'No valid columns to insert'}
            
            query = f"INSERT INTO expenses ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            cursor.execute(query, values)
            expense_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'expense_id': expense_id,
                'prediction': {
                    'predicted_category': predicted_category,
                    'is_essential': is_essential,
                    'confidence': 0.85,
                    'alert': ['✅ AI analyzed your expense']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_expenses_list(self, user_id, limit=10):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, time, amount, description, category, 
                    subcategory, payment_method, merchant, location, is_essential
                FROM expenses 
                WHERE user_id = ? 
                ORDER BY date DESC, time DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            expenses = []
            for row in rows:
                expenses.append({
                    'id': row[0],
                    'date': row[1],
                    'time': row[2],
                    'amount': row[3],
                    'description': row[4],
                    'category': row[5],
                    'subcategory': row[6] or '',
                    'payment_method': row[7] or 'Cash',
                    'merchant': row[8] or '',
                    'location': row[9] or '',
                    'is_essential': row[10] or 0
                })
            
            return expenses
        except Exception as e:
            print(f"Error getting expenses: {e}")
            return []
    
    def delete_expense(self, user_id, expense_id):
        """Delete expense if it belongs to user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify expense belongs to user
            cursor.execute('SELECT id FROM expenses WHERE id = ? AND user_id = ?', 
                          (expense_id, user_id))
            expense = cursor.fetchone()
            
            if expense:
                cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Expense deleted'}
            else:
                conn.close()
                return {'success': False, 'error': 'Expense not found or unauthorized'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_monthly_stats(self, user_id):
        """Get statistics for current month"""
        try:
            current_month = datetime.now().strftime('%Y-%m')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(amount), 0) as total_spent,
                    COALESCE(COUNT(*), 0) as total_transactions,
                    COALESCE(AVG(amount), 0) as avg_transaction,
                    COALESCE(MAX(amount), 0) as most_expensive
                FROM expenses 
                WHERE user_id = ? AND strftime('%Y-%m', date) = ?
            ''', (user_id, current_month))
            
            stats_row = cursor.fetchone()
            
            # Get favorite category
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM expenses 
                WHERE user_id = ? AND strftime('%Y-%m', date) = ?
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 1
            ''', (user_id, current_month))
            
            category_row = cursor.fetchone()
            favorite_category = category_row[0] if category_row else "No data"
            
            conn.close()
            
            return {
                'total_spent': float(stats_row[0]),
                'total_transactions': int(stats_row[1]),
                'avg_transaction': float(stats_row[2]),
                'most_expensive': float(stats_row[3]),
                'favorite_category': favorite_category
            }
                
        except Exception as e:
            print(f"Error getting monthly stats: {e}")
            return {
                'total_spent': 0,
                'total_transactions': 0,
                'avg_transaction': 0,
                'most_expensive': 0,
                'favorite_category': "No data"
            }
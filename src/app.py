import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import ExpenseDatabase


if 'PYTHONANYWHERE' in os.environ:
    USERNAME = os.environ.get('PYTHONANYWHERE_USERNAME', 'yourusername')
    # Use absolute path for database
    DB_PATH = f'/home/{USERNAME}/expense-tracker-dt/data/user_expenses.db'
    print(f"🚀 Running on PythonAnywhere as {USERNAME}")
    print(f"📁 Database path: {DB_PATH}")
else:
    DB_PATH = 'data/user_expenses.db'
    print("🚀 Running locally")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = os.urandom(24)

db = ExpenseDatabase(DB_PATH)

def init_app():
    """Initialize application"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("✅ Application initialized successfully")

# Middleware to check authentication
@app.before_request
def check_auth():
    public_routes = ['landing_page', 'login_page', 'register_page', 'login', 'register', 'static']
    
    if request.endpoint in public_routes:
        return
    
    user_id = session.get('user_id')
    session_token = session.get('session_token')
    
    if not user_id or not session_token:
        return redirect(url_for('login_page'))
    
    # Verify session
    result = db.verify_session(user_id, session_token)
    if not result['success']:
        session.clear()
        return redirect(url_for('login_page'))

# Public Routes
@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

# Auth APIs
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    result = db.authenticate_user(username, password)
    
    if result['success']:
        user = result['user']
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['session_token'] = user['session_token']
        session.permanent = True
        
        return jsonify({'success': True, 'redirect': '/dashboard'})
    else:
        return jsonify({'success': False, 'error': result['error']})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('full_name')
    
    result = db.create_user(username, password, email, full_name)
    
    if result['success']:
        login_result = db.authenticate_user(username, password)
        if login_result['success']:
            user = login_result['user']
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['session_token'] = user['session_token']
            session.permanent = True
            
            return jsonify({'success': True, 'redirect': '/dashboard'})
    
    return jsonify({'success': False, 'error': result.get('error', 'Registration failed')})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing_page'))

@app.route('/api/check-session')
def check_session():
    """Check if user has valid session"""
    user_id = session.get('user_id')
    session_token = session.get('session_token')
    
    if user_id and session_token:
        result = db.verify_session(user_id, session_token)
        if result['success']:
            return jsonify({'logged_in': True, 'username': session.get('username')})
    
    return jsonify({'logged_in': False})

# Protected Routes
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    
    # Get recent expenses
    recent_expenses = db.get_expenses_list(user_id, limit=10)
    
    # Calculate totals
    total_spent = float(sum([e['amount'] for e in recent_expenses])) if recent_expenses else 0.0
    avg_daily = float(total_spent / 30) if total_spent > 0 else 0.0
    
    # Generate AI insights
    insights = generate_insights(recent_expenses, total_spent)
    
    return render_template('index.html',
                         recent_expenses=recent_expenses,
                         total_spent=total_spent,
                         avg_daily=avg_daily,
                         insights=insights,
                         username=session.get('username'),
                         full_name=session.get('full_name'))

def generate_insights(expenses, total_spent):
    """Generate AI insights based on user expenses"""
    if not expenses:
        return [
            "🤖 Welcome! Add your first expense to get AI-powered insights!",
            "🎯 Track regularly to see spending patterns",
            "📈 Our ML model will analyze your habits"
        ]
    
    insights = []
    
    # Insight based on expense count
    if len(expenses) < 3:
        insights.append("📊 Add more expenses for better AI analysis")
    elif len(expenses) < 10:
        insights.append(f"📈 You've tracked {len(expenses)} expenses - keep going!")
    else:
        insights.append(f"✅ Excellent! {len(expenses)} expenses analyzed")
    
    # Insight based on total spent
    if total_spent > 20000:
        insights.append("💰 High spending detected. Consider reviewing non-essential expenses")
    elif total_spent > 5000:
        insights.append("📊 Your spending pattern is being analyzed by AI")
    elif total_spent > 0:
        insights.append("✅ Your spending is within typical range")
    
    # Insight based on categories
    if expenses:
        categories = [e['category'] for e in expenses if e.get('category')]
        if categories:
            most_common = max(set(categories), key=categories.count)
            insights.append(f"🎯 Most frequent category: {most_common}")
    
    return insights[:3]

# Expense APIs
@app.route('/add')
def add_expense_page():
    return render_template('add_expense.html', username=session.get('username'))

@app.route('/api/add', methods=['POST'])
def add_expense_api():
    user_id = session.get('user_id')
    data = request.json
    
    expense_data = {
        'amount': float(data['amount']),
        'description': data['description'],
        'payment_method': data.get('payment_method', 'Cash')
    }
    
    # Optional fields
    if 'category' in data:
        expense_data['category'] = data['category']
    if 'merchant' in data:
        expense_data['merchant'] = data['merchant']
    if 'location' in data:
        expense_data['location'] = data['location']
    
    result = db.add_expense(user_id, expense_data)
    return jsonify(result)

@app.route('/api/expenses')
def get_expenses_api():
    user_id = session.get('user_id')
    expenses = db.get_expenses_list(user_id, limit=50)
    return jsonify(expenses)

@app.route('/api/expense/<int:expense_id>', methods=['DELETE'])
def delete_expense_api(expense_id):
    user_id = session.get('user_id')
    result = db.delete_expense(user_id, expense_id)
    return jsonify(result)

# Analytics page
@app.route('/analytics')
def analytics():
    user_id = session.get('user_id')
    
    try:
        # Get monthly stats
        stats = db.get_monthly_stats(user_id)
        
        if stats['total_transactions'] > 0:
            month_name = datetime.now().strftime('%B %Y')
            
            return render_template('analytics.html', 
                                 stats=stats, 
                                 month=month_name, 
                                 no_data=False)
        else:
            return render_template('analytics.html', no_data=True)
            
    except Exception as e:
        print(f"Analytics error: {e}")
        return render_template('analytics.html', no_data=True)

@app.route('/')
def root():
    """Root route - redirect based on authentication"""
    # Check if user is logged in
    user_id = session.get('user_id')
    session_token = session.get('session_token')
    
    if user_id and session_token:
        result = db.verify_session(user_id, session_token)
        if result['success']:
            return redirect(url_for('dashboard'))
    
    # Not logged in, show landing page
    return render_template('landing.html')
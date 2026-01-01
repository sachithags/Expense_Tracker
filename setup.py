import os
import sys
import subprocess
from datetime import datetime, timedelta

def setup_project():
    print("🚀 Setting up Smart Expense Tracker...")
    
    directories = [
        'data',
        'models',
        'templates',
        'static/css',
        'static/js',
        'notebooks',
        'src'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    python_version = sys.version.split()[0]
    print(f"🐍 Python version: {python_version}")
    
    # Check key packages
    print("\n🔍 Checking installed packages...")
    packages_to_check = [
        ('flask', 'Flask'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('joblib', 'joblib'),
        ('plotly', 'plotly')
    ]
    
    for import_name, display_name in packages_to_check:
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {display_name}: {version}")
        except ImportError:
            print(f"❌ {display_name}: Not installed")
    
    # Generate sample data
    print("\n📊 Generating sample data...")
    try:
        create_sample_data()
    except Exception as e:
        print(f"⚠️ Could not generate sample data: {e}")
        print("Creating empty CSV file instead...")
        with open('data/expenses.csv', 'w') as f:
            f.write('date,amount,category,description,is_essential\n')
    
    with open('src/__init__.py', 'w') as f:
        f.write('# Expense Tracker Package\n')
    
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    print("\n📋 Next Steps:")
    print("1. Create your Flask app files:")
    print("   - src/app.py")
    print("   - src/database.py")
    print("   - src/predict.py")
    print("2. Create HTML templates:")
    print("   - templates/index.html")
    print("   - templates/add_expense.html")
    print("3. Run the app:")
    print("   python src/app.py")
    print("\n🔗 Quick Links:")
    print("  • App: http://localhost:5000")
    print("  • Add Expense: http://localhost:5000/add")
    
    return True

def create_sample_data():
    """Create sample expense data"""
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        import random
        
        categories = ['Food', 'Transport', 'Bills', 'Entertainment', 'Shopping', 'Healthcare']
        subcategories = {
            'Food': ['Groceries', 'Restaurant', 'Coffee', 'Takeout'],
            'Transport': ['Fuel', 'Public Transport', 'Taxi', 'Maintenance'],
            'Bills': ['Electricity', 'Internet', 'Phone', 'Rent'],
            'Entertainment': ['Movies', 'Concerts', 'Games', 'Subscriptions'],
            'Shopping': ['Clothes', 'Electronics', 'Home', 'Other'],
            'Healthcare': ['Medicine', 'Doctor', 'Insurance', 'Fitness']
        }
        
        data = []
        for i in range(100):
            date = datetime.now() - timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            subcategory = random.choice(subcategories[category])
            
            # Generate amount based on category
            amount_ranges = {
                'Food': (50, 3000),
                'Transport': (100, 5000),
                'Bills': (500, 20000),
                'Entertainment': (200, 10000),
                'Shopping': (500, 50000),
                'Healthcare': (200, 30000)
            }
            
            min_amt, max_amt = amount_ranges[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            description = f"{subcategory} expense"
            
            # Determine if essential
            if category in ['Bills', 'Healthcare']:
                is_essential = 1
            elif category == 'Shopping' and amount > 10000:
                is_essential = 0
            elif category == 'Entertainment' and amount > 5000:
                is_essential = 0
            else:
                is_essential = random.choice([0, 1])
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': category,
                'description': description,
                'is_essential': is_essential,
                'is_weekend': 1 if date.weekday() >= 5 else 0,
                'payment_method': random.choice(['Credit Card', 'Debit Card', 'Cash', 'UPI']),
                'merchant': random.choice(['Store', 'Online', 'Restaurant', 'Service'])
            })
        
        df = pd.DataFrame(data)
        df.to_csv('data/expenses.csv', index=False)
        print(f"✅ Generated {len(df)} sample expense records")
        print(f"✅ Saved to: data/expenses.csv")
        
    except ImportError as e:
        print(f"⚠️ Need pandas to generate sample data: {e}")
        print("Creating simple CSV manually...")
        
        import csv
        with open('data/expenses.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'amount', 'category', 'description', 'is_essential'])
            for i in range(20):
                writer.writerow([
                    f'2024-01-{i+1:02d}',
                    round(50 + i * 100, 2),
                    ['Food', 'Transport', 'Bills'][i % 3],
                    f'Sample expense {i+1}',
                    i % 2
                ])
        print("✅ Created simple CSV with 20 records")

if __name__ == "__main__":
    setup_project()
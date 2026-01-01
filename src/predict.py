import pandas as pd
from datetime import datetime

def analyze_expense_in_realtime(expense_data):
    """Real-time expense analysis (simple version)"""
    now = datetime.now()
    
    amount = float(expense_data.get('amount', 0))
    description = expense_data.get('description', '').lower()
    
    if any(word in description for word in ['food', 'restaurant', 'coffee', 'tea', 'cafe', 'groceries', 'dinner', 'lunch']):
        predicted_category = 'Food'
    elif any(word in description for word in ['uber', 'taxi', 'fuel', 'petrol', 'bus', 'train', 'metro', 'transport']):
        predicted_category = 'Transport'
    elif any(word in description for word in ['bill', 'electricity', 'water', 'internet', 'phone', 'rent']):
        predicted_category = 'Bills'
    elif any(word in description for word in ['movie', 'netflix', 'prime', 'concert', 'game', 'entertainment']):
        predicted_category = 'Entertainment'
    elif any(word in description for word in ['shopping', 'amazon', 'flipkart', 'clothes', 'electronics', 'purchase']):
        predicted_category = 'Shopping'
    else:
        predicted_category = 'Other'

    if predicted_category in ['Bills']:
        is_essential = 1
    elif amount > 5000 and predicted_category in ['Shopping', 'Entertainment']:
        is_essential = 0
    elif amount > 3000:
        is_essential = 0
    else:
        is_essential = 1

    alerts = []
    if amount > 10000:
        alerts.append(f"🚨 Large expense detected: ₹{amount:,.2f}")
    if not is_essential and amount > 5000:
        alerts.append(f"💸 High non-essential spending: ₹{amount:,.2f}")
    if not alerts:
        alerts.append("✅ Expense looks normal")
    
    # Generate insights
    insights = []
    if amount > 5000:
        insights.append({
            'type': 'high_spending',
            'message': f"This {predicted_category} expense is above average",
            'suggestion': 'Consider if this is necessary'
        })
    
    return {
        'predicted_category': predicted_category,
        'is_essential': int(is_essential),
        'confidence': 0.85,  # Fixed confidence for now
        'alert': alerts,
        'insights': insights,
        'probabilities': {
            'non_essential': 0.15 if is_essential else 0.85,
            'essential': 0.85 if is_essential else 0.15
        }
    }
# 📊 Smart Expense Tracker with AI/ML

A web app that tracks expenses and provides AI-powered insights using machine learning.

## 🚀 Live Demo
[https://sachitha.pythonanywhere.com](https://sachitha.pythonanywhere.com)

## ✨ Features
- **Expense Tracking** with categories
- **Multi-user Authentication**
- **AI/ML Classification** (Essential vs Non-essential)
- **Interactive Dashboard** with charts
- **Monthly Analytics** & spending insights
- **PythonAnywhere** deployment ready

## 🛠️ Tech Stack
- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **ML**: scikit-learn, Decision Trees, Pandas
- **Visualization**: Plotly.js

## 🏃‍♂️ Quick Start

### 1. Local Setup
```bash
# Clone repository
git clone https://github.com/sachithags/Expense_Tracker.git
cd Expense_Tracker

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python migrate.py

# Run app
python run.py
```
Visit: http://localhost:5000

### 2. Demo Login
- **Username**: `admin`
- **Password**: `admin123`

## 🤖 Machine Learning
The app uses a Decision Tree classifier trained on expense data to:
- Auto-categorize expenses as Essential/Non-essential
- Provide spending insights
- Detect unusual patterns

**Model Training**: See `notebooks/expense_classifier_colab.ipynb`

## 📁 Project Structure
```
expense-tracker-DT/
├── src/              # Flask application
├── templates/        # HTML templates
├── static/          # CSS, JS, images
├── notebooks/       # ML training notebooks
├── models/          # Trained ML models
├── data/            # Database & datasets
├── requirements.txt # Dependencies
└── README.md        # This file
```

## 🌐 Deployment on PythonAnywhere
1. Clone repo on PythonAnywhere
2. Create virtualenv: `mkvirtualenv expense-tracker`
3. Install: `pip install Flask pandas scikit-learn`
4. Configure WSGI file
5. Reload web app

## 🔧 API Endpoints
- `POST /api/login` - User authentication
- `POST /api/add` - Add expense
- `GET /api/expenses` - Get expenses
- `GET /analytics` - Spending analytics

## 📝 License
MIT License - see [LICENSE](LICENSE) file

## 📞 Support
For issues: [GitHub Issues](https://github.com/sachithags/Expense_Tracker/issues)

---

**Demo**: [sachitha.pythonanywhere.com](https://sachitha.pythonanywhere.com) | **GitHub**: [sachithags/Expense_Tracker](https://github.com/sachithags/Expense_Tracker)
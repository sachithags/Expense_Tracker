import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    """Main entry point for the expense tracker"""
    print("\n" + "="*60)
    print("🚀 SMART EXPENSE TRACKER - MULTI-USER EDITION")
    print("="*60)
    
    db_path = 'data/user_expenses.db'
    if os.path.exists(db_path):
        print("📊 Found existing database...")
        try:
            from migrate import migrate_database
            if migrate_database():
                print("✅ Database migrated successfully!")
            else:
                print("✅ Using existing database")
        except Exception as e:
            print(f"⚠️ Migration check skipped: {e}")
    
    from src.app import app, init_app

    init_app()

    import socket
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"📱 Local Network Access: http://{ip_address}:5000")
    except:
        pass
    
    print(f"🌐 Local Access: http://localhost:5000")
    print(f"🔐 Login: http://localhost:5000/login")
    print(f"📝 Register: http://localhost:5000/register")
    print("="*60)
    print("👥 Share with friends on the same WiFi network!")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
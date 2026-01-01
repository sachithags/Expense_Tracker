import os
import subprocess
import shutil
import time
import stat

def remove_readonly(func, path, _):
    """Remove readonly files on Windows"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def setup_git_repo():
    """Setup git repository properly"""
    
    print("🔧 Setting up Git repository...")
    
    if os.path.exists('.git'):
        print("Removing existing .git folder...")
        try:
            shutil.rmtree('.git')
        except PermissionError:
            print("Git files locked. Trying with force removal...")
            shutil.rmtree('.git', onerror=remove_readonly)
        except Exception as e:
            print(f"Could not remove .git: {e}")
            print("Trying alternative method...")
            subprocess.run(['git', 'clean', '-fd'], capture_output=True)
            subprocess.run(['git', 'reset', '--hard'], capture_output=True)

    time.sleep(1)

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
.venv/
ENV/
env.bak/
venv.bak/

# Environment variables
.env
.venv

# Database (don't commit database files)
*.db
*.sqlite
*.sqlite3
data/*.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Project specific
data/local.db
models/__pycache__/
notebooks/.ipynb_checkpoints/

# PythonAnywhere specific
pythonanywhere_wsgi.py
start_pa.py

# Notebook checkpoints
.ipynb_checkpoints/
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    subprocess.run(['git', 'init'], check=True)
    print("✅ Initialized git repository")

    essential_files = [
        'src/',
        'templates/',
        'models/',
        'notebooks/',
        'data/',  
        '.gitignore',
        'requirements.txt',
        'README.md',
        'run.py',
        'migrate.py'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            try:
                subprocess.run(['git', 'add', file], check=True)
                print(f"✅ Added: {file}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Failed to add {file}: {e}")
    
    try:
        subprocess.run(['git', 'commit', '-m', 'Initial commit: Smart Expense Tracker with AI/ML'], check=True)
        print("✅ Committed initial files")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not commit: {e}")
        print("Checking git status...")
        subprocess.run(['git', 'status'])

    print("\n📋 Files committed:")
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    files = result.stdout.strip().split('\n')
    for file in files:
        if file: 
            print(f"  📄 {file}")
    
    print("\n🎉 Git repository setup complete!")
    print("\n📋 Next steps:")
    print("1. Create GitHub repository at https://github.com/new")
    print("2. Connect your local repo:")
    print("   git remote add origin https://github.com/sachithags/Expense_Tracker.git")
    print("   git branch -M main")
    print("   git push -u origin main")

if __name__ == "__main__":
    setup_git_repo()
#!/usr/bin/env python3
"""
Setup script for Health Chatbot - Choose between ML and non-ML deployment
"""

import os
import sys
import subprocess
import shutil

def print_banner():
    """Print setup banner"""
    print("🏥 Health Chatbot Setup")
    print("=" * 40)
    print("Choose your deployment option:")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies(requirements_file):
    """Install dependencies from requirements file"""
    try:
        print(f"📦 Installing dependencies from {requirements_file}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_imports():
    """Test if ML dependencies can be imported"""
    try:
        import torch
        import transformers
        import scipy
        print("✅ ML dependencies available")
        return True
    except ImportError:
        print("❌ ML dependencies not available")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    print("\n🔧 Setup Options:")
    print("1. Production Deployment (Vercel/Render) - Rule-based only")
    print("2. Local Development with ML - Full capabilities")
    print("3. Test current setup")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🚀 Setting up for Production Deployment...")
            print("   This will use minimal dependencies for Vercel/Render")
            
            if install_dependencies("requirements.txt"):
                print("\n✅ Production setup complete!")
                print("   You can now deploy to Vercel or Render")
                print("   The system will use rule-based analysis")
            break
            
        elif choice == "2":
            print("\n🤖 Setting up for Local Development with ML...")
            print("   This will install ML dependencies (may take a while)")
            
            if install_dependencies("requirements-ml.txt"):
                print("\n✅ ML setup complete!")
                print("   Testing ML imports...")
                
                if test_imports():
                    print("   ✅ ML models will be available")
                else:
                    print("   ⚠️  ML models may not work - check your environment")
                    
                print("\n   You can now run: python app.py")
            break
            
        elif choice == "3":
            print("\n🧪 Testing current setup...")
            
            # Check what's currently installed
            print("   Checking current dependencies...")
            
            try:
                import flask
                import flask_cors
                print("   ✅ Flask dependencies available")
            except ImportError:
                print("   ❌ Flask dependencies missing")
            
            if test_imports():
                print("   ✅ ML dependencies available")
                print("   💡 You can use ML-enhanced analysis")
            else:
                print("   ❌ ML dependencies not available")
                print("   💡 You can use rule-based analysis")
            
            print("\n   Run 'python test_hybrid.py' to test the API")
            break
            
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 
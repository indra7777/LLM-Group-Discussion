#!/usr/bin/env python3
"""Setup script for the Multi-Agent Discussion LLM System."""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version check passed: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from example if it doesn't exist."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file from example")
            print("  Please edit .env and add your API keys")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("# Multi-Agent Discussion System Configuration\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("DEBUG=True\n")
            print("✓ Created basic .env file")
            print("  Please edit .env and add your OpenAI API key")
    else:
        print("✓ .env file already exists")

def run_tests():
    """Run basic tests to verify installation."""
    print("Running basic tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_basic.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("✗ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False

def main():
    """Main setup function."""
    print("Multi-Agent Discussion LLM System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed during dependency installation.")
        print("You can try installing manually with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Run tests
    if not run_tests():
        print("\nSetup completed with warnings.")
        print("Some tests failed, but the basic system should work.")
    else:
        print("\n✓ Setup completed successfully!")
    
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the system with: python3 src/main.py")
    print("3. Or try demo mode: python3 src/main.py --demo")

if __name__ == "__main__":
    main()
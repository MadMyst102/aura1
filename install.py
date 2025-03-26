import subprocess
import sys
import os

def install_dependencies():
    """Install required packages and handle platform-specific dependencies"""
    print("Installing dependencies...")
    
    # List of required packages
    requirements = [
        'pyautogui==0.9.54',
        'pynput==1.7.6',
        'PyQt5==5.15.9',
        'loguru==0.7.0',
        'keyboard==0.13.5',  # Added for better hotkey support
        'pywin32; platform_system=="Windows"',  # Windows-specific dependency
        'python-xlib; platform_system=="Linux"'  # Linux-specific dependency
    ]
    
    try:
        # Ensure pip is up to date
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Install each requirement
        for req in requirements:
            print(f"Installing {req}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
            
        print("\nAll dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nError installing dependencies: {e}")
        return False

if __name__ == "__main__":
    if install_dependencies():
        print("\nSetup complete! You can now run the application using:")
        print("  GUI mode: python gui.py")
        print("  Console mode: python main.py")
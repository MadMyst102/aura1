import os
import sys
import shutil
import subprocess

def build_executable():
    """Build a standalone executable using PyInstaller"""
    print("Starting build process...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Create build directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Define all Python modules to be included
    all_python_modules = [
        'main',
        'multiclient',
        'license_manager',
        'license_tab',
        'profile_widget',
        'profiles',
        'theme',
        'icons',
        'utils'
    ]
    
    # Define PyInstaller command
    pyinstaller_args = [
        'pyinstaller',
        'aura_full.spec',  # Use the comprehensive spec file
    ]
    
    # Run PyInstaller
    print("Running PyInstaller...")
    subprocess.check_call(pyinstaller_args)
    
    # Create deployment directory
    deploy_dir = 'deploy'
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy executable and config file to deployment directory
    shutil.copy(os.path.join('dist', 'Aura_Full.exe'), deploy_dir)
    # Rename to Aura.exe for consistency
    os.rename(os.path.join(deploy_dir, 'Aura_Full.exe'), os.path.join(deploy_dir, 'Aura.exe'))
    
    # Create a default config if it doesn't exist
    if os.path.exists('config.json'):
        shutil.copy('config.json', deploy_dir)
    else:
        from utils import get_config_manager
        config_manager = get_config_manager()
        config = config_manager._get_default_config()
        config_manager.config_path = os.path.join(deploy_dir, 'config.json')
        config_manager.save_config(config)
    
    # Copy license file if it exists
    if os.path.exists('license.acl'):
        shutil.copy('license.acl', deploy_dir)
        print(f"License file copied to {deploy_dir}")
    
    # Copy analytics file if it exists or create an empty one
    if os.path.exists('analytics.json'):
        shutil.copy('analytics.json', deploy_dir)
    else:
        with open(os.path.join(deploy_dir, 'analytics.json'), 'w') as f:
            f.write('[]')
        print(f"Empty analytics file created in {deploy_dir}")
    
    print("\nBuild completed successfully!")
    print(f"Executable and config file are available in the '{deploy_dir}' directory.")
    print("You can now distribute these files to your users.")

if __name__ == "__main__":
    build_executable()
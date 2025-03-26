# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define all Python modules to be included
all_modules = [
    'gui.py',
    'main.py',
    'multiclient.py',
    'license_manager.py',
    'license_tab.py',
    'profile_widget.py',
    'profiles.py',
    'theme.py',
    'icons.py',
    'utils.py'
]

# Create a list of Analysis objects for each module
a = Analysis(
    all_modules,
    pathex=[],
    binaries=[],
    datas=[
        ('logo.svg', '.'),
        ('logo_enhanced.svg', '.'),
        ('check.svg', '.'),
        ('profiles', 'profiles')
    ],
    hiddenimports=[
        'PyQt5.QtChart',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'win32gui',
        'win32con',
        'win32process',
        'win32api',
        'wmi',
        'pynput.keyboard',
        'pyautogui',
        'keyboard',
        'psutil',
        'cryptography',
        '_cffi_backend',  # Explicitly include _cffi_backend which is required by cryptography
        'main',
        'multiclient',
        'license_manager',
        'license_tab',
        'profile_widget',
        'profiles',
        'theme',
        'icons',
        'utils'
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Aura_Full',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # No icon specified to avoid conversion issues
)
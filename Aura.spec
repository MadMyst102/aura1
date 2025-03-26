# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.svg', '.'), ('logo_enhanced.svg', '.'), ('check.svg', '.'), ('profiles', 'profiles')],
    hiddenimports=['PyQt5.QtChart', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui', 'win32gui', 'win32con', 'win32process', 'win32api', 'wmi', 'pynput.keyboard', 'pyautogui', 'keyboard', 'psutil', 'cryptography', '_cffi_backend'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Aura',
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
    icon=['check.png'],
)

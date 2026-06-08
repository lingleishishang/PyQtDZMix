# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['PyDesktop.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ("./Ui_PyDesktop.py", "."),
        ("./Ui_PySubData.py", "."),
        ("./Ui_PyOriginalData.py", "."),
        ("./Ui_PyBigSource.py", "."),
        ("./Ui_PyOneSource.py", "."),
    ],
    hiddenimports=[
        'matplotlib.backends.backend_pdf',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_svg',
        'matplotlib.backends.backend_ps',
        'PyQt5.sip',
        'scipy.special.cython_special',
        'scipy._lib.messagestream',
        'numpy._globals',
        'numpy',
        'scipy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='PyQtDZMixture',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='./logo.ico',
    onefile=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
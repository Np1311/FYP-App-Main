# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.png', '.'), ('background.png', '.'), ('fyp.db', '.'), ('file_upload_icon.png', '.'), ('Model2_VGG16.h5', '.'), ('logo.ico', '.')],
    hiddenimports=['pymysql', 'tensorflow', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IntelligentHealthInc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IntelligentHealthInc',
)
app = BUNDLE(
    coll,
    name='IntelligentHealthInc.app',
    icon='logo.ico',
    bundle_identifier=None,
)

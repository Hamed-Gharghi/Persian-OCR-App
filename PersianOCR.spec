# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('build_data\\Tesseract', 'Tesseract'), ('build_data\\assets', 'assets')],
    hiddenimports=['fitz', 'cv2', 'numpy', 'ocr_utils', 'export_utils', 'settings', 'tessdata_manager', 'docx', 'windnd', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='PersianOCR',
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
    version='D:\\Project\\Persian_OCR\\build_temp\\2a0a29a8-b39f-4b74-87c7-eafde6c8fc9b',
    icon=['assets\\icon.ico'],
)

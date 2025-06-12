# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\ccerq\\OneDrive\\Documentos\\Python Scripts\\ML_CostAnalysis4_Branch3\\WOApprovalbyAI\\.venv\\Lib\\site-packages\\embedchain-0.1.110.dist-info', 'embedchain-0.1.110.dist-info'), ('C:\\Users\\ccerq\\OneDrive\\Documentos\\Python Scripts\\ML_CostAnalysis4_Branch3\\WOApprovalbyAI\\crewai\\translations\\en.json', 'crewai/translations'), ('C:\\Users\\ccerq\\OneDrive\\Documentos\\Python Scripts\\ML_CostAnalysis4_Branch3\\WOApprovalbyAI\\best_random_forest_model.joblib', '.')],
    hiddenimports=['embedchain', 'importlib_metadata', 'sklearn.ensemble._forest'],
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
    [],
    exclude_binaries=True,
    name='AI_WO_Approval',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_WO_Approval',
)

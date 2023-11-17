# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/numata/.pyenv/versions/3.11.3/lib/python3.11/site-packages/mediapipe/modules', 'mediapipe/modules'),
           ('/Users/numata/JPHACKS5/model/keypoint_classifier/keypoint_classifier.tflite', 'model/keypoint_classifier'),
           ('/Users/numata/JPHACKS5/model/point_history_classifier/point_history_classifier.tflite', 'model/point_history_classifier'),
           ('/Users/numata/JPHACKS5/model/keypoint_classifier/keypoint_classifier_label.csv', 'model/keypoint_classifier'),
           ('/Users/numata/JPHACKS5/model/point_history_classifier/point_history_classifier_label.csv', 'model/point_history_classifier')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='app',
    icon='/Users/numata/Documents/icon.icns',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

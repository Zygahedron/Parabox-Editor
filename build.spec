# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

version = "1.9.4"


a = Analysis(['sdl2_start.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['imgui.internal'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name=f'Zygan\'s Parabox Editor {version}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=False,
               upx_exclude=[],
               name=f'Zygan\'s Parabox Editor {version}')
app = BUNDLE(coll,
             name=f'Zygan\'s Parabox Editor {version}.app',
             icon=None,
             bundle_identifier=None)

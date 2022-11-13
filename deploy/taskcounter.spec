# -*- mode: python -*-

import os
import sys

block_cipher = None

if os.name == 'nt':
    icon = '../images/tasks.ico'
elif sys.platform == 'darwin':
    icon = '../images/tasks.icns'
else:
    icon = None

a = Analysis(['../main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Taskcounter',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=False, icon=icon)
app = BUNDLE(exe,
             name='Taskcounter.app',
             icon=icon,
             bundle_identifier='com.ardeidae.taskcounter',
             info_plist={
                 'NSHighResolutionCapable': 'True'
             },)

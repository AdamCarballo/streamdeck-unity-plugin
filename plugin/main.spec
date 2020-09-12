# -*- mode: python ; coding: utf-8 -*-
# pip install PyInstaller
# pip install websocket_client
# pip install six ->NEEDED?

block_cipher = None


a = Analysis(['main.py', 'actions.py', 'event_data.py', 'unity_response_data.py', 'unity_socket.py', 'websocket_server.py'],
             pathex=['C:\\Users\\batma\\AppData\\Roaming\\Elgato\\StreamDeck\\Plugins\\com.f10dev.unity.sdPlugin\\plugin'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='StreamDeckUnity',
		  icon='images\\actions\\icon.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

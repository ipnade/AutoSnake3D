# autosnake3d.spec
a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('textures/snake.png', 'textures'),  # Include texture
                ('config.py', '.'),                  # Include config
                ('game/*.py', 'game')               # Include game modules
             ],
             hiddenimports=[
                'pygame',
                'OpenGL.GL',
                'OpenGL.GLU',
                'OpenGL.arrays.vbo',
                'numpy'
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AutoSnake3D',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='textures/snake.png')
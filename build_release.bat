del /f mhwdb.exe & pyinstaller -w -F -i images\OfflineDatabase.ico src\Application.py & ren dist\Application.exe mhwdb.exe & move dist\mhwdb.exe ..\MonsterHunterWorld 
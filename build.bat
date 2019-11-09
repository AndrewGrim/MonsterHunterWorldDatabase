del /f "\Monster Hunter World Database\MHWDB-x64.exe" & 
pyinstaller -w -F -i images\Nergigante.ico src\Application.py & 
ren dist\Application.exe MHWDB-x64.exe & 
move dist\MHWDB-x64.exe "..\MonsterHunterWorld\Monster Hunter World Database\"

del /f "\Monster Hunter World Database\MHWDB-x86.exe" & 
%PYTHON32%\scripts\pyinstaller.exe -w -F -i images\Nergigante.ico src\Application.py & 
ren dist\Application.exe MHWDB-x86.exe & 
move dist\MHWDB-x86.exe "..\MonsterHunterWorld\Monster Hunter World Database\"

del /f "Monster Hunter World Database.zip"
python buildArchive.py
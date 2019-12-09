#!/usr/bin/env sh
pyinstaller -w -F -i "images/Nergigante.ico" "src/Application.py"
mv -f "dist/Application.exe" "MHWDB-x64.exe"

$PYTHON32/scripts/pyinstaller.exe -w -F -i "images/Nergigante.ico" "src/Application.py" 
mv -f "dist/Application.exe" "MHWDB-x86.exe" 

cd ../MHWorldData-Custom/ && ./build.sh && cp mhw.db ../MonsterHunterWorld/mhw.db

cd ../MonsterHunterWorld && python buildArchive.py
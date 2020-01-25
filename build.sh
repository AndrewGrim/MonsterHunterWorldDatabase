#!/bin/bash
pyinstaller -w -F -i "images/Nergigante.ico" "src/Application.py"
mv -f "dist/Application" "MHWDB-x64"

import zipfile
import os
import typing

def getDirPaths(dirName: str) -> None:
	"""
	Goes through the specified folder and retrieves all the file paths within.

	dirName = The path to the directory.
	"""

	filePaths = []
	for root, directories, files in os.walk(dirName):
		for filename in files:
			filePath = os.path.join(root, filename)
			filePaths.append(filePath)
			
	return filePaths


archive = zipfile.ZipFile("Monster Hunter World Database.zip", "w", zipfile.ZIP_DEFLATED, True, 9)
for f in getDirPaths("Monster Hunter World Database"):
	archive.write(f)
archive.close()
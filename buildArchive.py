import zipfile
import os
import typing
import shutil

def getDirPaths(dirName: str) -> List[str]:
	"""
	Goes through the specified folder and retrieves all the file paths within.

	Args:\n
		dirName: str = The path to the directory.

	Returns:\n
		filePaths: List[str] = A list of all the paths in the directory.
	"""

	filePaths = []
	for root, directories, files in os.walk(dirName):
		for filename in files:
			filePath = os.path.join(root, filename)
			filePaths.append(filePath)
			
	return filePaths


try:
	shutil.rmtree("Monster Hunter World Database")
	print("Finished clearing build folder")
except Exception as e:
	print(e)
try:
	shutil.copytree("images", "Monster Hunter World Database/images")
	print("Finished copying images")
except Exception as e:
	print(e)
files = ["CHANGELOG.md", "mhw.db", "preferences.config", "README.md", "LICENSE", "MHWDB-x86.exe", "MHWDB-x64.exe"]
for f in files:
	shutil.copy(f, "Monster Hunter World Database")
	print("Finished copying: ", f)
archive = zipfile.ZipFile("Monster Hunter World Database.zip", "w", zipfile.ZIP_DEFLATED, True, 9)
for f in getDirPaths("Monster Hunter World Database"):
	archive.write(f)
archive.close()
debug:
	pipenv run python src/Application.py
speed:
	pipenv run python tests/speedTest.py
db:
	cd ../MHWorldData-master/ && ./build.bat && cp mhw.db ../MonsterHunterWorld/mhw.db
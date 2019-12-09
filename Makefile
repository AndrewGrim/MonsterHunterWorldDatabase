debug:
	pipenv run python src/Application.py
speed:
	pipenv run python tests/speedTest.py
db:
	cd ../MHWorldData-Custom/ && ./build.sh && cp mhw.db ../MonsterHunterWorld/mhw.db
zip:
	./build.sh

import sqlite3

conn = sqlite3.connect('mhw.db')

# on second thought weapons and armor should be separated even if they will be displayed together in the program 
drop = "DROP TABLE palico_equipment"

create = """
CREATE TABLE palico_equipment (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	set_name TEXT NOT NULL,
	defense INTEGER NOT NULL,
	fire INTEGER NOT NULL,
	water INTEGER NOT NULL,
	ice INTEGER NOT NULL,
	thunder INTEGER NOT NULL,
	dragon INTEGER NOT NULL
)
"""
# need rarity as well
insert = """
INSERT INTO palico_equipment(id, name, set_name, defense, fire, water, ice, thunder, dragon)
	VALUES(0,'leather chest','leather',5,1,1,1,1,1)
"""
try:
	conn.execute(drop, ())
except Exception as e:
	print(e)

try:
	conn.execute(create, ())
except Exception as e:
	print(e)

try:
	conn.execute(insert, ())
except Exception as e:
	print(e)
conn.commit()

try:
	data = conn.execute("SELECT * FROM palico_equipment", ())
	for row in data:
		print(row)
except Exception as e:
	print(e)
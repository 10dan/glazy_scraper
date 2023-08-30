import sqlite3

conn = sqlite3.connect('recipes.db')
c = conn.cursor()
c.execute('SELECT recipe_id, images FROM recipes')
all_rows = c.fetchall()
for row in all_rows:
    print(row)
conn.close()
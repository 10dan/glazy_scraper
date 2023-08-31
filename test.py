import sqlite3

# conn = sqlite3.connect('recipes.db')
# c = conn.cursor()
# c.execute('SELECT * FROM recipes limit 5 ')
# all_rows = c.fetchall()
# for row in all_rows:
#     print(row)
# c.execute('select count(recipe_id) from recipes')
# count = c.fetchall()
# print(count)
# conn.close()

conn = sqlite3.connect('normalized_recipes.db')
c = conn.cursor()
c.execute('SELECT * FROM normalized_recipes limit 1 ')
all_rows = c.fetchall()
for row in all_rows:
    print(row)

conn.close()

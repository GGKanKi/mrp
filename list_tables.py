import sqlite3
from global_func import resource_path

path = resource_path('main.db')
print('db path', path)
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('tables', tables)
conn.close()
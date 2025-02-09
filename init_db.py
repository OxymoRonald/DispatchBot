# This script is to initialize the "discord_bot.db" database. It's included just incase the database gets corrupted.

# Import 
import sqlite3

# Create connection
conn = sqlite3.connect('discord_bot.db')

# Create cursor
c = conn.cursor()

# Create table
c.execute("""CREATE TABLE timetable (
          name TEXT,
          start TEXT,
          end TEXT,
          PRIMARY KEY(name, start)
    )""")

# commit
conn.commit()

# close the connection
conn.close()
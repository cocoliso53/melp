import sqlite3
import pandas as pd


conn = sqlite3.connect('restaurantes.db')
conn.execute('''CREATE TABLE Restaurants (id TEXT PRIMARY KEY, rating INTEGER, name TEXT, site TEXT, email TEXT, phone TEXT, street TEXT, city TEXT, state TEXT, lat FLOAT, lng FLOAT)''')
  
df = pd.read_csv('/app/restaurantes.csv')
  
for i,row in df.iterrows():
  conn.execute('''INSERT INTO Restaurants
                 (id, rating, name, site, email, phone, street, city, state, lat, lng)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
               (row[0], int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], row[8], float(row[9]), float(row[10])))
               
               
conn.commit()
conn.close()

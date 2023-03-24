from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from typing import Union
import statistics

import sqlite3

fields = ("id","rating","name","site","email","phone","street","city","state","lat","lng")

class Restaurant(BaseModel):
    id: str
    rating: int
    name: str
    site: str
    email: str
    phone: str
    street: str
    city: str
    state: str
    lat: float
    lng: float


class updateRestaurant(BaseModel):
    rating: Union[int, None] = None
    name: Union[str, None] = None
    site: Union[str, None] = None
    email: Union[str, None] = None
    phone: Union[str, None] = None
    street: Union[str, None] = None
    city: Union[str, None] = None
    state: Union[str, None] = None
    lat: Union[float, None] = None
    lng: Union[float, None] = None


app = FastAPI()

# We only adapt our function te query by ID, rating, or State.
# If we wanted to add more params the it would be easy but we'd have
# to add and if statement for each one of them making the code a bit more
# verbose. 
@app.get("/restaurants")
async def read(id: Union[str, None] = None, rating: Union[int, None] = None,
               state: Union[str, None] = None):

    base_str = "SELECT * FROM Restaurants WHERE {}"
    r = []
    l = []
    if id != None:
        l.append('id="{}"'.format(id))
    if rating != None:
        l.append("rating={}".format(rating))
    if state != None:
        l.append('state="{}"'.format(state))
    p = " AND ".join(l)
    query_str = base_str.format(p) if ((id != None) or (rating != None) or (state != None)) else "SELECT * FROM Restaurants"

    print("lol")

    conn = sqlite3.connect("../restaurantes.db")

    cursor = conn.cursor()
    cursor.execute(query_str)

    res = cursor.fetchall()

    conn.close()

    if len(res) < 1:
        raise HTTPException(status_code=404, detail="No such restaurant")

    for row in res:
        d = dict(zip(fields,row))
        r.append(Restaurant.parse_obj(d).json())

    

    return {"result": r}

# Simple function, really nothing fancy going on here
@app.post("/restaurants",status_code=201)
async def create(restaurant: Restaurant, response: Response):
    try:
        conn = sqlite3.connect("../restaurantes.db")
        print(tuple(restaurant.dict().values()))
        conn.execute('''INSERT INTO Restaurants
                 (id, rating, name, site, email, phone, street, city, state, lat, lng)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     tuple(restaurant.dict().values()))


        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail= e.args[0])
    finally:
        conn.close()

    # In theory we should return a location header like below,
    # but it will clash with /restaurants/statistics endpoint
    #response.headers["Location"] = "/restaurants/" + restaurant.id
    
    return {"result": restaurant}


# Again, very simple function. Nothing complicated happening here
@app.delete("/restaurants/{id}",status_code=204)
async def delete(id):

    try:
        conn = sqlite3.connect("../restaurantes.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Restaurants WHERE id="{}"'.format(id))
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPEXception(stauts_code=400, detail=e.args[0])
    finally:
        conn.close()

    return

# Here we use the class updateRestaurant defined before
# this give us the possibility of only accepting some
# parameters (the ones we want to update) instead of all of them
@app.patch("/restaurants/{id}",status_code=204)
async def put(id: str, restaurant: updateRestaurant):
    update_data = restaurant.dict(exclude_unset=True)
    base_str = 'UPDATE Restaurants SET {fields} WHERE id="{id}"'
    l = []
    for k,v in update_data.items():
        l.append('{k}="{v}"'.format(k=k,v=v) if type(v) == str else '{k}={v}'.format(k=k,v=v))

    field_str = ", ".join(l)
    query_str = base_str.format(fields=field_str,id=id)

    try:
        conn = sqlite3.connect("../restaurantes.db")
        cursor = conn.cursor()
        cursor.execute(query_str)
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    finally:
        conn.close()

    return


# We use package spatialite, sqlite3 geo extansion to
# make geographic queries
@app.get("/restaurants/statistics")
async def busca(latitud: float, longitud: float, radius: float):
    
    r = []
    conn = sqlite3.connect("../restaurantes.db")
    conn.enable_load_extension(True)
    conn.load_extension("mod_spatialite")
    query_str = "SELECT rating  FROM Restaurants WHERE Distance( ST_POINT(lat,lng), ST_POINT({lat},{lng}), TRUE) <= {rad};".format(lat=latitud,lng=longitud,rad=radius)
    cursor = conn.cursor()
    cursor.execute(query_str)

    res = cursor.fetchall()

    conn.close()

    
    if len(res) < 1:
        raise HTTPException(status_code=404, detail="No such restaurant")


    r = [x[0] for x in res]
    return {"result": {"count": len(r), "avg": statistics.mean(r), "std": statistics.stdev(r)}}

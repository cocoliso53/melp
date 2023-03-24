# Melp API

## Info

This is a simple FastAPI `python` project that crates a CRUO interface for a local `sqlite3` database, 
as such, all the modified data is lost each time the container builds again. Therefore it's not meant to be used in 
production.

This db is populated via popscript.py script, it reads data from `restaurates.csv` and creates a db named `restaurantes.db`.

You can interact with the api using your browser here [https://melp-production.up.railway.app/docs](https://melp-production.up.railway.app/docs)
or you can check the postman collection [here](https://postman.com/joint-operations-astronaut-91121978/workspace/my-workspace/collection/26550573-0b362c02-5f39-472d-b44e-4e5327e4b9a5?ctx=documentation)

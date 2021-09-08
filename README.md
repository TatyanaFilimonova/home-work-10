# home-work-10

Personal assistant with  data storage&operations implemented with MONGO. Also added LRU cache, that based  on REDIS.

Files:

**flask_app.py** - main module. LRU_cache used for wrapping of listener() function. Listener() does the neural prediction, and it is the most time expensive function.

**LRU_cache.py** - LRU cache on REDIS implementation 

**mongo_to_flask.py** - operation with MONGO: storing, searching and updating data

**mongo_DB_create_and_fill.py** - creating data collections and fill them with Faker data

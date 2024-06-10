# Core commands

Raise db in local (Need docker): 
```
docker compose -f .\mongo.yml up -d  
```

Laucn api
```
fastapi dev main.py
```

Setup mongo indexes (After runing the compose command):
```
python .\setup_index.py
```

URLS:
Swagger docs: http://127.0.0.1:8000/docs#/default
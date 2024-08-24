setup postgresql server, 
create user/password, 
setup in .env : DATABASE_URL=postgresql://[name]:[password]@localhost/[db_name]
                DEBUG=True
run init_db.py (in algo/app/)
sample routes in main.py
sample query:

curl -X POST http://localhost:8000/agencies/ -H "Content-Type: application/json" -d '{
  "id" : "hello", 
  "name": "Test Agency",
  "requirements": {
    "Halal": 10,
    "Vegetarian": 5
  },
  "priority_flag": true,
  "location": [1.5, -100]
}'



Postman testing collection (not exhaustive):
api_tests.json
import in postman as collection 

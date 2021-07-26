import json
profiles = {}
with open("teachers_db.json", "r") as database:
    profiles = json.load(database)
for profile in profiles:
    if profile['id'] in [8,9,10,11]:
        profile['goals'].append('programming')

with open("teachers_db.json","w") as database:
    data = json.dumps(profiles)
    database.write(data)

with open("goals_db.json", "r") as database:
        goals = json.load(database)
goals['programming'] = 'Для программирования'

with open("goals_db.json","w") as database:
    data = json.dumps(goals)
    database.write(data)
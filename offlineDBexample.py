# offlineDBexample.py
#
# Example code for how to interact with and edit database offline.
#


from os import environ as env 
from dotenv import load_dotenv, find_dotenv
import database as db

# Load environment variables
try:
    load_dotenv(find_dotenv())
except:
    print('.env not found.')
    raise RuntimeError(os.getcwd())
DBNAME = env.get('DBNAME')

# Connect mongoengine to database
db.eng.connect(DBNAME)

username = 'auser'
role = 'arole'

# Find a user by username
user = db.User.objects(username=username).first()

print('Current roles: %s' % str(user.roles))

# Update and save roles
user.update(roles=user.roles.append(role))
user.save()

print('Updated role: %s' % str(user.roles))

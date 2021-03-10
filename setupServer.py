# setupServer.py
#
# Configures .env file.
#
# Arguments:
#   SITEBASE_URL: the base URL of the website
#   DBNAME: the name of the MongoDB database to use
#

import sys
import os

def main(argv):
    if len(argv) != 2:
        print('\nNeeds 2 arguments.\n')
        print('Usage: setupServer.py baseURL databasename')
        print('Example: setupServer.py https://www.mysite.com mydb')
        return 0
    
    with open('.env','w') as f:
        f.write('SECRET_KEY='+os.urandom(24).hex()+'\n')
        f.write('SITEBASE_URL='+argv[0]+'\n')
        f.write('DBNAME='+argv[1]+'\n')
    
    print('Wrote .env file:\n')
    os.system('cat .env')
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])

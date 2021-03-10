# Code for generating a secret key for the app to use
#
# Place in the .env file.

import os
print(os.urandom(24).hex())

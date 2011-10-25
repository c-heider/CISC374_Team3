import sys
import os
sys.path.insert(0, os.path.abspath("libraries"))

import database

print database.list_users()
print database.login('test', 'test')
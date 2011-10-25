import sys
import os
sys.path.insert(0, os.path.abspath("libraries"))

import _server
import games.loader
import database_server
import fix_json

database_server.setup()

# print games.get_server_list()
# for x in games.get_server_list():
#     s = __import__('games.' + x + '.server')
#     s.setup()
_server.run()
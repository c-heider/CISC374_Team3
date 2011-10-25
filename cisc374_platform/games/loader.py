import os

def load_modules():
    res = {}
    lst = os.listdir("games")
    dir = []
    for d in lst:
        s = os.path.abspath("games") + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            dir.append(d)
    # Don't load internal modules
    dir = [d for d in dir if d[0] != '_']
    return [__import__("games." + d, fromlist = ["*"]) for d in dir]

def get_list():
    modules = load_modules()
    return [x.launcher_info for x in modules]

def get_server_list():
    res = {}
    lst = os.listdir("games")
    dir = []
    for d in lst:
        s = os.path.abspath("games") + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            dir.append(d)
    lst = []
    dir = [d for d in dir if
                os.path.exists(os.path.abspath("games") + os.sep + 
                                                d + os.sep + "server.py")]
    return dir
import _db

# Here we just point to the database api location. This is the one which is
# the default for the server_launcher.py when developing locally
_db.set_api_endpoint("http://localhost:5000/api/")
_user = ''
_pass = ''
_logged_in = False

def login(user, password):
    # We save the username and password so that we can continue to pass it along
    # for requests, so that every time the server knows who is logged in
    global _user, _pass, _logged_in
    # This is how we pull data from the server. The first parameter is the
    # action we want to perform. It will be added to the end of the API endpoint
    # So that on the server a request comes to /api/login, for example.
    # The second argument is the data we wish to pass along in a dictionary.
    # It will be json encoded for the server.
    r = _db.query('login', {'user' : user, 'pass' : password})
    if r['success'] == True:
        _user = user
        _pass = password
        _logged_in = True
        return True
    else:
        return False
        
def list_users():
    r = _db.query('list_users')
    return r['data']
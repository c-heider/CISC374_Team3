from _server import db, app
import sqlalchemy
from flaskext.sqlalchemy import SQLAlchemy
from flask import jsonify, request
import json
from hashlib import sha512

# This creates a table called User in our database
# Any table which should be in the database should inherit from db.Model
# For more on how to declare models, see:
# http://packages.python.org/Flask-SQLAlchemy/models.html
class User(db.Model):
    # These are three columns in the database
    username = db.Column(db.String(80), unique = True, primary_key = True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    type = db.Column(db.String(80), nullable = False)
    
    # This constructor is for us, not the database. It gives us an easy
    # way to create one User to be added to the database.
    def __init__(self, user, password, type = 'student'):
        self.username = user
        self.password = password
        self.type = type

# This method is currently called by the server_launcher every time it is
# started. 
def setup():
    # During development, since the schema may be changing, we currently
    # drop all the tables and recreate them all.
    db.drop_all()
    db.create_all()
    # This is an example of creating a User and adding them to the database
    test_user = User('test', sha512('test').hexdigest())
    db.session.add(test_user)
    db.session.commit()

# The app.route() decorator tells the server that this function should respond
# to requests from the first argument, and it should accept the methods listed
# in methods. We use the convention that all api calls to the server should be
# using /api/ as the prefix
@app.route('/api/login', methods = ['GET', 'POST'])
def login():
    # On the server side, we will always return json.
    # The client side automatically decodes the json for the responses
    # jsonify is an apppropriate json encoder to use on the server side
    fail = jsonify({'success' : False})
    # The client always sends all of the data as a dictionary titled data,
    # so we json decode that
    data = json.loads(request.form['data'])
    # We try to get a User named data['user'] from the database
    # For more on how to perform queries, see:
    # http://packages.python.org/Flask-SQLAlchemy/queries.html
    user = User.query.get(data['user'])
    # If it's None, then the query failed
    if user is None:
        return fail
    # We just verify their password
    if user.password != sha512(data['pass']).hexdigest():
        return fail
    # If it works, return true
    return jsonify({'success' : True})
    
@app.route('/api/list_users', methods = ['GET', 'POST'])
def list_users():
    # Here we just query all the users in the database
    users = [user.username for user in User.query.all()]
    return jsonify({'data' : users})
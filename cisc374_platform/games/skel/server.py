from _server import db, app
import sqlalchemy
from flaskext.sqlalchemy import SQLAlchemy
from flask import jsonify, request
import json

class skel_data(db.Model):
    id = db.Column(db.Integer, unique = True, primary_key = True, nullable = False)
    random_data = db.Column(db.String(80), nullable = False)
    type = db.Column(db.String(80), nullable = False)
    
    def __init__(self, data):
        self.username = user
        self.password = password
        self.type = type

def setup():
    db.drop_all()
    db.create_all()
    test_user = User('test', sha512('test').hexdigest())
    db.session.add(test_user)
    db.session.commit()
    
@app.route('/api/skel_hello', methods = ['GET', 'POST'])
def login():
    return jsonify('hello')
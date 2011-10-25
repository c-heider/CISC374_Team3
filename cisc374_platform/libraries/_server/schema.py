# This file really needs a better name. We'll discuss later
from accounts_web import db
import sqlalchemy
from flaskext.sqlalchemy import SQLAlchemy

class User(db.Model):
    username = db.Column(db.String(80), unique = True, primary_key = True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    type = db.Column(db.String(80), nullable = False)
    
    def __init__(self, user, password, type = 'student'):
        self.username = user
        self.password = password
        self.type = type

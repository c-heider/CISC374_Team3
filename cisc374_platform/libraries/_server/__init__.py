from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
import config

app = Flask(__name__.split('.')[0])
app.config.from_object(config.FlaskConfig)
db = SQLAlchemy(app)
import pages


def run():
    app.run(host='0.0.0.0', port=config.dev_port)
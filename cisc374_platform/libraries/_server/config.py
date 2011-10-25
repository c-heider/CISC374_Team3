# Uncomment this for the database type
# db_type = 'mysql'
db_type = 'sqlite'

sqlite_file = 'db.sqlite'

mysql = {}
mysql['user']    = 'cisc374'
mysql['pass']    = 'not_password'
mysql['host']    = 'localhost'
mysql['port']    = '3306'
mysql['db']      = 'accounts'
mysql['charset'] = 'utf8'
mysql['driver']  = 'pymysql'

flask_debug = True
dev_port = 5000

# Don't touch from here down!
if db_type == 'sqlite':
    class FlaskConfig():
        DEBUG = flask_debug
        SQLALCHEMY_DATABASE_URI =\
            'sqlite:///%s' % sqlite_file
else:
    class FlaskConfig():
        DEBUG = flask_debug
        SQLALCHEMY_DATABASE_URI =\
            'mysql+%(driver)s://%(user)s:%(pass)s@%(host)s:%(port)s/%(db)s?charset=%(charset)s' % mysql

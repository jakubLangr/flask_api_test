import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../tests/data-test.sqlite')

DEBUG = False
TESTING = True
IGNORE_AUTH = False
SECRET_KEY = 'top-secret!'
SERVER_NAME = 'example.com'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path

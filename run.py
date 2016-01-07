#!/usr/bin/env python
import os
from app_v1.__init__ import create_app, db
from flask.ext.sqlalchemy import SQLAlchemy
from app_v1.models import User

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')


DEBUG = True
IGNORE_AUTH = True
SECRET_KEY = 'top-secret!'

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        db = SQLAlchemy()
        db.create_all()
        # create a development user
        if User.query.get(1) is None:
            u = User(username='john')
            u.set_password('horsenosebattery')
            db.session.add(u)
            db.session.commit()
    app.run()

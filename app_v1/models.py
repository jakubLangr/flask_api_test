import os
from flask import Flask, url_for, jsonify, request, g, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.tz import tzutc
from dateutil import parser as datetime_parser
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .utils import split_url
from .__init__ import db

class ValidationError(ValueError):
    pass


class User(db.Model):
    '''
    CREATE TABLE users(
   ...> id integer PRIMARY KEY NOT NULL,
   ...> username string NOT NULL,
   ...> password_hash string NOT NULL);
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

class Module(db.Model):
    __tablename__ = 'modules'
    __table_args__ = { 'sqlite_autoincrement': True }
    id = db.Column( db.Integer, primary_key=True )
    UserId = db.Column( db.String(255) ) 
    CourseSoftwareId = db.Column( db.String(255) )
    CourseMaterialId = db.Column( db.String(255) )
    N2K = db.Column( db.Float )
    DAK = db.Column( db.Float )
    Included = db.Column( db.Integer )
    CreatedDate = db.Column( db.DateTime, default=datetime.now )
    ModifiedDate = db.Column( db.DateTime, default=datetime.now )
    FilteredOut = db.Column( db.Integer )

    def get_url(self):
        return url_for('get_module', id=self.id, _external=True)

    def export_data(self):
        return {
            #'self_url' : self.get_url(),
            'id' : self.id,
            'UserId' : self.UserId,
            'CourseSoftwareId' : self.CourseSoftwareId,
            'CourseMaterialId' : self.CourseMaterialId,
            'CreatedDate'  : self.CreatedDate.isoformat() + 'Z',
            'ModifiedDate' : self.ModifiedDate.isoformat() + 'Z',
            'Included' : self.Included,
            'N2K' : self.N2K,
            'DAK' : self.DAK,
            'FilteredOut' : self.FilteredOut
        }

    def import_data(self, data):
        try:
            # self.id = data['id']
            self.UserId = data['UserId']
            self.CourseSoftwareId = data['CourseSoftwareId']
            self.CourseMaterialId = data['CourseMaterialId']
            self.N2K = data['N2K']
            self.DAK = data['DAK']
            self.Included = data['Included']
            self.CreatedDate = datetime_parser.parse(
                data['CreatedDate'])
            self.ModifiedDate = datetime_parser.parse(
                data['ModifiedDate'])
            self.FilteredOut = data['FilteredOut']
        except KeyError as e:
            raise ValidationError('Invalid row (module), missing ' + e.args[0] )
        return self


class FilterReply(db.Model):
    # waypoints for standalone filter and rough timelines 
    # draw out conclusions & snapshots 
    # live demo of Flask API?
    __tablename__ = 'filterReplies'
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.String(64), index=True)
    CourseSoftwareId = db.Column(db.String(64))
    Type = db.Column(db.String(64))
    Answer = db.Column(db.String(64))
    MaxAnswer = db.Column(db.String(64))
    CreatedDate = db.Column(db.DateTime, default=datetime.now)
    ModifiedDate = db.Column(db.DateTime, default=datetime.now)

    def get_url(self):
        print( url_for('get_filter_reply', id=self.id , _external=True ) )
        return url_for('get_filter_reply', id=self.id , _external=True)

    def export_data(self):
        return {
            # 'self_url' : self.get_url(),
            'id' : self.id,
            'UserId': self.UserId,
            'CourseSoftwareId' : self.CourseSoftwareId,
            'Type' : self.Type,
            'Answer' : self.Answer,
            'MaxAnswer' : self.MaxAnswer,
            'CreatedDate'  : self.CreatedDate.isoformat() + 'Z',
            'ModifiedDate' : self.ModifiedDate.isoformat() + 'Z'
        }

    def import_data(self, data):
        try:
            # self.id = data['id']
            self.UserId = data['UserId']
            self.CourseSoftwareId = data['CourseSoftwareId']
            self.Type = data['Type']
            self.Answer = data['Answer']
            self.MaxAnswer = data['MaxAnswer']
            self.CreatedDate = datetime_parser.parse(
                data['CreatedDate'])
            self.ModifiedDate = datetime_parser.parse(
                data['ModifiedDate'])
        except KeyError as e:
            raise ValidationError('Invalid row (module), missing ' + e.args[0] )
        return self

import os
from flask import Flask, url_for, jsonify, request, g 
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.tz import tzutc
from dateutil import parser as datetime_parser
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import split_url
from .__init__ import db


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
        return url_for('get_module', UserId=self.UserId, _external=True)

    def export_data(self):
        return {
            'self_url' : self.get_url(),
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
        ''' Schema: 
            CREATE TABLE modules (
                 id integer PRIMARY KEY NOT NULL,
                 UserId integer NOT NULL,
                 CourseSoftwareId NOT NULL, 
                 CourseMaterialId NOT NULL,
                 N2K float,
                 DAK float,
                 Included Integer,
                 FilteredOut Integer,
                 CreatedDate datetime,
                 ModifiedDate datetime
                 ); '''
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
        return url_for('get_filter_reply', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url' : self.get_url(),
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
            ''' Schema
            CREATE TABLE filterReplies ( 
                id Integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                UserId String NOT NULL,
                CourseSoftwareId string NOT NULL,
                Type String,
                Answer Float,
                MaxAnswer Integer,
                CreatedDate datetime,
                ModifiedDate datetime);'''

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

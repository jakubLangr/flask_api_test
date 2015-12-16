import os
from flask import Flask, url_for, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.tz import tzutc
from dateutil import parser as datetime_parser
from utils import split_url

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass

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


@app.route('/filterReplies/', methods=['POST'])
def new_filter_reply():
    '''
    http POST http://localhost:5000/filterReplies/ id=1 UserId=aaaa CourseSoftwareId=aaaaa Type=AOI Answer=5 MaxAnswer=12 CreatedDate='22 Jan 2013' ModifiedDate='23 Jun 2013'
    '''
    filter_reply = FilterReply()
    filter_reply.import_data(request.json)
    db.session.add(filter_reply)
    db.session.commit()
    return jsonify({}), 201, {'Location' : filter_reply.get_url() }

@app.route('/filterReplies/', methods=['GET'])
def get_filter_replies():
    return jsonify( {'filterReplies' : [ reply.export_data() for reply in FilterReply.query.all()]} )

@app.route('/filterReplies/<int:id>', methods=['GET'])
def get_filter_reply(id):
    return jsonify(FilterReply.query.get_or_404(id).export_data())

@app.route('/modules/', methods=['GET'])
def get_modules():
    return jsonify({'modules' : [ module.get_url() for module in Module.query.all() ] })

@app.route('/modules/<string:UserId>', methods=['GET'])
def get_module(UserId):
    # results = [ (module.id,module.export_data()) for module in Module.query.all() if module.UserId==UserId ] 
    # The below is probably a better way to do it
    results = [ (module.id, module.export_data()) for module in  Module.query.filter_by(UserId=UserId).all() ]  
    return jsonify( results )

@app.route('/modules/<int:id>', methods=['PUT'])
def edit_module(id):
    module = Module.query.get_or_404(id)
    module.import_data(request.json)
    db.session.add(module)
    db.session.commit()
    return jsonify({})

@app.route('/modules/', methods=['POST'])
def new_module():
    '''
    http POST http://localhost:5000/modules/ UserId='aaac' id=12 CourseSoftwareId='aaaaa' CourseMaterialId='bbbbb' N2K=.25 DAK=.32 Included=1 FilteredOut=0 CreatedDate='22 Jan 2013' ModifiedDate='23 Jun 2013'

    Location: http://localhost:5000/modules/aaac
    '''
    module = Module()
    module.import_data(request.json)
    db.session.add(module)
    db.session.commit()
    return jsonify({}), 201, {'Location': module.get_url()}

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

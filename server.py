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

def check_presence(data_attr, item):
    if data_attr.UserId==item:
        return item
    else:
        pass


class ValidationError(ValueError):
    pass

class Module(db.Model):
    __tablename__ = 'modules'
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
            self.id = data['id']
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

@app.route('/modules/', methods=['GET'])
def get_modules():
    return jsonify({'modules' : [ module.get_url() for module in Module.query.all() ] })

@app.route('/modules/<int:id>', methods=['GET'])
def get_module(id):
    # the call here passes UserId correctly, investigate get_or_404 method 
    # [SQL: u'SELECT dummy.id AS dummy_id \nFROM dummy \nWHERE dummy.id = ?'] [parameters: ('hi',)]
    # SELECT modules.UserId AS module_UserId FROM modules WHERE modules.UserId = 'aaac';
    # Turns out get_or_404 uses the primary key only, so I cannot query on UserId
    # response =  Module.query.all()
    # response = map(check_presence(response, UserId), response)
    # response = {'modules' : [ module for module in Module.query.all() ] }
    # Module.query.filter(Module.UserId==UserId)
    '''
    all_modules = Module.query.all()
    response = []
    for module in all_modules:
        if module.UserId == UserId:
            response.append(module)
    return response
    '''
    return jsonify(Module.query.get_or_404(id).export_data())

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

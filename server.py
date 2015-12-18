import os
from flask import Flask, url_for, jsonify, request, g 
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.tz import tzutc
from dateutil import parser as datetime_parser
from werkzeug.security import generate_password_hash, check_password_hash
from utils import split_url

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass

@app.before_request
@auth.login_required
def before_request():
    pass


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

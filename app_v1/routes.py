from flask import jsonify, request
from datetime import datetime
from dateutil import parser as datetime_parser
from flask import url_for, current_app, Blueprint
from .models import User, Module, FilterReply
from .__init__ import db 


api = Blueprint('api', __name__)


@api.route('/filterReplies/', methods=['POST'])
def new_filter_reply():
    '''
    http --auth jakub:Freeman POST http://localhost:5000/filterReplies/ UserId=aaaa CourseSoftwareId=aaaaa Type=AOI Answer=5 MaxAnswer=12 CreatedDate='22 Jan 2013' ModifiedDate='23 Jun 2013'
    '''
    filter_reply = FilterReply()
    filter_reply.import_data(request.json)
    db.session.add(filter_reply)
    db.session.commit()
    return jsonify({}), 201, {'Location' : filter_reply.id } # this also needs to be changed? seems correct

@api.route('/filterReplies/', methods=['GET'])
def get_filter_replies():
    return jsonify( {'filterReplies' : [ reply.export_data() for reply in FilterReply.query.all()]} )

@api.route('/filterReplies/<int:id>', methods=['GET'])
def get_filter_reply(id):
    '''
    http --auth jakub:Freeman GET http://localhost:5000/filterReplies/1
    '''
    return jsonify(FilterReply.query.get_or_404(id).export_data())

@api.route('/filterReplies/<int:id>', methods=['PATCH'])
def modify_filter_reply(id):
    '''
    http  --auth jakub:Freeman PATCH http://localhost:5000/filterReplies/2 UserId='Jakub Langr'
    '''
    filter_reply = FilterReply.query.get_or_404(id)
    filter_reply_data = filter_reply.export_data()
    new_data = request.json 
    for datum in new_data.keys():
        filter_reply_data[datum] = new_data[datum]

    # this ridiculousness is because of bs way that python handles datetime and the
    # inability of SQLite to convert timezone aware to naive datetimes  
    filter_reply_data['ModifiedDate'] = datetime.utcnow().isoformat()
    filter_reply_data['CreatedDate'] = datetime_parser.parse(filter_reply_data['CreatedDate']).replace(tzinfo=None).isoformat()
    filter_reply.import_data(filter_reply_data)
    db.session.add(filter_reply)
    db.session.commit()
    return jsonify({})

@api.route('/filterReplies/<string:CourseSoftwareId>/<string:UserId>', methods=['GET'])
def get_filter_reply_id(CourseSoftwareId,UserId):
    '''
    http --auth jakub:Freeman GET http://localhost:5000/filterReplies/aaaaa/aaaa
    '''
    results = FilterReply.query.filter_by(CourseSoftwareId=CourseSoftwareId,
        UserId=UserId)
    results = { 'ids' : [result.id for result in results ] }
    return jsonify( results )

@api.route('/modules/', methods=['GET'])
def get_modules():
    return jsonify({'modules' : [ module.get_url() for module in Module.query.all() ] })

@api.route('/modules/<int:id>', methods=['GET'])
def get_module(id):
        # callback = [ module.export_data() for module in callback ]  
        # results['response'] = callback
        # results = [ (module.export_data(), 'hi') for module in  Module.query.filter_by(UserId=UserId).all() ]  
    # results = { 'response ids' : [ module.id for module in Module.query.filter_by(UserId=UserId).all() ] }
    return jsonify( Module.query.get_or_404(id).export_data(œ) )

@api.route('/module-id/<string:CourseSoftwareId>/<string:CourseMaterialId>/<string:UserId>', methods=['GET'])
def get_module_id(CourseMaterialId,CourseSoftwareId,UserId):
    '''
    http --auth jakub:Freeman GET http://localhost:5000/module-id/aaaaa/bbbbb/aaac
    '''
    results = Module.query.filter_by(CourseSoftwareId=CourseSoftwareId,
        CourseMaterialId=CourseMaterialId, UserId=UserId).all()
    results = {'ids': [ result.id for result in results ] }
    return jsonify( results )

@api.route('/modules/<int:id>', methods=['PATCH'])
def edit_module(id):
    module = Module.query.get_or_404(id)
    module_data = module.export_data()
    new_data = request.json 
    for datum in new_data.keys():
        module_data[datum] = new_data[datum]

    # this ridiculousness is because of bs way that python handles datetime and the
    # inability of SQLite to convert timezone aware to naive datetimes  
    module_data['ModifiedDate'] = datetime.utcnow().isoformat()
    module_data['CreatedDate'] = datetime_parser.parse(module_data['CreatedDate']).replace(tzinfo=None).isoformat()
    module.import_data(module_data)
    db.session.add(module)
    db.session.commit()
    return jsonify({})

@api.route('/modules/', methods=['POST'])
def new_module():
    '''
    http --auth jakub:Freeman POST http://localhost:5000/modules/ UserId='aaac' CourseSoftwareId='aaaaa' CourseMaterialId='bbbbb' N2K=.25 DAK=.32 Included=1 FilteredOut=0 CreatedDate='22 Jan 2013' ModifiedDate='23 Jun 2013'

    Location: http://localhost:5000/modules/aaac
    '''
    module = Module()
    module.import_data(request.json)
    db.session.add(module)
    db.session.commit()
    return jsonify({}), 201, {'Location': module.get_url()}

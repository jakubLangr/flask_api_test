import os
from flask import Flask, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)

    from models import FilterReply, Module
    from flask import request

    # apply configuration
    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)

    # initialize extensions
    db.init_app(app)

    # authentication token route
    from auth import auth
    @app.route('/get-auth-token')
    @auth.login_required
    def get_auth_token():
        return jsonify({'token': g.user.generate_auth_token()})

    # register blueprints
    #from .api_v1 import api as api_blueprint
    #app.register_blueprint(api_blueprint, url_prefix='/api/v1')

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

    #@app.route('/filterReplies/<')

    @app.route('/modules/', methods=['GET'])
    def get_modules():
        return jsonify({'modules' : [ module.get_url() for module in Module.query.all() ] })

    @app.route('/modules/<string:UserId>', methods=['GET'])
    def get_module(UserId):
        results = [ (module.id, module.export_data()) for module in  Module.query.filter_by(UserId=UserId).all() ]  
        return jsonify( results )

    @app.route('/module-id/<string:CourseSoftwareId>/<string:CourseMaterialId>/<string:UserId>', methods=['GET'])
    def get_module_id(CourseMaterialId,CourseSoftwareId,UserId):
        '''
        http --auth jakub:Freeman GET http://localhost:5000/module-id/aaaaa/bbbbb/aaac
        '''
        
        results = Module.query.filter_by(CourseSoftwareId=CourseSoftwareId,
            CourseMaterialId=CourseMaterialId, UserId=UserId).all()
        results = {'ids': [ result.id for result in results ] }
        return jsonify( results )

    @app.route('/modules/<int:id>', methods=['PATCH'])
    def edit_module(id):
        module = Module.query.get_or_404(id)
        module.import_data(request.json)
        db.session.add(module)
        db.session.commit()
        return jsonify({})

    @app.route('/modules/', methods=['POST'])
    def new_module():
        '''
        http POST http://localhost:5000/modules/ UserId='aaac' CourseSoftwareId='aaaaa' CourseMaterialId='bbbbb' N2K=.25 DAK=.32 Included=1 FilteredOut=0 CreatedDate='22 Jan 2013' ModifiedDate='23 Jun 2013'

        Location: http://localhost:5000/modules/aaac
        '''
        module = Module()
        module.import_data(request.json)
        db.session.add(module)
        db.session.commit()
        return jsonify({}), 201, {'Location': module.get_url()}

    return app
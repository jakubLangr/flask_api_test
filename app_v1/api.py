import os
from flask import Flask, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Blueprint


db = SQLAlchemy()
api = Blueprint('api', __name__)


def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)

    from .models import FilterReply, Module
    from flask import request

    # apply configuration
    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)

    # initialize extensions
    db.init_app(app)

    # authentication token route
    from .auth import auth
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
    
    # get routes    
    cfg = os.path.join(os.getcwd(), 'app_v1', 'routes.py')
    app.config.from_pyfile(cfg)


    return app
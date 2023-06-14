from flask import Flask

from flask_migrate import Migrate

from flask_login import LoginManager, current_user

from .models import db, User

from flask_bcrypt import Bcrypt
from flask_breadcrumbs import Breadcrumbs

import  pytz

from app.blueprints.devices.devicesAPI import devices_api
from app.blueprints.directories.directoriesAPI import directories_api
from app.blueprints.posts.postAPI import posts_api
from app.blueprints.records.recordsAPI import records_api
from app.blueprints.buildings.buildingsAPI import buildings_api
from app.blueprints.visual.visualAPI import visual_api
from app.timeAPI import time_api
from app.blueprints.flows.flowsAPI import flows_api
from app.blueprints.objects.objectAPI import object_api
from app.blueprints.map.map_bp import map_bp
from app.blueprints.user.user_bp import user_bp
from app.blueprints.gateway.gatewayAPI import gateway_api

# for degugging
'''
def create_app():

    app = Flask(__name__, static_url_path='/static')

    app.register_blueprint(devices_api)

    app.config['SECRET_KEY'] = 'key'
    app.config["DEBUG"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return app
'''

app = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = '/static/upload'

app.config['SECRET_KEY'] = 'key'
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUF'] = True
app.config['JSON_AS_ASCII'] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://metadb_dev2:D5R4wyCGsrZDJMza@metadb.ru/metadb_dev2'


Breadcrumbs(app=app)
login = LoginManager()
login.init_app(app)
login.login_view = 'user_bp.login'
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt()

app.register_blueprint(devices_api)
app.register_blueprint(directories_api)
app.register_blueprint(posts_api)
app.register_blueprint(records_api)
app.register_blueprint(buildings_api)
app.register_blueprint(visual_api)
app.register_blueprint(time_api)
app.register_blueprint(flows_api)
app.register_blueprint(map_bp)
app.register_blueprint(object_api)
app.register_blueprint(user_bp)
app.register_blueprint(gateway_api)



def datetime_user_tz(value, format="%d.%m.%Y, %H:%M:%S"):
    if current_user.timezone is not None:
        tz = pytz.timezone(current_user.timezone)
    else:
        tz = pytz.timezone("UTC")

    local_dt = tz.fromutc(value)
    return local_dt.strftime(format)


app.jinja_env.filters['datetime_user_tz'] = datetime_user_tz

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

from app import views



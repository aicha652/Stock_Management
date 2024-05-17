import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet,configure_uploads, patch_request_class
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


app = Flask(__name__)


# *Handling Images* #
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADED_PHOTOS_DEST'] = os.pathsep.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)



# *DataBase Setup* #
app.config['SECRET_KEY'] = '0123456789abcdefghij'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://stock_db:password123@localhost/Stock'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)



migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app,db, render_as_batch=True)
    else:
        migrate.init_app(app,db)



login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u"Please Login Sir/ Madam"


# *Password Hashing* #

bcrypt = Bcrypt(app)

# *Routes* #
from Stock import routes
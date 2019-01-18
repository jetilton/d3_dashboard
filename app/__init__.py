from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login =LoginManager(app)
bootstrap = Bootstrap(app)
login.login_view = 'login'

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')




from app.views import routes
from app import models


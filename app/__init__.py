from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap



db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.map import bp as map_bp
    app.register_blueprint(map_bp, url_prefix='/map')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')
    
    from app.dash import bp as dash_bp
    app.register_blueprint(dash_bp, url_prefix='/dash')
    return app








from app import models


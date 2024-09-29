from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from .route.valve_routes import valve_bp as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix=Config.BASE_PATH)

    from .route.trigger_routes import trigger_bp as trigger_blueprint
    app.register_blueprint(trigger_blueprint, url_prefix=Config.BASE_PATH)

    from .route.factor_routes import factor_bp
    app.register_blueprint(factor_bp, url_prefix=Config.BASE_PATH)

    return app
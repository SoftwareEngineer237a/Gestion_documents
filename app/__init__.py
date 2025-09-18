from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config

# Initialiser extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"  # redirection si non connecté

    # Importer tous les modèles pour éviter les problèmes de dépendances croisées
    from app import models

    # Enregistrer les blueprints
    from app.routes.auth_route import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.routes.employee_route import employee_bp
    from app.routes.manager_route import manager_bp
    from app.routes.security_route import security_bp
    from app.routes.admin_route import admin_bp

    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(security_bp, url_prefix="/security")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
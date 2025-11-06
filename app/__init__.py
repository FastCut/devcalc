from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Inicjalizacja rozszerzeń
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Factory function do tworzenia aplikacji Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicjalizacja rozszerzeń z aplikacją
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'

    # Rejestracja blueprintów
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.calculator import bp as calc_bp
    app.register_blueprint(calc_bp)

    from app.costs import bp as costs_bp
    app.register_blueprint(costs_bp, url_prefix='/costs')

    # Tworzenie tabel bazy danych
    with app.app_context():
        db.create_all()
        # Inicjalizacja domyślnych kosztów jednostkowych
        from app.models import CostDatabase
        if CostDatabase.query.count() == 0:
            CostDatabase.init_default_costs()

    return app

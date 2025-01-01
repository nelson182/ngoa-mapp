from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Importer la configuration
import pymysql
pymysql.install_as_MySQLdb()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Appliquer la configuration depuis config.py
    
    db.init_app(app)  # Initialiser SQLAlchemy avec l'application Flask

    with app.app_context():
        db.create_all()  # Créer les tables si elles n'existent pas encore

    return app


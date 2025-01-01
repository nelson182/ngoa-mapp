import os

class Config:
    # Configuration de la base de données MySQL avec Flask
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'QLkbNBDfWudjxFlceZdhilMyFDyVOvul')
    DB_HOST = os.getenv('DB_HOST', 'junction.proxy.rlwy.net')
    DB_PORT = os.getenv('DB_PORT', '29125')
    DB_NAME = os.getenv('DB_NAME', 'railway')

    # Construire l'URI de la base de données MySQL
    SQLALCHEMY_DATABASE_URI = f'mysql://root:QLkbNBDfWudjxFlceZdhilMyFDyVOvul@junction.proxy.rlwy.net:29125/railway'

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactiver la surveillance des modifications des objets
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre_cle_secrete')  # Clé secrète pour Flask


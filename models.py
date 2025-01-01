from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import create_app, db

class User(db.Model):  # Nom de la classe en français
    __tablename__ = 'utilisateurs'  # Le nom de la table dans la base de données

    # Définition des colonnes de la table
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)  # 'name' devient 'nom'
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)  # 'password' devient 'mot_de_passe'
    age = db.Column(db.Integer, nullable=False)

    # Relation avec la table evaluer
    evaluations = db.relationship('Evaluation', backref='utilisateur', lazy=True)

    # Méthode pour enregistrer un nouvel utilisateur avec un mot de passe haché
    def definir_mot_de_passe(self, mot_de_passe):
        self.mot_de_passe = generate_password_hash(mot_de_passe)

    # Méthode pour vérifier si un mot de passe correspond au mot de passe haché
    def verifier_mot_de_passe(self, mot_de_passe):
        return check_password_hash(self.mot_de_passe, mot_de_passe)


class Evaluation(db.Model):  # Classe pour la table des évaluations
    __tablename__ = 'evaluer'  # Nom de la table dans la base de données

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note = db.Column(db.Integer, nullable=False)  # Note donnée par l'utilisateur
    commentaire = db.Column(db.Text, nullable=True)  # Commentaire optionnel
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)  # Clé étrangère vers utilisateurs

    def __repr__(self):
        return f"<Evaluation {self.id} - Note: {self.note}, Utilisateur ID: {self.utilisateur_id}>"


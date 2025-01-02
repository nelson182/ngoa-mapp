from flask import Flask
from __init__ import create_app, db
import lxml.etree as ET
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import pymysql
pymysql.install_as_MySQLdb()
# ... ( modèle Batiment et la configuration de la base de données restent inchangés)
Base = declarative_base()

class Batiment(db.Model):
    __tablename__ = 'batiments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(255))
    coordonneex = db.Column(db.Float)
    coordonneey = db.Column(db.Float)
    type = db.Column(db.String(255), default="Inconnu")
    images = db.Column(db.String(255), default="/images/default.jpg")
    description = db.Column(db.String(255), default="non précisé")
    salles = db.relationship('Salle' , back_populates='batiments' , cascade='all, delete-orphan')

class Salle(db.Model):
    __tablename__ = 'salles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), default="non précisé")
    coordonneex = db.Column(db.Float, default=None)
    coordonneey = db.Column(db.Float, default=None)
    images = db.Column(db.String(255), default="/images/default.jpg")
    id_batiment = db.Column(db.Integer, db.ForeignKey('batiments.id'), default=None)
    batiments = db.relationship('Batiment' , back_populates='salles')

    # Relation avec la classe Batiment (clé étrangère)
    batiment = db.relationship('Batiment', back_populates='salles')
app = create_app()

# Configuration de la base de données
# Créer la session SQLAlchemy
engine = create_engine(f'mysql://root:QLkbNBDfWudjxFlceZdhilMyFDyVOvul@junction.proxy.rlwy.net:29125/railway')
Session = sessionmaker(bind=engine)
db_session = Session()


def extraire_et_inserer_batiments(fichier_osm):
    tree = ET.parse(fichier_osm)
    root = tree.getroot()

    batiments = []
    batch_size = 400

    # Dictionnaire pour stocker les coordonnées des nodes
    nodes_coords = {}
    for node in root.iter('node'):
        nodes_coords[int(node.get('id'))] = (float(node.get('lat')), float(node.get('lon')))

    # Obtenir tous les noms déjà présents dans la base
    session = Session()
    try:
        noms_existants = {b.nom for b in session.query(Batiment.nom).all()}
        print(noms_existants)
    finally:
        session.close()

    for tag in root.iter('tag'):
        if tag.get('k') == 'name':
            parent = tag.getparent()
            if parent is not None:
                if parent.tag == 'node':
                    # Cas d'un nœud
                    lat = float(parent.get('lat')) if parent.get('lat') else None
                    lon = float(parent.get('lon')) if parent.get('lon') else None
                    nom = tag.get('v')
                    if nom not in noms_existants:  # Vérifier si le nom n'existe pas déjà
                        batiments.append(Batiment(nom=nom, coordonneex=lat, coordonneey=lon))
                elif parent.tag == 'way':
                    # Parcourir tous les <nd> pour trouver une correspondance
                    for nd in parent.findall('./nd'):
                        ref = int(nd.get('ref'))
                        if ref in nodes_coords:
                            lat, lon = nodes_coords[ref]
                            nom = tag.get('v')
                            if nom not in noms_existants:  # Vérifier si le nom n'existe pas déjà
                                batiments.append(Batiment(nom=nom, coordonneex=lat, coordonneey=lon))
                            break  # Trouvé, pas besoin de vérifier les autres <nd>
                        else:
                            print(f"Node avec ref {ref} non trouvé pour le way {parent.get('id')}")
                elif parent.tag == 'relation':
                    # Cas d'une relation avec des members de type 'way'
                    for member in parent.findall("./member[@type='way']"):
                        way_ref = int(member.get('ref'))
                        way = root.find(f"./way[@id='{way_ref}']")
                        if way is not None:
                            for nd in way.findall('./nd'):
                                ref = int(nd.get('ref'))
                                if ref in nodes_coords:
                                    lat, lon = nodes_coords[ref]
                                    nom = tag.get('v')
                                    if nom not in noms_existants:  # Vérifier si le nom n'existe pas déjà
                                        batiments.append(Batiment(nom=nom, coordonneex=lat, coordonneey=lon))
                                    break  # Trouvé, sortir de la boucle
                                else:
                                    print(f"Node avec ref {ref} non trouvé pour le way {way_ref} dans la relation {parent.get('id')}")
                            break  # Trouvé, pas besoin de vérifier d'autres members
                        else:
                            print(f"Way avec id {way_ref} non trouvé pour la relation {parent.get('id')}")
                    else:
                        print(f"Aucun way valide trouvé dans la relation {parent.get('id')}")

                if len(batiments) >= batch_size:
                    inserer_batiments(batiments)
                    # Mettre à jour les noms existants
                    noms_existants.update(b.nom for b in batiments)
                    batiments = []

    if batiments:
        inserer_batiments(batiments)


def inserer_batiments(batiments):
    """Insère un lot de bâtiments dans la base de données."""
    session = Session()
    try:
        session.bulk_save_objects(batiments)
        session.commit()
        print(f"Données insérées avec succès : {len(batiments)} bâtiments.")
    except IntegrityError as e:
        session.rollback()
        print(f"Erreur d'intégrité : {e}")
    finally:
        session.close()


# Exemple d'utilisation
# fichier_osm = 'static/js/map/map.osm'
# extraire_et_inserer_batiments(fichier_osm)

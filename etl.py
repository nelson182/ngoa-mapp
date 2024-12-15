import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

# Modèle de base pour SQLAlchemy
Base = declarative_base()

class Batiment(Base):
    __tablename__ = 'batiments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(255))
    coordonneex = Column(Float)
    coordonneey = Column(Float)
    type = Column(String(255), default="Inconnu")  # Valeur par défaut
    images = Column(String(255), default="/images/default.jpg")  # Chemin par défaut

# Configuration de la base de données
engine = create_engine('mysql+pymysql://root@localhost/ngoa')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def extraire_et_inserer_batiments(fichier_osm):
    # Parse le fichier OSM
    tree = ET.parse(fichier_osm)
    root = tree.getroot()

    # Compteur pour les insertions
    nombre_inseres = 0

    # Parcourir tous les nœuds
    for node in root.findall('node'):
        lat = node.attrib.get('lat')
        lon = node.attrib.get('lon')

        # Vérifier s'il y a un tag <tag> avec k="name"
        for tag in node.findall('tag'):
            if tag.attrib.get('k') == 'name':
                nom = tag.attrib.get('v')

                # Créer un objet Batiment et l'ajouter à la session
                batiment = Batiment(
                    nom=nom,
                    coordonneex=float(lat) if lat else None,
                    coordonneey=float(lon) if lon else None,
                )
                session.add(batiment)
                nombre_inseres += 1
                break  # Passer au nœud suivant une fois le nom trouvé

    # Enregistrer les modifications dans la base
    try:
        session.commit()
        print(f"Données insérées avec succès : {nombre_inseres} bâtiments.")
    except IntegrityError as e:
        session.rollback()
        print(f"Erreur d'intégrité : {e}")
    finally:
        session.close()

# Exemple d'utilisation
fichier_osm = 'js/map/map.osm'  # Remplacez par le chemin réel de votre fichier OSM
extraire_et_inserer_batiments(fichier_osm)

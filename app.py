from flask import Flask, jsonify, request, render_template
import osmnx as ox
from flask import Flask, redirect, url_for, session, render_template
import networkx as nx
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql
import os  
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask import Blueprint
from routes.auth import auth_bp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz
from routes import auth
from etl import Batiment
from sqlalchemy import create_engine
from flask import flash
from models import db, User,Evaluation
from __init__ import create_app, db
from routes.routes import setup_routes
from sqlalchemy import text
import logging
import pymysql
pymysql.install_as_MySQLdb()

# Charger les variables d'environnement
load_dotenv()
pymysql.install_as_MySQLdb()
# Configuration de l'application Flask
def create_app():
    app = Flask(__name__)

    # Configuration de la clé secrète
    app.secret_key = os.getenv('SECRET_KEY', 'votre_cle_secrete')  # Clé par défaut pour développement
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'QLkbNBDfWudjxFlceZdhilMyFDyVOvul')
    DB_HOST = os.getenv('DB_HOST', 'junction.proxy.rlwy.net')
    DB_PORT = os.getenv('DB_PORT', '29125')
    DB_NAME = os.getenv('DB_NAME', 'railway')

    # Construire l'URI de la base de données MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:QLkbNBDfWudjxFlceZdhilMyFDyVOvul@junction.proxy.rlwy.net:29125/railway'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialiser SQLAlchemy avec Flask
    db.init_app(app)

    # Charger les blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Charger le graphe depuis le fichier OSM
    osm_file = "static/js/map/map.osm"
    app.graph = ox.graph_from_xml(osm_file, simplify=True)

    # Retourner l'application Flask
    return app

# Créer la session SQLAlchemy
engine_users = create_engine(f'mysql://root:QLkbNBDfWudjxFlceZdhilMyFDyVOvul@junction.proxy.rlwy.net:29125/railway')
Session = sessionmaker(bind=engine_users)
db_session = Session()

# Initialisation globale
app = create_app()

# Créez les tables si elles n'existent pas
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')

        connection = db.engine.raw_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM utilisateurs WHERE email=%s", (email,))
                utilisateur = cursor.fetchone()

                if utilisateur and check_password_hash(utilisateur[3], mot_de_passe):
                    session['user_id'] = utilisateur[0]
                    session['nom'] = utilisateur[1]
                    session['email'] = utilisateur[2]
                    flash("Connexion réussie", "success")
                    return redirect(url_for('accueil'))
                elif utilisateur is None:
                    flash("Utilisateur non trouvé. Veuillez vous inscrire.", "info")
                    return redirect(url_for('register'))
                else:
                    flash("Identifiants incorrects. Réessayez.", "error")
        except Exception as e:
            flash(f"Erreur : {str(e)}", "error")
        finally:
            connection.close()

    return render_template('login.html')

# Route d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('name')
        email = request.form.get('email')
        mot_de_passe = request.form.get('password')
        age = request.form.get('age', type=int)
        hashed_password = generate_password_hash(mot_de_passe)

        connection = db.engine.raw_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO utilisateurs (nom, email, mot_de_passe, age)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nom, email, hashed_password, age)
                )
                connection.commit()

                flash("Inscription réussie. Connectez-vous maintenant.", "success")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Erreur : {str(e)}", "error")
        finally:
            connection.close()

    return render_template('register.html')

# Route de réinitialisation du mot de passe
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        try:
            user = db_session.execute(text("SELECT * FROM utilisateurs WHERE email=:email"), {"email": email}).mappings().first()

            if user:
                hashed_password = generate_password_hash(new_password)
                db_session.execute(
                    text("UPDATE utilisateurs SET mot_de_passe=:mot_de_passe WHERE email=:email"),
                    {"mot_de_passe": hashed_password, "email": email}
                )
                db_session.commit()
                flash('Mot de passe réinitialisé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Adresse email non trouvée. Veuillez vérifier et réessayer.', 'error')
        except Exception as e:
            flash(f"Erreur : {str(e)}", "error")

    return render_template('forgot_password.html')

@app.route('/batiment/<option>')
def batiment(option):
    # Recherche des bâtiments dont le nom commence par l'option sélectionnée (par exemple : 'Restaurants')
    batiments = Batiment.query.filter(Batiment.nom.like(f'{option}%')).all()

    # Suppression des doublons côté serveur (si nécessaire)
    unique_batiments = []
    seen = set()
    for batiment in batiments:
        if batiment.nom not in seen:
            unique_batiments.append(batiment)
            seen.add(batiment.nom)

    # Affichage des résultats dans une page HTML
    return render_template('batiment.html', batiments=unique_batiments, option=option)



# Route de la page d'accueil
@app.route('/accueil')
def accueil():
    if 'user_id' not in session:
        flash("Vous devez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))

    return render_template('accueil.html', nom=session['nom'])

# Route de déconnexion
@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('login'))

@app.before_request
def load_user_info():
    if 'user_id' in session:
        connection = engine_users.raw_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email, mot_de_passe FROM utilisateurs WHERE id=%s", (session['user_id'],))
                utilisateur = cursor.fetchone()
                if utilisateur:
                    session['email'] = utilisateur[0]
                    session['mot_de_passe'] = utilisateur[1]
        finally:
            connection.close()

# Route du compte utilisateur
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour accéder à votre compte.", "warning")
        return redirect(url_for('login'))

    result = db_session.execute(
        text("SELECT * FROM utilisateurs WHERE id=:id"), {"id": session['user_id']}
    )
    utilisateur = result.mappings().fetchone()

    if not utilisateur:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nouveau_nom = request.form.get('name', utilisateur['nom']).strip()
        nouveau_email = request.form.get('email', utilisateur['email']).strip()
        nouveau_age = request.form.get('age', utilisateur['age'])
        nouveau_mot_de_passe = request.form.get('password')

        if not nouveau_nom or not nouveau_email:
            flash("Le nom et l'email sont obligatoires.", "danger")
            return redirect(url_for('account'))

        hashed_password = (
            generate_password_hash(nouveau_mot_de_passe) if nouveau_mot_de_passe else utilisateur['mot_de_passe']
        )

        try:
            db_session.execute(
                text("""
                UPDATE utilisateurs SET nom=:nom, email=:email, mot_de_passe=:mot_de_passe, age=:age 
                WHERE id=:id
                """),
                {
                    "nom": nouveau_nom,
                    "email": nouveau_email,
                    "mot_de_passe": hashed_password,
                    "age": int(nouveau_age),
                    "id": session['user_id']
                }
            )
            db_session.commit()

            session['nom'] = nouveau_nom
            session['email'] = nouveau_email
            flash("Informations mises à jour avec succès.", "success")
        except Exception as e:
            flash(f"Erreur : {str(e)}", "error")

        return redirect(url_for('account'))

    return render_template(
        'account.html',
        nom=utilisateur['nom'],
        email=utilisateur['email'],
        age=utilisateur['age']
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/evaluer', methods=['GET', 'POST'])
def evaluer():
    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour soumettre une évaluation.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Récupération des données du formulaire
        try:
            note = int(request.form['rating'])
            commentaire = request.form['comment'].strip()

            # Validation de la note
            if note < 1 or note > 5:
                flash("La note doit être comprise entre 1 et 5.", "danger")
                return redirect(url_for('evaluer'))

            # ID de l'utilisateur connecté
            utilisateur_id = session['user_id']

            # Création d'une nouvelle évaluation
            nouvelle_evaluation = Evaluation(
                note=note,
                commentaire=commentaire,
                utilisateur_id=utilisateur_id
            )
            db.session.add(nouvelle_evaluation)
            db.session.commit()

            flash("Merci pour votre évaluation !", "success")
            return redirect(url_for('accueil'))
        except ValueError:
            flash("Veuillez entrer une note valide.", "danger")
            return redirect(url_for('evaluer'))

    return render_template('evaluate.html')

    
@app.route('/share', methods=['GET', 'POST'])
def share():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    share_link = None

    if request.method == 'POST':
        location = get_location(user_id)
        if location:
            # Création du lien de partage avec les informations récupérées
            share_link = f"https://your-app.com/location?user_id={user_id}&building={location['nom_batiment']}&room={location['nom_salle']}"

    return render_template('share.html', share_link=share_link)


def get_location(user_id):
    query = """
        SELECT bat.nom AS nom_batiment, salle.nom AS nom_salle
        FROM salles salle
        JOIN batiments bat ON salle.batiment_id = bat.id
        WHERE salle.user_id = :user_id
    """
    
    # Utilisation de db_session avec des paramètres nommés
    result = db_session.execute(text(query), {'user_id': user_id})
    location = result.fetchone()

    if location:
        return dict(location)
    return None

# Charger le graphe depuis le fichier OSM
osm_file = "static/js/map/map.osm"
graph = ox.graph_from_xml(osm_file, simplify=True)
def get_shortest_path(user_coords, destination_coords):
    """
    Calculer le plus court chemin entre deux points dans le graphe.
    """
    try:
        orig_node = ox.distance.nearest_nodes(graph, user_coords[1], user_coords[0])
        dest_node = ox.distance.nearest_nodes(graph, destination_coords[1], destination_coords[0])
        path = nx.shortest_path(graph, orig_node, dest_node, weight='length')
        return path
    except Exception as e:
        raise ValueError(f"Erreur lors du calcul du chemin : {str(e)}")
        
@app.route('/api/position', methods=['POST'])
def position():
    """
    Recevoir la position de l'utilisateur et vérifier si elle est dans le campus.
    """
    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    print(lat ,"", lon)
    # Vérifier si la position est dans les limites du campus
    campus_bounds = {
        "min_lat": 3.84747,
        "max_lat": 3.86849,
        "min_lon": 11.48706,
        "max_lon": 11.51457
    }

    if campus_bounds['min_lat'] <= lat <= campus_bounds['max_lat'] and campus_bounds['min_lon'] <= lon <= campus_bounds['max_lon']:
        return jsonify({"status": "success", "message": "Vous êtes dans le campus."})
    else:
        return jsonify({"status": "error", "message": "Vous n'êtes pas dans la zone du campus."})

@app.route('/api/amphis', methods=['GET'])
def obtenir_amphis():
    """
    Retourner des lieux contenant 'amphi' dans leur nom ou type.
    """
    try:
        query = "SELECT nom, description, coordonneex AS latitude , coordonneey AS longitude , images FROM batiments WHERE nom LIKE '%amphi%' OR type LIKE '%amphi%' LIMIT 5"
        connection = engine_users.raw_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            amphis = [
                {
                    "nom": row[0],
                    "description": row[1],
                    "latitude": row[2],
                    "longitude": row[3],
                    "images": row[4].split(',')  # Les images sont séparées par des virgules
                    
                }
                for row in result
            ]
            return jsonify({"status": "success", "data": amphis}), 200
    except Exception as e:
        # Log the erreur pour débogage
        print(f"Erreur dans /api/amphis : {e}")
        return jsonify({"status": "error", "message": "Une erreur est survenue lors de la récupération des amphithéâtres."}), 500

@app.route('/api/recherche', methods=['POST'])
def recherche():
    """
    Rechercher un lieu par nom dans la base de données avec fuzzywuzzy et retourner tous les résultats correspondants.
    """
    data = request.json
    nom_recherche = data.get('nom')

    # Requête SQL pour récupérer tous les noms et autres informations des lieux dans les tables 'batiments' et 'salles'
    query = """
    SELECT 
        batiments.nom AS nom_batiment, 
        batiments.coordonneex AS latitude, 
        batiments.coordonneey AS longitude, 
        batiments.description, 
        batiments.images 
    FROM batiments
    UNION
    SELECT 
        salles.nom AS nom_salle, 
        salles.coordonneex AS latitude, 
        salles.coordonneey AS longitude, 
        salles.description, 
        salles.images 
    FROM salles
    """
    
    connection = engine_users.raw_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)  # Récupérer tous les lieux de 'batiments' et 'salles'
            results = cursor.fetchall()  # Récupérer tous les résultats

            # Utiliser fuzzywuzzy pour rechercher les lieux correspondant au terme de recherche
            matches = []
            for result in results:
                nom, latitude, longitude, description, images = result
                # Calculer la similarité avec fuzzywuzzy (comparaison entre nom recherché et nom de chaque lieu)
                similarity = fuzz.ratio(nom_recherche.lower(), nom.lower())
                
                if similarity >=65:  # Seulement les résultats ayant un score de similarité supérieur à 65
                    matches.append({
                        "nom": nom,
                        "latitude": latitude,
                        "longitude": longitude,
                        "description": description,
                        "images": images.split(',')  # Les images sont séparées par des virgules
                    })
            print(matches)
            if matches:
                return jsonify({
                    "status": "success",
                    "data": matches
                })
            else:
                return jsonify({"status": "error", "message": "Aucun lieu trouvé."})

    finally:
        connection.close()


@app.route('/api/itineraire', methods=['POST'])
def itineraire():
    """
    Calculer l'itinéraire entre l'utilisateur et un lieu.
    """
    campus_bounds = {
        "min_lat": 3.84747,
        "max_lat": 3.86849,
        "min_lon": 11.48706,
        "max_lon": 11.51457
    }
    data = request.json
    user_coords = data.get('user_coords')  # [latitude, longitude]
    destination_coords = data.get('destination_coords')  # [latitude, longitude]
    if campus_bounds['min_lat'] <= user_coords[0] <= campus_bounds['max_lat'] and campus_bounds['min_lon'] <= user_coords[1] <= campus_bounds['max_lon']:
        try:
            path = get_shortest_path(user_coords, destination_coords)
            path_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]
            return jsonify({"status": "success", "path": path_coords})
        except Exception as e:
            
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "Vous n'êtes pas dans la zone du campus."})
# if __name__ == '__main__':
#     app.run(host='0.0.0.0' , port=5000, debug=True)

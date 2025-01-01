from flask import Blueprint, render_template, request, redirect, url_for, session
from etl import Salle, Batiment  # Remplacez par vos classes de modèle
from __init__ import db  # Assurez-vous d'importer correctement votre instance de la base de données

share = Blueprint('share', __name__, template_folder='templates')

@share.route('/share', methods=['GET', 'POST'])
def share():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    share_link = None

    if request.method == 'POST':
        if 'generate' in request.form:
            # Générer un lien de partage
            share_link = f"https://your-app.com/location/{user_id}"  # Exemple d'URL de partage

    # Récupération des informations de la position du lieu
    # Ici, nous allons supposer que 'Salle' et 'Batiment' sont les tables pertinentes
    # Vous devez adapter les jointures et les filtres selon votre modèle de données
    location = db.session.query(Salle.nom, Salle.coordonneex, Salle.coordonneey, Batiment.nom, Batiment.coordonneex, Batiment.coordonneey) \
                         .join(Batiment, Salle.batiment_id == Batiment.id) \
                         .filter(Salle.user_id == user_id) \
                         .first()

    return render_template('share.html', share_link=share_link)



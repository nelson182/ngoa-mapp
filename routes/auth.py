from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from __init__ import create_app, db

auth_bp = Blueprint('auth', __name__)  # Création du Blueprint pour les routes d'authentification

# Route de connexion
@auth_bp.route('/login', methods=['GET', 'POST'])
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
@auth_bp.route('/register', methods=['GET', 'POST'])
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

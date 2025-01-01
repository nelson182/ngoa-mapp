from flask import request, redirect, url_for, render_template
from models import User, db
from werkzeug.security import generate_password_hash


def setup_routes(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            nom = request.form['nom']
            email = request.form['email']
            mot_de_passe = request.form['mot_de_passe']
            age = request.form['age']

            utilisateur = User(nom=nom, email=email, age=int(age))
            utilisateur.mot_de_passe = generate_password_hash(mot_de_passe)

            db.session.add(utilisateur)
            db.session.commit()

            return redirect(url_for('home'))

        return render_template('register.html')

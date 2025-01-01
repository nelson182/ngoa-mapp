from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash
from models import User  # Remplacez myapp par le nom de votre application
from __init__ import db  # Assurez-vous que db est bien configuré pour votre application Flask avec SQLAlchemy

account = Blueprint('account', __name__)

@account.route('/account', methods=['GET', 'POST'])
def account_view():
    if 'email' not in session:
        return redirect(url_for('auth.login'))  # Rediriger si l'utilisateur n'est pas connecté

    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        mot_de_passe = generate_password_hash(request.form.get('mot_de_passe'))
        age = request.form.get('age')

        # Mise à jour des informations de l'utilisateur
        user = User.query.filter_by(email=session['email']).first()
        if user:
            user.nom = nom
            user.email = email
            user.mot_de_passe = mot_de_passe
            user.age = age
            db.session.commit()
            flash('Informations mises à jour avec succès!')
        return redirect(url_for('account.account_view'))

    # Récupération des informations de l'utilisateur
    user = User.query.filter_by(email=session['email']).first()
    if user:
        return render_template('account.html', nom=user.nom, email=user.email, mot_de_passe=user.mot_de_passe, age=user.age)
    else:
        flash('Utilisateur non trouvé.')
        return redirect(url_for('auth.login'))

@account.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Evaluation

# Créer un Blueprint pour les évaluations
evaluate_bp = Blueprint('evaluate', __name__, template_folder='../templates')

@evaluate_bp.route('/evaluer', methods=['GET', 'POST'])
def evaluer():
    """
    Route pour permettre à un utilisateur connecté de soumettre une évaluation.
    """
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour évaluer l'application.", "error")
        return redirect(url_for('auth.login'))  # Redirige vers la page de connexion

    if request.method == 'POST':
        commentaire = request.form.get('commentaire')
        note = int(request.form.get('note'))
        user_id = session['user_id']

        # Validation de la note
        if note < 1 or note > 5:
            flash("La note doit être comprise entre 1 et 5 étoiles.", "error")
            return redirect(url_for('evaluate.evaluer'))

        try:
            # Ajouter une nouvelle évaluation
            nouvelle_evaluation = Evaluation(user_id=user_id, commentaire=commentaire, note=note)
            db.session.add(nouvelle_evaluation)
            db.session.commit()
            flash("Merci pour votre évaluation !", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement : {str(e)}", "error")

        return redirect(url_for('home.accueil'))  # Redirige vers la page d'accueil

    return render_template('evaluate.html')


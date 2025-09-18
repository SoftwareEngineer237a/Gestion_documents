from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

# ----- INSCRIPTION -----
@auth_bp.route("/register", methods=["GET", "POST"])
@login_required  # Ajoutez cette ligne pour restreindre l'accès aux utilisateurs connectés
def register():
    # Vérifiez que seul l'admin peut créer des comptes
    if not current_user.is_admin():
        flash("Accès refusé. Seuls les administrateurs peuvent créer des comptes.", "danger")
        return redirect(url_for('admin.dashboard'))
    
    if request.method == "POST":
        prenom = request.form.get("prenom")
        nom = request.form.get("nom")
        mail = request.form.get("mail")
        password = request.form.get("password")
        role = request.form.get("role")

        if User.query.filter_by(mail=mail).first():
            flash("Un compte avec cet email existe déjà.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(prenom=prenom, nom=nom, mail=mail, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Compte créé avec succès !", "success")
        return redirect(url_for("admin.manage_users"))  # Rediriger vers la gestion des utilisateurs

    return render_template("auth/register.html")


# ----- CONNEXION -----
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mail = request.form.get("mail")
        password = request.form.get("password")

        user = User.query.filter_by(mail=mail).first()

        if user and user.check_password(password):
            if user.est_actif:
                login_user(user)
                flash(f"Bienvenue {user.prenom} !", "success")

                # Redirection selon le rôle
                if user.is_admin():
                    return redirect(url_for("admin.dashboard"))
                elif user.is_manager():
                    return redirect(url_for("manager.dashboard"))
                elif user.is_security():
                    return redirect(url_for("security.dashboard"))
                else:
                    return redirect(url_for("employee.dashboard"))
            else:
                flash("Votre compte est désactivé. Contactez l’administrateur.", "danger")
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template("auth/login.html")


# ----- DECONNEXION -----
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous êtes maintenant déconnecté.", "info")
    return redirect(url_for("auth.login"))

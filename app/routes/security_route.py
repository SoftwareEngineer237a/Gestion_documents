from flask import Blueprint, render_template

security_bp = Blueprint("security", __name__, template_folder="../templates/security")

@security_bp.route("/dashboard")
def dashboard():
    return "<h1>Dashboard Sécurité</h1><p>Bienvenue sur le tableau de bord sécurité.</p>"

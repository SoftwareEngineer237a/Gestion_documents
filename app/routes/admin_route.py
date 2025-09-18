from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")

@admin_bp.route("/dashboard")
def dashboard():
    return "<h1>Dashboard Admin</h1><p>Bienvenue sur le tableau de bord administrateur.</p>"

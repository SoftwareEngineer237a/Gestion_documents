from flask import Blueprint, render_template

manager_bp = Blueprint("manager", __name__, template_folder="../templates/manager")

@manager_bp.route("/dashboard")
def dashboard():
    return "<h1>Dashboard Manager</h1><p>Bienvenue sur le tableau de bord manager.</p>"

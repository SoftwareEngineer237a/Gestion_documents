from flask import Blueprint, render_template

employee_bp = Blueprint("employee", __name__, template_folder="../templates/employee")

@employee_bp.route("/dashboard")
def dashboard():
    return "<h1>Dashboard Employé</h1><p>Bienvenue sur le tableau de bord employé.</p>"

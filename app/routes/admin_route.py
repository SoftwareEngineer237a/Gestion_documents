from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.document import Document
from app.models.droit_acces import DroitAcces
from app.models.journal_activite import JournalActivite
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin():
        return "Accès refusé", 403
    return render_template("admin/dashboard.html", user=current_user)

@admin_bp.route("/manage_users")
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("Accès refusé. Seuls les administrateurs peuvent accéder à cette page.", "danger")
        return redirect(url_for('admin.dashboard'))
    
    # Récupérer tous les utilisateurs
    users = User.query.order_by(User.date_creation.desc()).all()
    return render_template("admin/manage_users.html", users=users)

@admin_bp.route("/toggle_user_status/<int:user_id>", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Empêcher de désactiver son propre compte
    if user.id == current_user.id:
        return jsonify({"success": False, "message": "Vous ne pouvez pas modifier votre propre statut"}), 400
    
    user.est_actif = not user.est_actif
    db.session.commit()
    
    action = "activé" if user.est_actif else "désactivé"
    return jsonify({"success": True, "message": f"Utilisateur {action} avec succès", "is_active": user.est_actif})

@admin_bp.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Empêcher de supprimer son propre compte
    if user.id == current_user.id:
        return jsonify({"success": False, "message": "Vous ne pouvez pas supprimer votre propre compte"}), 400
    
    # Vérifier s'il y a des données associées avant suppression
    # (À adapter selon vos besoins de suppression en cascade)
    has_documents = user.documents.count() > 0
    has_related_data = has_documents  # Ajouter d'autres vérifications si nécessaire
    
    if has_related_data:
        return jsonify({
            "success": False, 
            "message": "Impossible de supprimer cet utilisateur car il a des données associées. Désactivez-le plutôt."
        }), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Utilisateur supprimé avec succès"})

@admin_bp.route("/manage_permissions")
@login_required
def manage_permissions():
    if not current_user.is_admin():
        flash("Accès refusé. Seuls les administrateurs peuvent accéder à cette page.", "danger")
        return redirect(url_for('admin.dashboard'))
    
    # Récupérer tous les utilisateurs et documents
    users = User.query.order_by(User.nom, User.prenom).all()
    documents = Document.query.order_by(Document.titre).all()
    
    # Récupérer les droits existants pour pré-remplir le formulaire
    existing_permissions = {}
    for doc in documents:
        for droit in doc.droits_acces:
            key = f"{droit.iduser}_{droit.iddoc}"
            if key not in existing_permissions:
                existing_permissions[key] = []
            existing_permissions[key].append(droit.typedroit)
    
    return render_template("admin/droit_acces.html", 
                         users=users, 
                         documents=documents,
                         existing_permissions=existing_permissions)

@admin_bp.route("/update_permissions", methods=["POST"])
@login_required
def update_permissions():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        doc_id = data.get('doc_id')
        permission_type = data.get('permission_type')
        action = data.get('action')  # 'add' or 'remove'
        
        # Validation des données
        if not all([user_id, doc_id, permission_type, action]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        user = User.query.get(user_id)
        document = Document.query.get(doc_id)
        
        if not user or not document:
            return jsonify({"success": False, "message": "Utilisateur ou document non trouvé"}), 404
        
        # Vérifier si le droit existe déjà
        existing_right = DroitAcces.query.filter_by(
            iduser=user_id, 
            iddoc=doc_id, 
            typedroit=permission_type
        ).first()
        
        if action == 'add':
            if existing_right:
                return jsonify({"success": False, "message": "Ce droit existe déjà"}), 400
            
            # Créer un nouveau droit
            new_right = DroitAcces(
                typedroit=permission_type,
                iduser=user_id,
                iddoc=doc_id
            )
            db.session.add(new_right)
            message = f"Droit {permission_type} ajouté pour {user.nom_complet()} sur le document {document.titre}"
            
        else:  # action == 'remove'
            if not existing_right:
                return jsonify({"success": False, "message": "Ce droit n'existe pas"}), 400
            
            db.session.delete(existing_right)
            message = f"Droit {permission_type} retiré pour {user.nom_complet()} sur le document {document.titre}"
        
        db.session.commit()
        return jsonify({"success": True, "message": message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erreur: {str(e)}"}), 500

@admin_bp.route("/get_document_permissions/<int:doc_id>")
@login_required
def get_document_permissions(doc_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    document = Document.query.get_or_404(doc_id)
    
    # Récupérer tous les droits pour ce document
    permissions = []
    for droit in document.droits_acces:
        user = User.query.get(droit.iduser)
        permissions.append({
            'user_id': droit.iduser,
            'user_name': user.nom_complet(),
            'permission_type': droit.typedroit,
            'date_attribution': droit.date_attribution.strftime('%d/%m/%Y %H:%M')
        })
    
    return jsonify({"success": True, "permissions": permissions})

@admin_bp.route("/view_logs")
@login_required
def view_logs():
    if not current_user.is_admin():
        flash("Accès refusé. Seuls les administrateurs peuvent accéder à cette page.", "danger")
        return redirect(url_for('admin.dashboard'))
    
    # Récupérer les filtres par défaut (30 derniers jours)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Récupérer les logs avec les informations utilisateur et document
    logs = JournalActivite.query \
        .join(User, JournalActivite.iduser == User.id) \
        .outerjoin(Document, JournalActivite.iddoc == Document.id) \
        .add_columns(
            JournalActivite.id,
            JournalActivite.action,
            JournalActivite.dateaction,
            JournalActivite.details,
            User.nom,
            User.prenom,
            User.role,
            Document.titre
        ) \
        .filter(JournalActivite.dateaction.between(start_date, end_date)) \
        .order_by(JournalActivite.dateaction.desc()) \
        .all()
    
    # Compter les actions par type pour les statistiques
    action_stats = db.session.query(
        JournalActivite.action,
        db.func.count(JournalActivite.id)
    ).filter(JournalActivite.dateaction.between(start_date, end_date)) \
     .group_by(JournalActivite.action).all()
    
    # Récupérer tous les utilisateurs pour le filtre
    users = User.query.order_by(User.nom, User.prenom).all()
    
    # Types d'actions disponibles
    action_types = ['connexion', 'telechargement', 'modification', 
                   'suppression', 'partage', 'validation', 'creation', 'consultation']
    
    return render_template("admin/journeaux_log.html", 
                         logs=logs, 
                         users=users,
                         action_types=action_types,
                         action_stats=action_stats,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@admin_bp.route("/filter_logs", methods=["POST"])
@login_required
def filter_logs():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    try:
        data = request.get_json()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        user_id = data.get('user_id')
        action_type = data.get('action_type')
        
        # Convertir les dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # Construire la requête de base
        query = JournalActivite.query \
            .join(User, JournalActivite.iduser == User.id) \
            .outerjoin(Document, JournalActivite.iddoc == Document.id) \
            .add_columns(
                JournalActivite.id,
                JournalActivite.action,
                JournalActivite.dateaction,
                JournalActivite.details,
                User.nom,
                User.prenom,
                User.role,
                Document.titre
            )
        
        # Appliquer les filtres
        if start_date and end_date:
            # Ajouter un jour à end_date pour inclure toute la journée
            end_date = end_date + timedelta(days=1)
            query = query.filter(JournalActivite.dateaction.between(start_date, end_date))
        
        if user_id and user_id != 'all':
            query = query.filter(JournalActivite.iduser == user_id)
        
        if action_type and action_type != 'all':
            query = query.filter(JournalActivite.action == action_type)
        
        # Exécuter la requête
        logs = query.order_by(JournalActivite.dateaction.desc()).all()
        
        # Formater les résultats pour JSON
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'action': log.action,
                'dateaction': log.dateaction.strftime('%d/%m/%Y %H:%M:%S'),
                'details': log.details,
                'user_nom': log.nom,
                'user_prenom': log.prenom,
                'user_role': log.role,
                'document_titre': log.titre if log.titre else 'N/A'
            })
        
        return jsonify({"success": True, "logs": logs_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur: {str(e)}"}), 500

@admin_bp.route("/export_logs", methods=["POST"])
@login_required
def export_logs():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Accès refusé"}), 403
    
    try:
        data = request.get_json()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        export_format = data.get('format', 'csv')
        
        # Convertir les dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # Construire la requête
        query = JournalActivite.query \
            .join(User, JournalActivite.iduser == User.id) \
            .outerjoin(Document, JournalActivite.iddoc == Document.id) \
            .add_columns(
                JournalActivite.action,
                JournalActivite.dateaction,
                JournalActivite.details,
                User.nom,
                User.prenom,
                User.role,
                Document.titre
            )
        
        # Appliquer les filtres de date
        if start_date and end_date:
            end_date = end_date + timedelta(days=1)
            query = query.filter(JournalActivite.dateaction.between(start_date, end_date))
        
        logs = query.order_by(JournalActivite.dateaction.desc()).all()
        
        # Générer le contenu CSV
        if export_format == 'csv':
            csv_content = "Date;Heure;Action;Utilisateur;Rôle;Document;Détails\n"
            for log in logs:
                date_str = log.dateaction.strftime('%d/%m/%Y')
                time_str = log.dateaction.strftime('%H:%M:%S')
                user_str = f"{log.prenom} {log.nom}"
                document_str = log.titre if log.titre else "N/A"
                details_str = log.details.replace(';', ',') if log.details else ""
                
                csv_content += f"{date_str};{time_str};{log.action};{user_str};{log.role};{document_str};{details_str}\n"
            
            return jsonify({
                "success": True, 
                "content": csv_content, 
                "filename": f"journaux_activite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            })
        
        return jsonify({"success": False, "message": "Format non supporté"}), 400
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur: {str(e)}"}), 500
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(64), nullable=False)
    prenom = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # employee, manager, security, admin
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    est_actif = db.Column(db.Boolean, default=True)
    
    # Relations
    documents = db.relationship('Document', backref='user', lazy='dynamic')
    droits_acces = db.relationship('DroitAcces', backref='user', lazy='dynamic')
    journaux = db.relationship('JournalActivite', backref='user', lazy='dynamic')
    validations = db.relationship('Validation', backref='user', lazy='dynamic')
    rapports = db.relationship('Rapport', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_employee(self):
        return self.role == 'employee'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_security(self):
        return self.role == 'security'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
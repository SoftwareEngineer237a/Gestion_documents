from app import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=True)
    typedoc = db.Column(db.String(50), nullable=False)  # Type de document
    datedepot = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='brouillon')  # brouillon, en attente, validé, rejeté, archivé
    iduser = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    droits_acces = db.relationship('DroitAcces', backref='document', lazy='dynamic')
    journaux = db.relationship('JournalActivite', backref='document', lazy='dynamic')
    validations = db.relationship('Validation', backref='document', lazy='dynamic')
from app import db
from datetime import datetime

class JournalActivite(db.Model):
    __tablename__ = 'journaux_activite'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)  # connexion, telechargement, modification, suppression, partage, validation
    dateaction = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)
    iduser = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    iddoc = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)  # Peut être null pour certaines actions (ex: connexion)
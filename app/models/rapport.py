from app import db
from datetime import datetime

class Rapport(db.Model):
    __tablename__ = 'rapports'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    dategeneration = db.Column(db.DateTime, default=datetime.utcnow)
    idmanager = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
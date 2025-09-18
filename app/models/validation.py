from app import db
from datetime import datetime

class Validation(db.Model):
    __tablename__ = 'validations'
    
    id = db.Column(db.Integer, primary_key=True)
    iddoc = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    idmanager = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    decision = db.Column(db.String(20), nullable=False)  # validé, rejeté
    commentaire = db.Column(db.Text, nullable=True)
    datevalidation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contrainte d'unicité pour éviter les validations multiples d'un même document par le même manager
    __table_args__ = (
        db.UniqueConstraint('iddoc', 'idmanager', name='unique_validation_doc_manager'),
    )
from app import db

class DroitAcces(db.Model):
    __tablename__ = 'droits_acces'
    
    id = db.Column(db.Integer, primary_key=True)
    typedroit = db.Column(db.String(20), nullable=False)  # lecture, ecriture, partage, suppression, validation, modification
    iduser = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    iddoc = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    date_attribution = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Contrainte d'unicité pour éviter les doublons de droits
    __table_args__ = (
        db.UniqueConstraint('iduser', 'iddoc', 'typedroit', name='unique_droit_user_doc'),
    )
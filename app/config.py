import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "12345678"
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/document_manager"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

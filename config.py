import os
import cloudinary


# ==========================
# CLOUDINARY
# ==========================

cloudinary.config(
    cloud_url=os.environ.get("CLOUDINARY_URL")
)


# ==========================
# CONFIGURATION FLASK
# ==========================

class Config:

    # Clé secrète Flask
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # Base de données Supabase PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+pg8000://postgres.mctfgwglsiwtogiwjxio:"
        "n6em*QhKz8RSAHD"
        "@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"
    )


    # Désactive les notifications SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Taille maximale des fichiers uploadés (100 Mo)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

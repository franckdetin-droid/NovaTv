import os
import cloudinary

# Configuration Cloudinary (sécurisée avec variables d'environnement)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)


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

    # Désactive les notifications inutiles de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Taille maximale des fichiers (100 Mo)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

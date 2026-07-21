import os


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


    # Vérification connexion avant utilisation
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10
    }


    # Désactive les notifications SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Upload
    UPLOAD_FOLDER = "storage"


    # Taille maximale upload 5 Go
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024


    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    )

    CLOUDINARY_API_KEY = os.environ.get(
        "CLOUDINARY_API_KEY"
    )

    CLOUDINARY_API_SECRET = os.environ.get(
        "CLOUDINARY_API_SECRET"
    )

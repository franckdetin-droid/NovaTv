import os


class Config:

    # ==========================
    # FLASK
    # ==========================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # ==========================
    # DATABASE SUPABASE
    # ==========================

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres.mctfgwglsiwtogiwjxio:"
        "n6em*QhKz8RSAHD"
        "@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"
    )


    SQLALCHEMY_ENGINE_OPTIONS = {

        # Vérifie que la connexion existe encore
        "pool_pre_ping": True,

        # Renouvelle les connexions régulièrement
        "pool_recycle": 280,

        # Nombre de connexions gardées
        "pool_size": 5,

        # Connexions supplémentaires possibles
        "max_overflow": 10

    }


    SQLALCHEMY_TRACK_MODIFICATIONS = False



    # ==========================
    # UPLOAD
    # ==========================

    UPLOAD_FOLDER = "storage"


    # Taille maximale fichier : 5 Go

    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024 * 1024
    )



    # ==========================
    # CLOUDINARY
    # ==========================

    CLOUDINARY_CLOUD_NAME = os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    )


    CLOUDINARY_API_KEY = os.environ.get(
        "CLOUDINARY_API_KEY"
    )


    CLOUDINARY_API_SECRET = os.environ.get(
        "CLOUDINARY_API_SECRET"
    )



    # ==========================
    # SESSION
    # ==========================

    SESSION_COOKIE_SECURE = True

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

import os


class Config:

    # ==========================
    # FLASK SECRET KEY
    # ==========================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # ==========================
    # DATABASE SUPABASE POSTGRES
    # ==========================

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres.iokvvjkgehewlszzkcvb:"
        "franckdetin2012"
        "@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
        "?pgbouncer=true"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Reconnexion automatique si Supabase coupe la connexion

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10
    }


    # ==========================
    # STOCKAGE FICHIERS
    # ==========================

    UPLOAD_FOLDER = "storage"


    # Taille maximale upload : 5 Go

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

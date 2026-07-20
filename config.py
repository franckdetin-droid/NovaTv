import os


class Config:

    # Clé secrète Flask
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # Base de données Supabase PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres.mctfgwglsiwtogiwjxio:"
        "n6em*QhKz8RSAHD"
        "@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"
    )


    # Désactive les notifications inutiles de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False



    # Taille maximale des fichiers (100 Mo)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024



    # ==========================
    # CLOUDINARY
    # ==========================

    CLOUDINARY_CLOUD_NAME = os.environ.get(
        "CLOUDINARY_CLOUD_NAME",
        "nf8uv7f4"
    )


    CLOUDINARY_API_KEY = os.environ.get(
        "CLOUDINARY_API_KEY",
        "921943687156619"
    )


    CLOUDINARY_API_SECRET = os.environ.get(
        "CLOUDINARY_API_SECRET",
        ""
    )

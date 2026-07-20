import os


class Config:

    # Clé secrète Flask
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # Base de données Supabase PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    )


    # Désactive les notifications SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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


    # Taille maximale fichiers
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

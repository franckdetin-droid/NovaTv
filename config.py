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

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+pg8000://postgres.mctfgwglsiwtogiwjxio:"
        "n6em*QhKz8RSAHD"
        "@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False



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
    # LIMITE UPLOAD
    # ==========================

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

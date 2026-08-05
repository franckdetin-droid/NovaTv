import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-moi-cette-cle-secrete"
    )


    # Base PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10
    }


    # Google Drive Storage

    GOOGLE_DRIVE_FOLDER_ID = os.environ.get(
        "GOOGLE_DRIVE_FOLDER_ID"
    )

    GOOGLE_CREDENTIALS = os.environ.get(
        "GOOGLE_CREDENTIALS",
        "credentials.json"
    )


    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024 * 1024
    )

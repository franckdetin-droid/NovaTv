import os

from flask import Flask
from flask_socketio import SocketIO

from database import db
from config import Config
from routes import main



# ==========================
# CREATION APPLICATION
# ==========================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


app.config.from_object(
    Config
)
# ==========================
# CLOUDINARY
# ==========================

import cloudinary


cloudinary.config(
    cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
    api_key=app.config["CLOUDINARY_API_KEY"],
    api_secret=app.config["CLOUDINARY_API_SECRET"]
)



# ==========================
# SOCKET IO
# ==========================

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)



# ==========================
# DATABASE
# ==========================

db.init_app(app)



# ==========================
# MODELES
# ==========================

from models import *



# ==========================
# ROUTES
# ==========================

app.register_blueprint(
    main
)



# ==========================
# BASE DE DONNEES
# ==========================

with app.app_context():

    db.create_all()



# ==========================
# SOCKET EVENTS
# ==========================

from socket_events import socket_events


socket_events(
    socketio
)



# ==========================
# DEMARRAGE
# ==========================

if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=False
    )

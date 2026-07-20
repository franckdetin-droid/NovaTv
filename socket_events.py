from flask_socketio import emit, join_room, leave_room
from flask import request

def socket_events(socketio):


    # ==========================
    # CONNEXION
    # ==========================

    @socketio.on("connect")
    def connect():

        print("✅ Utilisateur connecté")



    # ==========================
    # DECONNEXION
    # ==========================

    @socketio.on("disconnect")
    def disconnect():

        print("❌ Utilisateur déconnecté")



    # ==========================
    # REJOINDRE LIVE CAMERA
    # ==========================

    @socketio.on("join_camera")
    def join_camera(data):

        room = data["room"]

        join_room(room)

        print(
            "📡 Salle caméra :",
            room
        )
        emit(
    "viewer_joined",
    {
        "room": room,
        "viewer_id": request.sid
    },
    room=room,
    include_self=False
        )


        



    # ==========================
    # OFFRE DU CREATEUR
    # ==========================

    @socketio.on("camera_offer")
    def camera_offer(data):

        room = data["room"]


        emit(
            "camera_offer",
            {
                "offer": data["offer"]
            },
            room=room,
            include_self=False
        )



    # ==========================
    # REPONSE DU SPECTATEUR
    # ==========================

    @socketio.on("camera_offer")
def camera_offer(data):

    emit(
        "camera_offer",
        {
            "offer": data["offer"],
            "sender": request.sid
        },
        room=data["room"],
        include_self=False
        )


    # ==========================
    # ICE CREATEUR / SPECTATEUR
    # ==========================

    @socketio.on("camera_ice")
    def camera_ice(data):

        room = data["room"]


        emit(
            "camera_ice",
            {
                "candidate": data["candidate"]
            },
            room=room,
            include_self=False
        )



    # ==========================
    # ARRET LIVE CAMERA
    # ==========================

    @socketio.on("stop_camera")
    def stop_camera(data):

        room = data["room"]


        emit(
            "camera_stopped",
            {},
            room=room
        )


        print(
            "⛔ Live arrêté :",
            room
        )



    # ==========================
    # QUITTER SALLE
    # ==========================

    @socketio.on("leave_camera")
    def leave_camera(data):

        room = data["room"]

        leave_room(room)

        print(
            "Sortie salle :",
            room
        )

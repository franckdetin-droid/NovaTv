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
    # REJOINDRE SALLE CAMERA
    # ==========================

    @socketio.on("join_camera")
    def join_camera(data):

        room = data["room"]

        join_room(room)

        print(
            "📡 Salle caméra :",
            room
        )


        # prévenir le créateur qu'un spectateur arrive

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
    # REPONSE DU SPECTATEUR
    # ==========================

    @socketio.on("camera_answer")
    def camera_answer(data):

        emit(
            "camera_answer",
            {
                "answer": data["answer"],
                "sender": request.sid
            },
            room=data["room"],
            include_self=False
        )



    # ==========================
    # ICE WEBRTC
    # ==========================

    @socketio.on("camera_ice")
    def camera_ice(data):

        emit(
            "camera_ice",
            {
                "candidate": data["candidate"],
                "sender": request.sid
            },
            room=data["room"],
            include_self=False
        )



    # ==========================
    # ARRET LIVE
    # ==========================

    @socketio.on("stop_camera")
    def stop_camera(data):

        emit(
            "camera_stopped",
            {},
            room=data["room"]
        )


        print(
            "⛔ Live caméra arrêté :",
            data["room"]
        )



    # ==========================
    # QUITTER SALLE
    # ==========================

    @socketio.on("leave_camera")
    def leave_camera(data):

        leave_room(
            data["room"]
        )


        print(
            "👋 Sortie salle :",
            data["room"]
        )

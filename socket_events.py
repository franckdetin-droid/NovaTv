from flask_socketio import emit, join_room, leave_room
from flask import request

# 🔢 stocker nombre de viewers
rooms_users = {}


def socket_events(socketio):

    # ==========================
    # CONNEXION
    # ==========================
    @socketio.on("connect")
    def connect():
        print("✅ Utilisateur connecté :", request.sid)


    # ==========================
    # DECONNEXION
    # ==========================
    @socketio.on("disconnect")
    def disconnect():
        print("❌ Utilisateur déconnecté :", request.sid)


    # ==========================
    # REJOINDRE SALLE CAMERA
    # ==========================
    @socketio.on("join_camera")
    def join_camera(data):

        room = data.get("room")

        if not room:
            return

        # créer room si elle existe pas
        if room not in rooms_users:
            rooms_users[room] = 0

        # 🔥 limite viewers (20 max)
        if rooms_users[room] >= 20:
            emit("room_full")
            return

        rooms_users[room] += 1

        join_room(room)

        print(f"📡 {request.sid} rejoint {room} | total: {rooms_users[room]}")

        # prévenir les autres (créateur inclus)
        emit(
            "viewer_joined",
            {
                "room": room,
                "viewer_id": request.sid,
                "count": rooms_users[room]
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

        room = data.get("room")

        emit(
            "camera_stopped",
            {},
            room=room
        )

        print("⛔ Live arrêté :", room)


    # ==========================
    # QUITTER SALLE
    # ==========================
    @socketio.on("leave_camera")
    def leave_camera(data):

        room = data.get("room")

        leave_room(room)

        if room in rooms_users:
            rooms_users[room] -= 1

            if rooms_users[room] <= 0:
                del rooms_users[room]

        print(f"👋 {request.sid} quitte {room}")

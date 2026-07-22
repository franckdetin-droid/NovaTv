from flask_socketio import emit, join_room, leave_room
from flask import request


# ==========================
# STOCKAGE
# ==========================

live_creators = {}   # room -> creator sid
live_viewers = {}    # room -> [viewer sid]


def socket_events(socketio):

    # ==========================
    # CONNEXION
    # ==========================

    @socketio.on("connect")
    def connect():
        print("✅ Connecté :", request.sid)

    @socketio.on("disconnect")
    def disconnect():
        print("❌ Déconnecté :", request.sid)

        # retirer spectateur
        for room, viewers in list(live_viewers.items()):
            if request.sid in viewers:
                viewers.remove(request.sid)

        # retirer créateur
        for room, creator in list(live_creators.items()):
            if creator == request.sid:
                del live_creators[room]
                emit("camera_stopped", {}, room=room)

    # ==========================
    # JOIN CAMERA
    # ==========================

    @socketio.on("join_camera")
    def join_camera(data):

        room = data["room"]
        join_room(room)

        # ==========================
        # CREATEUR
        # ==========================
        if data.get("creator"):

            live_creators[room] = request.sid
            live_viewers[room] = []

            print("🎥 Créateur :", room, request.sid)

        # ==========================
        # SPECTATEUR
        # ==========================
        else:

            if room not in live_viewers:
                live_viewers[room] = []

            if len(live_viewers[room]) >= 100:
                emit("room_full", {"message": "Live complet"})
                return

            live_viewers[room].append(request.sid)

            print("👀 Spectateur :", request.sid, "->", room)

            # prévenir créateur
            creator_sid = live_creators.get(room)

            if creator_sid:
                emit(
                    "viewer_joined",
                    {
                        "viewer_id": request.sid
                    },
                    room=creator_sid
                )

    # ==========================
    # OFFER (CREATEUR -> VIEWER)
    # ==========================

    @socketio.on("camera_offer")
    def camera_offer(data):

        target = data.get("target")

        if target:
            emit(
                "camera_offer",
                {
                    "offer": data["offer"],
                    "sender": request.sid
                },
                room=target
            )

            print("📡 Offer envoyée ->", target)

    # ==========================
    # ANSWER (VIEWER -> CREATEUR)
    # ==========================

    @socketio.on("camera_answer")
    def camera_answer(data):

        target = data.get("target")

        if target:
            emit(
                "camera_answer",
                {
                    "answer": data["answer"],
                    "sender": request.sid
                },
                room=target
            )

            print("✅ Answer envoyée ->", target)

    # ==========================
    # ICE
    # ==========================

    @socketio.on("camera_ice")
    def camera_ice(data):

        target = data.get("target")

        if target:
            emit(
                "camera_ice",
                {
                    "candidate": data["candidate"],
                    "sender": request.sid
                },
                room=target
            )

    # ==========================
    # STOP LIVE
    # ==========================

    @socketio.on("stop_camera")
    def stop_camera(data):

        room = data["room"]

        emit("camera_stopped", {}, room=room)

        if room in live_creators:
            del live_creators[room]

        if room in live_viewers:
            del live_viewers[room]

        print("⛔ Live stoppé :", room)

    # ==========================
    # LEAVE
    # ==========================

    @socketio.on("leave_camera")
    def leave_camera(data):

        room = data["room"]
        leave_room(room)

        if room in live_viewers:
            if request.sid in live_viewers[room]:
                live_viewers[room].remove(request.sid)

        print("👋 Quitte :", request.sid)

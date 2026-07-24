from flask_socketio import emit, join_room, leave_room
from flask import request

# ==================================================
# APPEL VIDEO
# ==================================================

video_rooms = {}

# ==================================================
# LIVE MULTI PERSONNES
# ==================================================

live_rooms = {}

"""
Structure :

live_rooms = {

    "camera_live_1":{

        "creator":"SID123",

        "guests":{

            "SID456",

            "SID789"

        },

        "viewers":{

            "SID111",

            "SID222"

        }

    }

}
"""


def socket_events(socketio):

    # ============================================
    # CONNEXION
    # ============================================

    @socketio.on("connect")
    def connect():

        print(
            "🟢 Connecté :",
            request.sid
        )

    # ============================================
    # DECONNEXION
    # ============================================

    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid

        # ---------- APPEL VIDEO ----------

        for room in list(video_rooms.keys()):

            if sid in video_rooms[room]:

                video_rooms[room].remove(sid)

                emit(
                    "user_left",
                    {
                        "id": sid
                    },
                    room=room
                )

                if len(video_rooms[room]) == 0:

                    del video_rooms[room]

        # ---------- LIVE ----------

        for room in list(live_rooms.keys()):

            live = live_rooms[room]

            if live["creator"] == sid:

                emit(
                    "camera_stopped",
                    {},
                    room=room
                )

                del live_rooms[room]

                continue

            if sid in live["guests"]:

                live["guests"].remove(sid)

                emit(
                    "guest_left",
                    {
                        "id": sid
                    },
                    room=room
                )

            if sid in live["viewers"]:

                live["viewers"].remove(sid)

                emit(
                    "viewer_left",
                    {
                        "id": sid
                    },
                    room=live["creator"]
                )

        print(
            "🔴 Déconnecté :",
            sid
)
        # ==================================================
# REJOINDRE UN LIVE
# ==================================================

@socketio.on("join_camera")
def join_camera(data):

    room = data.get("room")
    creator = data.get("creator", False)

    if not room:
        return

    join_room(room)

    # Création de la salle
    if room not in live_rooms:

        live_rooms[room] = {

            "creator": None,

            "guests": set(),

            "viewers": set()

        }

    live = live_rooms[room]

    # -----------------------------
    # Créateur
    # -----------------------------

    if creator:

        live["creator"] = request.sid

        emit(
            "creator_ready",
            {},
            room=request.sid
        )

        print("🎥 Créateur :", room)

        return

    # -----------------------------
    # Spectateur
    # -----------------------------

    live["viewers"].add(request.sid)

    emit(
        "viewer_joined",
        {
            "viewer_id": request.sid,

            "count": len(live["viewers"])
        },
        room=live["creator"]
    )

    emit(
        "viewer_count",
        {
            "count": len(live["viewers"])
        },
        room=room
    )

    print(
        "👀 Spectateur :",
        request.sid
    )


# ==================================================
# DEMANDE DE REJOINDRE LE LIVE
# ==================================================

@socketio.on("request_join_live")
def request_join_live(data):

    room = data["room"]

    if room not in live_rooms:
        return

    creator = live_rooms[room]["creator"]

    emit(

        "join_request",

        {

            "guest": request.sid

        },

        room=creator

    )

    print(
        "✋ Demande invité :",
        request.sid
    )


# ==================================================
# LE CREATEUR ACCEPTE
# ==================================================

@socketio.on("accept_guest")
def accept_guest(data):

    room = data["room"]

    guest = data["guest"]

    if room not in live_rooms:
        return

    live_rooms[room]["guests"].add(guest)

    emit(

        "guest_accepted",

        {},

        room=guest

    )

    emit(

        "guest_joined",

        {

            "guest": guest

        },

        room=room

    )

    print(
        "✅ Invité accepté :",
        guest
                )
    # ==================================================
# WEBRTC OFFER
# ==================================================

@socketio.on("camera_offer")
def camera_offer(data):

    target = data.get("target")

    if not target:
        return

    emit(

        "camera_offer",

        {

            "offer": data["offer"],

            "sender": request.sid

        },

        room=target

    )


# ==================================================
# WEBRTC ANSWER
# ==================================================

@socketio.on("camera_answer")
def camera_answer(data):

    target = data.get("target")

    if not target:
        return

    emit(

        "camera_answer",

        {

            "answer": data["answer"],

            "sender": request.sid

        },

        room=target

    )


# ==================================================
# ICE CANDIDATE
# ==================================================

@socketio.on("camera_ice")
def camera_ice(data):

    target = data.get("target")

    if not target:
        return

    emit(

        "camera_ice",

        {

            "candidate": data["candidate"],

            "sender": request.sid

        },

        room=target

    )


# ==================================================
# CHAT DU LIVE
# ==================================================

@socketio.on("live_message")
def live_message(data):

    room = data.get("room")

    if not room:
        return

    emit(

        "live_message",

        {

            "user": request.sid[:6],

            "message": data["message"]

        },

        room=room

    )


# ==================================================
# REACTIONS ❤️ 😂 🔥 👍
# ==================================================

@socketio.on("live_reaction")
def live_reaction(data):

    room = data.get("room")

    if not room:
        return

    emit(

        "live_reaction",

        {

            "emoji": data["emoji"],

            "user": request.sid

        },

        room=room

    )


# ==================================================
# CREATEUR EXCLUT UN INVITE
# ==================================================

@socketio.on("kick_guest")
def kick_guest(data):

    room = data["room"]

    guest = data["guest"]

    if room not in live_rooms:
        return

    live_rooms[room]["guests"].discard(guest)

    emit(

        "kicked",

        {},

        room=guest

    )

    emit(

        "guest_left",

        {

            "id": guest

        },

        room=room

    )


# ==================================================
# ARRET DU LIVE
# ==================================================

@socketio.on("stop_camera")
def stop_camera(data):

    room = data.get("room")

    if not room:
        return

    emit(

        "camera_stopped",

        {},

        room=room

    )

    live_rooms.pop(room, None)

    print("⛔ Live arrêté :", room)

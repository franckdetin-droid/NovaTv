from flask_socketio import emit, join_room, leave_room
from app import socketio



# ==========================
# CONNEXION
# ==========================

@socketio.on("connect")
def connected():

    print("✅ Utilisateur connecté")



# ==========================
# REJOINDRE UN LIVE
# ==========================

@socketio.on("join_live")
def join_live(data):

    room = data.get("room")


    if room:

        join_room(room)


        emit(
            "live_joined",
            {
                "message":"Connecté au live"
            },
            room=room
        )



# ==========================
# DEMARRER LIVE CREATEUR
# ==========================

@socketio.on("start_live")
def start_live(data):

    room = data.get("room")


    emit(
        "live_started",
        data,
        room=room
    )



# ==========================
# OFFRE WEBRTC
# ==========================

@socketio.on("camera_offer")
def camera_offer(data):

    room = data.get("room")


    emit(
        "camera_offer",
        data,
        room=room,
        include_self=False
    )



# ==========================
# REPONSE WEBRTC
# ==========================

@socketio.on("camera_answer")
def camera_answer(data):

    room = data.get("room")


    emit(
        "camera_answer",
        data,
        room=room,
        include_self=False
    )



# ==========================
# ICE
# ==========================

@socketio.on("ice_candidate")
def ice_candidate(data):

    room = data.get("room")


    emit(
        "ice_candidate",
        data,
        room=room,
        include_self=False
    )



# ==========================
# STOP LIVE
# ==========================

@socketio.on("stop_live")
def stop_live(data):

    room = data.get("room")


    emit(
        "live_stopped",
        data,
        room=room
    )
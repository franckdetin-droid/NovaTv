from flask_socketio import emit, join_room, leave_room
from flask import request


# ==========================
# STOCKAGE LIVE CAMERA
# ==========================

live_creators = {}   # room -> creator sid
live_viewers = {}    # room -> liste des viewers sid



def socket_events(socketio):


    # ==========================
    # CONNEXION
    # ==========================

    @socketio.on("connect")
    def connect():

        print(
            "✅ Socket connecté :",
            request.sid
        )



    # ==========================
    # DECONNEXION
    # ==========================

    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid

        print(
            "❌ Socket déconnecté :",
            sid
        )


        # supprimer spectateur

        for room, viewers in list(live_viewers.items()):

            if sid in viewers:

                viewers.remove(sid)

                print(
                    "👋 Spectateur retiré :",
                    room
                )



        # supprimer créateur

        for room, creator in list(live_creators.items()):

            if creator == sid:


                del live_creators[room]


                emit(
                    "camera_stopped",
                    {},
                    room=room
                )


                print(
                    "⛔ Créateur retiré :",
                    room
                )



    # ==========================
    # REJOINDRE CAMERA
    # ==========================

    @socketio.on("join_camera")
    def join_camera(data):


        room = data.get("room")

        creator = data.get(
            "creator",
            False
        )


        if not room:

            print(
                "❌ Room manquante"
            )

            return



        join_room(room)



        # ==========================
        # CREATEUR
        # ==========================

        if creator:


            live_creators[room] = request.sid


            if room not in live_viewers:

                live_viewers[room] = []



            print(
                "🎥 Créateur connecté :",
                room,
                request.sid
            )



        # ==========================
        # SPECTATEUR
        # ==========================

        else:


            if room not in live_viewers:

                live_viewers[room] = []



            if len(live_viewers[room]) >= 100:


                emit(
                    "room_full",
                    {
                        "message":
                        "Live complet"
                    }
                )

                return



            live_viewers[room].append(
                request.sid
            )



            print(
                "👀 Spectateur :",
                request.sid,
                "->",
                room
            )



            creator_sid = live_creators.get(
                room
            )


            if creator_sid:


                emit(
                    "viewer_joined",
                    {
                        "viewer_id":
                        request.sid
                    },
                    room=creator_sid
                )


                print(
                    "📢 Notification envoyée au créateur"
                )

            else:

                print(
                    "⚠️ Aucun créateur trouvé pour",
                    room
                )



    # ==========================
    # OFFER WEBRTC
    # ==========================

    @socketio.on("camera_offer")
    def camera_offer(data):


        target = data.get(
            "target"
        )


        if target:


            emit(
                "camera_offer",
                {
                    "offer":
                    data.get("offer"),

                    "sender":
                    request.sid
                },
                room=target
            )


            print(
                "📡 Offer envoyée vers",
                target
            )



    # ==========================
    # ANSWER WEBRTC
    # ==========================

    @socketio.on("camera_answer")
    def camera_answer(data):


        target = data.get(
            "target"
        )


        if target:


            emit(
                "camera_answer",
                {
                    "answer":
                    data.get("answer"),

                    "sender":
                    request.sid
                },
                room=target
            )


            print(
                "✅ Answer envoyée vers",
                target
            )



    # ==========================
    # ICE CANDIDATE
    # ==========================

    @socketio.on("camera_ice")
    def camera_ice(data):


        target = data.get(
            "target"
        )


        if target:


            emit(
                "camera_ice",
                {
                    "candidate":
                    data.get("candidate"),

                    "sender":
                    request.sid
                },
                room=target
            )



    # ==========================
    # STOP CAMERA
    # ==========================

    @socketio.on("stop_camera")
    def stop_camera(data):


        room = data.get(
            "room"
        )


        if not room:

            return



        emit(
            "camera_stopped",
            {},
            room=room
        )


        live_creators.pop(
            room,
            None
        )


        live_viewers.pop(
            room,
            None
        )


        print(
            "⛔ Live arrêté :",
            room
        )



    # ==========================
    # QUITTER LIVE
    # ==========================

    @socketio.on("leave_camera")
    def leave_camera(data):


        room = data.get(
            "room"
        )


        leave_room(
            room
        )


        if room in live_viewers:


            if request.sid in live_viewers[room]:

                live_viewers[room].remove(
                    request.sid
                )


        print(
            "👋 Quitte la room :",
            request.sid
        )

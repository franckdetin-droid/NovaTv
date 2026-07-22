from flask_socketio import emit, join_room, leave_room
from flask import request


# Stockage des créateurs de live
live_creators = {}

# Stockage des spectateurs
live_viewers = {}



def socket_events(socketio):


    @socketio.on("connect")
    def connect():

        print(
            "✅ Utilisateur connecté:",
            request.sid
        )



    @socketio.on("disconnect")
    def disconnect():

        print(
            "❌ Déconnecté:",
            request.sid
        )

        # retirer le spectateur si présent
        for room, viewers in list(live_viewers.items()):

            if request.sid in viewers:

                viewers.remove(request.sid)



        # retirer créateur
        for room, creator in list(live_creators.items()):

            if creator == request.sid:

                del live_creators[room]
                    # ==========================
    # REJOINDRE UN LIVE CAMERA
    # ==========================

    @socketio.on("join_camera")
    def join_camera(data):

        room = data["room"]

        join_room(room)


        # Créateur du live
        if data.get("creator"):

            live_creators[room] = request.sid


            live_viewers[room] = []


            print(
                "🎥 Créateur live :",
                room,
                request.sid
            )


        else:

            # Spectateur
            if room not in live_viewers:
                live_viewers[room] = []


            # limite 100 spectateurs
            if len(live_viewers[room]) >= 100:

                emit(
                    "room_full",
                    {
                        "message":
                        "Ce live est complet"
                    }
                )

                return



            live_viewers[room].append(
                request.sid
            )


            print(
                "👀 Nouveau spectateur :",
                request.sid,
                "dans",
                room
            )


            # prévenir le créateur
            creator_sid = live_creators.get(room)


            if creator_sid:

                emit(
                    "viewer_joined",
                    {
                        "viewer":
                        request.sid
                    },
                    room=creator_sid
                        )
                    # ==========================
    # OFFRE WEBRTC DU CREATEUR
    # ==========================

    @socketio.on("camera_offer")
    def camera_offer(data):

        viewer = data.get("target")

        if viewer:

            emit(
                "camera_offer",
                {
                    "offer": data["offer"],
                    "creator": request.sid
                },
                room=viewer
            )

            print(
                "📡 Offre envoyée au spectateur:",
                viewer
            )




    # ==========================
    # REPONSE DU SPECTATEUR
    # ==========================

    @socketio.on("camera_answer")
    def camera_answer(data):

        creator = data.get("target")


        if creator:

            emit(
                "camera_answer",
                {
                    "answer": data["answer"],
                    "viewer": request.sid
                },
                room=creator
            )


            print(
                "✅ Réponse envoyée au créateur:",
                creator
            )
                # ==========================
    # ICE WEBRTC
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


            print(
                "🧊 ICE envoyé vers:",
                target
            )
                # ==========================
    # ARRET DU LIVE
    # ==========================

    @socketio.on("stop_camera")
    def stop_camera(data):

        room = data["room"]


        emit(
            "camera_stopped",
            {},
            room=room
        )


        # supprimer le créateur

        if room in live_creators:

            del live_creators[room]



        # supprimer les spectateurs

        if room in live_viewers:

            del live_viewers[room]



        print(
            "⛔ Live arrêté :",
            room
        )





    # ==========================
    # QUITTER UN LIVE
    # ==========================

    @socketio.on("leave_camera")
    def leave_camera(data):

        room = data["room"]


        leave_room(room)



        if room in live_viewers:


            if request.sid in live_viewers[room]:

                live_viewers[room].remove(
                    request.sid
                )


        print(
            "👋 Sortie live :",
            request.sid
        )
            

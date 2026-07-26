from flask_socketio import emit, join_room, leave_room
from flask import request


# ==================================================
# STOCKAGE GLOBAL
# ==================================================

video_rooms = {}

# Live caméra
live_rooms = {}

# Connexions WebRTC
camera_peers = {}

# ICE en attente
pending_ice = {}



# ==================================================
# SOCKET EVENTS
# ==================================================

def socket_events(socketio):


    # ==================================================
    # CONNEXION
    # ==================================================

    @socketio.on("connect")
    def connect():

        print(
            "🟢 Socket connecté :",
            request.sid
        )



    # ==================================================
    # DECONNEXION
    # ==================================================

    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid


        # -----------------------------
        # Nettoyage appel vidéo
        # -----------------------------

        for room in list(video_rooms):

            if sid in video_rooms[room]:

                video_rooms[room].remove(sid)

                emit(
                    "user_left",
                    {
                        "id": sid
                    },
                    room=room
                )


                if not video_rooms[room]:

                    del video_rooms[room]



        # -----------------------------
        # Nettoyage live caméra
        # -----------------------------

        for room in list(live_rooms):

            live = live_rooms[room]


            # Le créateur quitte

            if live["creator"] == sid:


                emit(
                    "camera_stopped",
                    {},
                    room=room
                )


                del live_rooms[room]

                continue



            # Spectateur quitte

            if sid in live["viewers"]:


                live["viewers"].remove(sid)


                emit(
                    "viewer_count",
                    {
                        "count":
                        len(live["viewers"])
                    },
                    room=room
                )


                emit(
                    "viewer_left",
                    {
                        "viewer_id":sid
                    },
                    room=live["creator"]
                )



            # Invité quitte

            if sid in live["guests"]:


                live["guests"].remove(sid)


                emit(
                    "guest_left",
                    {
                        "id":sid
                    },
                    room=room
                )



        if sid in camera_peers:

            del camera_peers[sid]


        if sid in pending_ice:

            del pending_ice[sid]



        print(
            "🔴 Socket déconnecté :",
            sid
        )



    # ==================================================
    # REJOINDRE LIVE CAMERA
    # ==================================================

    @socketio.on("join_camera")
    def join_camera(data):


        room = data.get("room")

        creator = data.get(
            "creator",
            False
        )



        if not room:

            return



        join_room(room)



        if room not in live_rooms:


            live_rooms[room] = {

                "creator":None,

                "viewers":set(),

                "guests":set()

            }



        live = live_rooms[room]



        # ==========================
        # CREATEUR
        # ==========================

        if creator:


            live["creator"] = request.sid


            emit(
                "creator_ready",
                {
                    "room":room
                },
                room=request.sid
            )


            emit(
                "viewer_count",
                {
                    "count":
                    len(live["viewers"])
                },
                room=request.sid
            )


            print(
                "🎥 Créateur live :",
                request.sid
            )

            return



        # ==========================
        # SPECTATEUR
        # ==========================


        live["viewers"].add(
            request.sid
        )


        emit(
            "viewer_count",
            {
                "count":
                len(live["viewers"])
            },
            room=room
        )


        creator_id = live["creator"]


        if creator_id:


            emit(
                "viewer_joined",
                {

                    "viewer_id":
                    request.sid,


                    "count":
                    len(
                        live["viewers"]
                    )

                },
                room=creator_id
            )



        print(
            "👀 Nouveau spectateur :",
            request.sid
        )



    # ==================================================
    # QUITTER LIVE
    # ==================================================

    @socketio.on("leave_live")
    def leave_live(data):


        room = data.get("room")


        if not room:

            return



        leave_room(room)



        if room in live_rooms:


            live = live_rooms[room]


            live["viewers"].discard(
                request.sid
            )


            live["guests"].discard(
                request.sid
            )


            emit(
                "viewer_count",
                {
                    "count":
                    len(
                        live["viewers"]
                    )
                },
                room=room
            )



        print(
            "🚪 Sortie live :",
            request.sid
        )



    # ==================================================
    # WEBRTC OFFER
    # ==================================================

    @socketio.on("camera_offer")
    def camera_offer(data):


        target = data.get(
            "target"
        )

        offer = data.get(
            "offer"
        )


        if not target or not offer:

            return



        camera_peers[request.sid] = target



        emit(
            "camera_offer",
            {

                "offer":offer,

                "sender":
                request.sid

            },
            room=target
        )



        print(
            "📡 OFFER envoyée :",
            request.sid,
            "->",
            target
             )
         # ==================================================
    # WEBRTC ANSWER
    # ==================================================

    @socketio.on("camera_answer")
    def camera_answer(data):


        target = data.get(
            "target"
        )

        answer = data.get(
            "answer"
        )


        if not target or not answer:

            return



        emit(
            "camera_answer",
            {

                "answer":answer,

                "sender":
                request.sid

            },
            room=target
        )



        print(
            "✅ ANSWER envoyée :",
            request.sid,
            "->",
            target
        )



    # ==================================================
    # WEBRTC ICE
    # ==================================================

    @socketio.on("camera_ice")
    def camera_ice(data):


        target = data.get(
            "target"
        )

        candidate = data.get(
            "candidate"
        )


        if not target or not candidate:

            return



        emit(
            "camera_ice",
            {

                "candidate":
                candidate,


                "sender":
                request.sid

            },
            room=target
        )



        print(
            "🧊 ICE envoyé :",
            request.sid,
            "->",
            target
        )



    # ==================================================
    # DEMANDE INVITE LIVE
    # ==================================================

    @socketio.on("request_join_live")
    def request_join_live(data):


        room = data.get(
            "room"
        )


        if room not in live_rooms:

            return



        creator = live_rooms[room]["creator"]



        if creator:


            emit(
                "join_request",
                {

                    "guest":
                    request.sid

                },
                room=creator
            )



        print(
            "✋ Demande invité :",
            request.sid
        )



    # ==================================================
    # ACCEPTER INVITE
    # ==================================================

    @socketio.on("accept_guest")
    def accept_guest(data):


        room = data.get(
            "room"
        )

        guest = data.get(
            "guest"
        )



        if room not in live_rooms:

            return



        live = live_rooms[room]


        if live["creator"] != request.sid:

            return



        live["guests"].add(
            guest
        )



        emit(
            "guest_accepted",
            {},
            room=guest
        )



        emit(
            "guest_joined",
            {
                "guest":guest
            },
            room=room
        )



        print(
            "✅ Invité accepté :",
            guest
        )



    # ==================================================
    # REFUSER INVITE
    # ==================================================

    @socketio.on("reject_guest")
    def reject_guest(data):


        guest = data.get(
            "guest"
        )


        if guest:


            emit(
                "guest_rejected",
                {},
                room=guest
            )



    # ==================================================
    # CHAT LIVE
    # ==================================================

    @socketio.on("live_message")
    def live_message(data):


        room = data.get(
            "room"
        )


        message = data.get(
            "message",
            ""
        )


        if not room or not message:

            return



        emit(
            "live_message",
            {

                "user":
                request.sid[:6],


                "message":
                message

            },
            room=room
        )



    # ==================================================
    # REACTIONS
    # ==================================================

    @socketio.on("live_reaction")
    def live_reaction(data):


        room = data.get(
            "room"
        )


        emoji = data.get(
            "emoji",
            "👍"
        )


        if not room:

            return



        emit(
            "live_reaction",
            {

                "emoji":
                emoji,


                "user":
                request.sid

            },
            room=room
        )



    # ==================================================
    # STATISTIQUES LIVE
    # ==================================================

    @socketio.on("live_stats")
    def live_stats(data):


        room = data.get(
            "room"
        )


        if room not in live_rooms:

            return



        live = live_rooms[room]



        emit(
            "live_stats",
            {

                "viewer_count":
                len(
                    live["viewers"]
                ),


                "guest_count":
                len(
                    live["guests"]
                )

            },
            room=room
        )



    # ==================================================
    # COMPTEUR SPECTATEURS
    # ==================================================

    @socketio.on("viewer_count")
    def send_viewer_count(data):


        room = data.get(
            "room"
        )


        if room not in live_rooms:

            return



        emit(
            "viewer_count",
            {

                "count":
                len(
                    live_rooms[room]["viewers"]
                )

            },
            room=room
        )



    # ==================================================
    # ARRET LIVE
    # ==================================================

    @socketio.on("stop_camera")
    def stop_camera(data):


        room = data.get(
            "room"
        )


        if room not in live_rooms:

            return



        live = live_rooms[room]



        if live["creator"] != request.sid:

            return



        emit(
            "camera_stopped",
            {},
            room=room
        )



        emit(
            "viewer_count",
            {
                "count":0
            },
            room=room
        )



        del live_rooms[room]



        print(
            "⛔ Live arrêté :",
            room
 )
         # ==================================================
    # EXPULSER UN INVITE
    # ==================================================

    @socketio.on("kick_guest")
    def kick_guest(data):


        room = data.get(
            "room"
        )

        guest = data.get(
            "guest"
        )


        if room not in live_rooms:

            return



        live = live_rooms[room]



        # Seulement le créateur

        if live["creator"] != request.sid:

            return



        live["guests"].discard(
            guest
        )



        emit(
            "kicked",
            {},
            room=guest
        )



        emit(
            "guest_left",
            {
                "id":guest
            },
            room=room
        )



        emit(
            "live_stats",
            {

                "viewer_count":
                len(
                    live["viewers"]
                ),


                "guest_count":
                len(
                    live["guests"]
                )

            },
            room=room
        )



        print(
            "🚫 Invité expulsé :",
            guest
        )



    # ==================================================
    # INFORMATIONS DU LIVE
    # ==================================================

    @socketio.on("get_live_info")
    def get_live_info(data):


        room = data.get(
            "room"
        )


        if room not in live_rooms:


            emit(
                "live_info",
                {

                    "exists":
                    False

                },
                room=request.sid
            )

            return



        live = live_rooms[room]



        emit(
            "live_info",
            {

                "exists":
                True,


                "creator":
                live["creator"],


                "viewers":
                len(
                    live["viewers"]
                ),


                "guests":
                len(
                    live["guests"]
                )

            },
            room=request.sid
        )



    # ==================================================
    # PING SERVEUR LIVE
    # ==================================================

    @socketio.on("ping_live")
    def ping_live():


        emit(
            "pong_live",
            {},
            room=request.sid
        )



    # ==================================================
    # NETTOYAGE LIVE
    # ==================================================

    @socketio.on("cleanup_live")
    def cleanup_live(data):


        room = data.get(
            "room"
        )


        if not room:

            return



        if room in live_rooms:


            live = live_rooms[room]



            if live["creator"] == request.sid:


                emit(
                    "camera_stopped",
                    {},
                    room=room
                )



                del live_rooms[room]



                print(
                    "🧹 Salle supprimée :",
                    room
                )



    # ==================================================
    # FERMER CONNEXION WEBRTC
    # ==================================================

    @socketio.on("close_peer")
    def close_peer(data):


        target = data.get(
            "target"
        )


        if target in camera_peers:

            del camera_peers[target]



        if target in pending_ice:

            del pending_ice[target]



        print(
            "🔌 Peer fermé :",
            target
        )



    # ==================================================
    # FIN
    # ==================================================

    print(
        "✅ Socket Events MY TV chargés avec WebRTC + spectateurs."
    )

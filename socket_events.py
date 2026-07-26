from flask_socketio import emit, join_room, leave_room
from flask import request


# ==================================================
# APPEL VIDEO
# ==================================================

video_rooms = {}



# ==================================================
# LIVE CAMERA WEBRTC
# ==================================================

live_rooms = {}


"""
Structure :

live_rooms = {

    "camera_live_1":{

        "creator":"SID123",

        "viewers":set(),

        "guests":set()

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



        # ==========================
        # APPEL VIDEO
        # ==========================


        for room in list(video_rooms.keys()):


            if sid in video_rooms[room]:


                video_rooms[room].remove(sid)



                emit(
                    "user_left",
                    {
                        "id":sid
                    },
                    room=room
                )



                leave_room(room)



                if len(video_rooms[room]) == 0:

                    del video_rooms[room]




        # ==========================
        # LIVE CAMERA
        # ==========================


        for room in list(live_rooms.keys()):


            live = live_rooms[room]



            # Créateur quitte


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
                    "viewer_left",
                    {
                        "viewer_id":sid
                    },
                    room=live["creator"]
                )



                emit(
                    "viewer_count",
                    {
                        "count":len(
                            live["viewers"]
                        )
                    },
                    room=room
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



        print(
            "🔴 Déconnecté :",
            sid
        )




    # ============================================
    # APPEL VIDEO - REJOINDRE
    # ============================================


    @socketio.on("join_room")
    def join_room_video(data):


        room = data.get("room")



        if not room:

            return



        join_room(room)



        if room not in video_rooms:

            video_rooms[room] = []



        emit(
            "all_users",
            {
                "users":video_rooms[room]
            },
            room=request.sid
        )



        if request.sid not in video_rooms[room]:

            video_rooms[room].append(
                request.sid
            )



        emit(
            "user_joined",
            {
                "id":request.sid
            },
            room=room,
            include_self=False
        )



        print(
            "👥 Appel vidéo :",
            room
        )



    @socketio.on("leave_room")
    def leave_video(data):


        room=data.get("room")



        if not room:

            return



        leave_room(room)



        if room in video_rooms:


            if request.sid in video_rooms[room]:

                video_rooms[room].remove(
                    request.sid
                )



        emit(
            "user_left",
            {
                "id":request.sid
            },
            room=room
    )
            # ============================================
    # REJOINDRE UN LIVE CAMERA
    # ============================================


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



        # Création de la salle


        if room not in live_rooms:


            live_rooms[room] = {

                "creator":None,

                "viewers":set(),

                "guests":set()

            }




        live = live_rooms[room]




        # ====================================
        # CREATEUR DU LIVE
        # ====================================


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
                    "count":len(
                        live["viewers"]
                    )
                },
                room=request.sid
            )



            print(
                "🎥 Créateur connecté :",
                request.sid
            )



            return





        # ====================================
        # SPECTATEUR
        # ====================================



        live["viewers"].add(
            request.sid
        )



        creator_sid = live["creator"]




        # Prévenir le créateur
        # pour créer la connexion WebRTC


        if creator_sid:


            emit(
                "viewer_joined",
                {
                    "viewer_id":request.sid,

                    "count":len(
                        live["viewers"]
                    )

                },
                room=creator_sid
            )




        # Mettre à jour le compteur


        emit(
            "viewer_count",
            {
                "count":len(
                    live["viewers"]
                )
            },
            room=room
        )



        print(
            "👀 Nouveau spectateur :",
            request.sid
        )





    # ============================================
    # DEMANDE POUR DEVENIR INVITE
    # ============================================


    @socketio.on("request_join_live")
    def request_join_live(data):


        room=data.get("room")



        if room not in live_rooms:

            return



        creator = live_rooms[room]["creator"]



        if creator:


            emit(
                "join_request",
                {
                    "guest":request.sid
                },
                room=creator
            )



        print(
            "✋ Demande invité :",
            request.sid
        )





    # ============================================
    # ACCEPTER UN INVITE
    # ============================================


    @socketio.on("accept_guest")
    def accept_guest(data):


        room=data.get("room")

        guest=data.get("guest")



        if room not in live_rooms:

            return




        live_rooms[room]["guests"].add(
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





    # ============================================
    # REFUSER UN INVITE
    # ============================================


    @socketio.on("reject_guest")
    def reject_guest(data):


        guest=data.get("guest")



        emit(
            "guest_rejected",
            {},
            room=guest
        )



        print(
            "❌ Invité refusé :",
            guest
        )
            # ============================================
    # CAMERA OFFER
    # Créateur -> Spectateur
    # ============================================


    @socketio.on("camera_offer")
    def camera_offer(data):


        target = data.get("target")



        if not target:

            return




        emit(
            "camera_offer",
            {

                "offer":data.get("offer"),

                "sender":request.sid

            },
            room=target
        )



        print(
            "📡 Offre envoyée :",
            request.sid,
            "->",
            target
        )





    # ============================================
    # CAMERA ANSWER
    # Spectateur -> Créateur
    # ============================================


    @socketio.on("camera_answer")
    def camera_answer(data):


        target = data.get("target")



        if not target:

            return




        emit(
            "camera_answer",
            {

                "answer":data.get("answer"),

                "sender":request.sid

            },
            room=target
        )



        print(
            "✅ Réponse envoyée :",
            request.sid,
            "->",
            target
        )





    # ============================================
    # CAMERA ICE CANDIDATE
    # ============================================


    @socketio.on("camera_ice")
    def camera_ice(data):


        target = data.get("target")



        candidate = data.get(
            "candidate"
        )



        if not target or not candidate:

            return




        emit(
            "camera_ice",
            {

                "candidate":candidate,

                "sender":request.sid

            },
            room=target
        )



        print(
            "🧊 ICE envoyé :",
            request.sid,
            "->",
            target
        )





    # ============================================
    # CHAT DU LIVE
    # ============================================


    @socketio.on("live_message")
    def live_message(data):


        room=data.get("room")



        if not room:

            return




        message=data.get(
            "message",
            ""
        )



        emit(
            "live_message",
            {

                "user":request.sid[:6],

                "message":message

            },
            room=room
        )



        print(
            "💬 Message live :",
            message
        )





    # ============================================
    # REACTIONS LIVE
    # ============================================


    @socketio.on("live_reaction")
    def live_reaction(data):


        room=data.get("room")



        if not room:

            return




        emit(
            "live_reaction",
            {

                "emoji":data.get(
                    "emoji",
                    "👍"
                ),

                "user":request.sid

            },
            room=room
        )



        print(
            "❤️ Réaction :",
            data.get("emoji")
        )
            # ============================================
    # STATISTIQUES DU LIVE
    # ============================================


    @socketio.on("live_stats")
    def live_stats(data):


        room = data.get("room")



        if room not in live_rooms:

            return



        live = live_rooms[room]



        emit(
            "live_stats",
            {

                "viewer_count":
                    len(live["viewers"]),

                "guest_count":
                    len(live["guests"])

            },
            room=room
        )





    # ============================================
    # EXPULSER UN INVITE
    # ============================================


    @socketio.on("kick_guest")
    def kick_guest(data):


        room=data.get("room")

        guest=data.get("guest")



        if room not in live_rooms:

            return



        live=live_rooms[room]




        if guest in live["guests"]:


            live["guests"].remove(
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
                    len(live["viewers"]),


                "guest_count":
                    len(live["guests"])

            },
            room=room
        )



        print(
            "🚫 Invité expulsé :",
            guest
        )





    # ============================================
    # ENVOYER LE COMPTEUR SPECTATEURS
    # ============================================


    @socketio.on("viewer_count")
    def viewer_count(data):


        room=data.get("room")



        if room not in live_rooms:

            return



        live=live_rooms[room]



        emit(
            "viewer_count",
            {

                "count":
                    len(live["viewers"])

            },
            room=room
        )





    # ============================================
    # ARRETER LE LIVE
    # ============================================


    @socketio.on("stop_camera")
    def stop_camera(data):


        room=data.get("room")



        if not room:

            return




        if room in live_rooms:



            emit(
                "camera_stopped",
                {},
                room=room
            )



            emit(
                "live_stats",
                {

                    "viewer_count":0,

                    "guest_count":0

                },
                room=room
            )



            del live_rooms[room]



        print(
            "⛔ Live arrêté :",
            room
        )
            # ============================================
    # PING CONNEXION LIVE
    # ============================================


    @socketio.on("ping_live")
    def ping_live():


        emit(
            "pong_live",
            {},
            room=request.sid
        )





    # ============================================
    # INFORMATIONS DU LIVE
    # ============================================


    @socketio.on("get_live_info")
    def get_live_info(data):


        room=data.get("room")



        if room not in live_rooms:


            emit(
                "live_info",
                {

                    "exists":False

                },
                room=request.sid
            )


            return




        live=live_rooms[room]



        emit(
            "live_info",
            {

                "exists":True,

                "creator":
                    live["creator"],


                "viewers":
                    len(live["viewers"]),


                "guests":
                    len(live["guests"])

            },
            room=request.sid
        )





    # ============================================
    # NETTOYAGE MANUEL D'UN LIVE
    # ============================================


    @socketio.on("leave_live")
    def leave_live(data):


        room=data.get("room")



        if not room:

            return



        leave_room(room)



        if room in live_rooms:


            live=live_rooms[room]



            if request.sid in live["viewers"]:

                live["viewers"].remove(
                    request.sid
                )



            if request.sid in live["guests"]:

                live["guests"].remove(
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



        print(
            "🚪 Sortie du live :",
            request.sid
        )





    # ============================================
    # FIN CHARGEMENT SOCKET
    # ============================================


    print(
        "✅ Socket Events MY TV chargés."
    )

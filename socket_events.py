from flask_socketio import emit, join_room, leave_room
from flask import request


# ==========================
# APPEL VIDEO MULTI PERSONNES
# ==========================

video_rooms = {}



# ==========================
# LIVE CAMERA TV
# ==========================

live_creators = {}
live_viewers = {}




def socket_events(socketio):


    # ==========================
    # CONNEXION
    # ==========================

    @socketio.on("connect")
    def connect():

        print(
            "🟢 Socket connecté :",
            request.sid
        )




    # ==========================
    # DECONNEXION
    # ==========================

    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid


        # retirer appel vidéo

        for room, users in list(video_rooms.items()):

            if sid in users:

                users.remove(sid)

                emit(
                    "user_left",
                    {
                        "id": sid
                    },
                    room=room
                )


            if len(users) == 0:
                del video_rooms[room]



        # retirer live caméra

        for room, viewers in list(live_viewers.items()):

            if sid in viewers:

                viewers.remove(sid)



        for room, creator in list(live_creators.items()):

            if creator == sid:

                del live_creators[room]


                emit(
                    "camera_stopped",
                    {},
                    room=room
                )



        print(
            "🔴 Déconnecté :",
            sid
        )




    # ==================================================
    # APPEL VIDEO MULTI PERSONNES
    # ==================================================


    @socketio.on("join_room")
    def join_video_room(data):


        room = data["room"]


        join_room(room)



        if room not in video_rooms:

            video_rooms[room] = []



        # envoyer les anciens utilisateurs

        emit(
            "all_users",
            video_rooms[room]
        )



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
            request.sid,
            room
        )





    @socketio.on("offer")
    def video_offer(data):


        emit(
            "offer",
            {
                "from":request.sid,
                "offer":data["offer"]
            },
            room=data["target"]
        )





    @socketio.on("answer")
    def video_answer(data):


        emit(
            "answer",
            {
                "from":request.sid,
                "answer":data["answer"]
            },
            room=data["target"]
        )





    @socketio.on("ice_candidate")
    def video_ice(data):


        emit(
            "ice_candidate",
            {
                "from":request.sid,
                "candidate":data["candidate"]
            },
            room=data["target"]
        )






    @socketio.on("leave_room")
    def leave_video(data):


        room=data["room"]


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




    # ==================================================
    # LIVE CAMERA MY TV
    # ==================================================


    @socketio.on("join_camera")
    def join_camera(data):


        room=data.get("room")

        creator=data.get(
            "creator",
            False
        )


        join_room(room)



        if creator:


            live_creators[room]=request.sid


            print(
                "🎥 Créateur live :",
                room
            )



        else:


            if room not in live_viewers:

                live_viewers[room]=[]



            live_viewers[room].append(
                request.sid
            )


            creator_sid=live_creators.get(room)



            if creator_sid:


                emit(
                    "viewer_joined",
                    {
                        "viewer_id":request.sid
                    },
                    room=creator_sid
                )



            print(
                "👀 Spectateur live :",
                room
            )






    @socketio.on("camera_offer")
    def camera_offer(data):


        emit(
            "camera_offer",
            {
                "offer":data["offer"],
                "sender":request.sid
            },
            room=data["target"]
        )





    @socketio.on("camera_answer")
    def camera_answer(data):


        emit(
            "camera_answer",
            {
                "answer":data["answer"],
                "sender":request.sid
            },
            room=data["target"]
        )





    @socketio.on("camera_ice")
    def camera_ice(data):


        emit(
            "camera_ice",
            {
                "candidate":data["candidate"],
                "sender":request.sid
            },
            room=data["target"]
        )






    @socketio.on("stop_camera")
    def stop_camera(data):


        room=data.get("room")


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

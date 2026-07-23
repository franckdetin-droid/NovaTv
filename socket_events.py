from flask_socketio import emit, join_room, leave_room
from flask import request


# ==================================================
# APPEL VIDEO MULTI PERSONNES
# ==================================================

video_rooms = {}



# ==================================================
# LIVE CAMERA MY TV
# ==================================================

live_creators = {}
live_viewers = {}





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



        # ------------------------------
        # APPEL VIDEO
        # ------------------------------

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


                leave_room(room)



            if len(users) == 0:

                del video_rooms[room]






        # ------------------------------
        # LIVE CAMERA
        # ------------------------------


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
    # REJOINDRE APPEL VIDEO
    # ==================================================

    @socketio.on("join_room")
    def join_video_room(data):


        room = data.get(
            "room"
        )


        if not room:

            return



        join_room(room)



        if room not in video_rooms:

            video_rooms[room] = []




        # envoyer les utilisateurs déjà présents

        emit(
            "all_users",
            {
                "users": video_rooms[room]
            }
        )





        # ajouter utilisateur

        if request.sid not in video_rooms[room]:


            video_rooms[room].append(
                request.sid
            )





        # prévenir les autres


        emit(
            "user_joined",
            {
                "id": request.sid
            },
            room=room,
            include_self=False
        )



        print(
            "👥 Appel vidéo :",
            request.sid,
            room
        )








    # ==================================================
    # WEBRTC OFFER
    # ==================================================

    @socketio.on("offer")
    def offer(data):


        emit(
            "offer",
            {
                "from": request.sid,

                "offer": data["offer"]
            },

            room=data["target"]
        )






    # ==================================================
    # WEBRTC ANSWER
    # ==================================================

    @socketio.on("answer")
    def answer(data):


        emit(
            "answer",
            {
                "from": request.sid,

                "answer": data["answer"]
            },

            room=data["target"]
        )







    # ==================================================
    # ICE
    # ==================================================

    @socketio.on("ice_candidate")
    def ice_candidate(data):


        emit(
            "ice_candidate",
            {
                "from": request.sid,

                "candidate": data["candidate"]
            },

            room=data["target"]
        )








    # ==================================================
    # QUITTER APPEL VIDEO
    # ==================================================

    @socketio.on("leave_room")
    def leave_video(data):


        room = data.get(
            "room"
        )


        leave_room(room)



        if room in video_rooms:


            if request.sid in video_rooms[room]:


                video_rooms[room].remove(
                    request.sid
                )



        emit(
            "user_left",
            {
                "id": request.sid
            },
            room=room
        )









    # ==================================================
    # LIVE CAMERA MY TV
    # ==================================================

    @socketio.on("join_camera")
    def join_camera(data):


        room = data.get(
            "room"
        )


        creator = data.get(
            "creator",
            False
        )



        if not room:

            return



        join_room(room)




        if creator:


            live_creators[room] = request.sid



            if room not in live_viewers:

                live_viewers[room] = []



            print(
                "🎥 Créateur live :",
                room
            )





        else:


            if room not in live_viewers:

                live_viewers[room] = []



            live_viewers[room].append(
                request.sid
            )



            creator_sid = live_creators.get(
                room
            )



            if creator_sid:


                emit(
                    "viewer_joined",
                    {
                        "viewer_id": request.sid
                    },
                    room=creator_sid
                )



            print(
                "👀 Spectateur live :",
                room
            )








    # ==================================================
    # CAMERA OFFER
    # ==================================================

    @socketio.on("camera_offer")
    def camera_offer(data):


        emit(
            "camera_offer",
            {
                "offer": data["offer"],

                "sender": request.sid
            },

            room=data["target"]
        )






    # ==================================================
    # CAMERA ANSWER
    # ==================================================

    @socketio.on("camera_answer")
    def camera_answer(data):


        emit(
            "camera_answer",
            {
                "answer": data["answer"],

                "sender": request.sid
            },

            room=data["target"]
        )







    # ==================================================
    # CAMERA ICE
    # ==================================================

    @socketio.on("camera_ice")
    def camera_ice(data):


        emit(
            "camera_ice",
            {
                "candidate": data["candidate"],

                "sender": request.sid
            },

            room=data["target"]
        )







    # ==================================================
    # STOP CAMERA LIVE
    # ==================================================

    @socketio.on("stop_camera")
    def stop_camera(data):


        room = data.get(
            "room"
        )


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

from flask_socketio import emit, join_room, leave_room
from flask import request


rooms = {}


def socket_events(socketio):


    @socketio.on("connect")
    def connect():
        print("🟢 Connecté :", request.sid)



    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid

        for room, users in list(rooms.items()):

            if sid in users:

                users.remove(sid)

                emit(
                    "user_left",
                    {"id": sid},
                    room=room
                )

            if len(users) == 0:
                del rooms[room]

        print("🔴 Déconnecté :", sid)



    @socketio.on("join_room")
    def join(data):

        room = data["room"]

        join_room(room)


        if room not in rooms:
            rooms[room] = []


        # envoyer les anciens utilisateurs
        emit(
            "all_users",
            rooms[room]
        )


        # ajouter le nouveau
        rooms[room].append(
            request.sid
        )


        emit(
            "user_joined",
            {
                "id": request.sid
            },
            room=room,
            include_self=False
        )


        print(
            "👥",
            request.sid,
            "rejoint",
            room
        )



    @socketio.on("offer")
    def offer(data):

        emit(
            "offer",
            {
                "from":request.sid,
                "offer":data["offer"]
            },
            room=data["target"]
        )



    @socketio.on("answer")
    def answer(data):

        emit(
            "answer",
            {
                "from":request.sid,
                "answer":data["answer"]
            },
            room=data["target"]
        )



    @socketio.on("ice_candidate")
    def ice(data):

        emit(
            "ice_candidate",
            {
                "from":request.sid,
                "candidate":data["candidate"]
            },
            room=data["target"]
        )



    @socketio.on("leave_room")
    def leave(data):

        room=data["room"]

        leave_room(room)


        if room in rooms:

            if request.sid in rooms[room]:

                rooms[room].remove(
                    request.sid
                )


        emit(
            "user_left",
            {
                "id":request.sid
            },
            room=room
        )

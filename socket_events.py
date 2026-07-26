from flask_socketio import emit, join_room, leave_room
from flask import request


# ==================================================
# STOCKAGE GLOBAL
# ==================================================

video_rooms = {}


# Live caméra WebRTC
live_rooms = {}


# Connexions WebRTC
camera_peers = {}


# ICE en attente
pending_ice = {}


# Connexions créateur -> spectateurs
camera_connections = {}



"""
Structure live_rooms :

{
 "camera_live_1":{
    
    "creator":"SID",

    "viewers":set(),

    "guests":set(),

    "viewers_info":{}

 }
}

"""



# ==================================================
# SOCKET EVENTS
# ==================================================

def socket_events(socketio):



    # ==================================================
    # CONNEXION
    # ==================================================

    @socketio.on("connect")
    def connect():

        sid = request.sid

        print(
            "🟢 Socket connecté :",
            sid
        )



    # ==================================================
    # DECONNEXION
    # ==================================================

    @socketio.on("disconnect")
    def disconnect():

        sid = request.sid


        print(
            "🔴 Déconnexion :",
            sid
        )



        # ------------------------------
        # Nettoyage appels vidéo
        # ------------------------------

        for room in list(video_rooms.keys()):


            if sid in video_rooms[room]:


                video_rooms[room].remove(
                    sid
                )


                emit(
                    "user_left",
                    {
                        "id":sid
                    },
                    room=room
                )


                if not video_rooms[room]:

                    del video_rooms[room]




        # ------------------------------
        # Nettoyage live caméra
        # ------------------------------

        for room in list(live_rooms.keys()):


            live = live_rooms[room]



            # Le créateur quitte

            if live["creator"] == sid:


                emit(
                    "camera_stopped",
                    {
                        "reason":"creator_left"
                    },
                    room=room
                )


                del live_rooms[room]


                continue





            # Spectateur quitte

            if sid in live["viewers"]:


                live["viewers"].remove(
                    sid
                )


                if sid in live["viewers_info"]:

                    del live["viewers_info"][sid]



                emit(
                    "viewer_left",
                    {
                        "viewer_id":sid
                    },
                    room=room
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





            # Invité quitte

            if sid in live["guests"]:


                live["guests"].remove(
                    sid
                )


                emit(
                    "guest_left",
                    {
                        "id":sid
                    },
                    room=room
                )



        # Nettoyage WebRTC

        if sid in camera_peers:

            del camera_peers[sid]



        if sid in pending_ice:

            del pending_ice[sid]



        if sid in camera_connections:

            del camera_connections[sid]




    # ==================================================
    # APPEL VIDEO CLASSIQUE
    # ==================================================

    @socketio.on("join_room")
    def join_video(data):


        room = data.get(
            "room"
        )


        if not room:

            return



        join_room(room)



        if room not in video_rooms:

            video_rooms[room] = []



        users = video_rooms[room]



        emit(
            "all_users",
            {
                "users":users
            },
            room=request.sid
        )



        if request.sid not in users:

            users.append(
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
            "👥 Appel vidéo rejoint :",
            room
        )




    @socketio.on("leave_room")
    def leave_video(data):


        room=data.get(
            "room"
        )


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



    # ==================================================
    # REJOINDRE LIVE CAMERA
    # (CORRIGÉ POUR LES SPECTATEURS)
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



        if room not in live_rooms:


            live_rooms[room]={

                "creator":None,

                "viewers":set(),

                "guests":set(),

                "viewers_info":{}

            }



        live = live_rooms[room]



        if creator:


            live["creator"]=request.sid


            camera_connections[request.sid]={}


            emit(
                "creator_ready",
                {
                    "room":room
                },
                room=request.sid
            )


            print(
                "🎥 Créateur prêt :",
                request.sid
            )


            return



        # ------------------------------
        # SPECTATEUR
        # ------------------------------

        live["viewers"].add(
            request.sid
        )


        live["viewers_info"][request.sid]={

            "connected":True

        }



        creator_sid = live["creator"]



        # informer le créateur

        if creator_sid:


            emit(
                "viewer_joined",
                {
                    "viewer_id":request.sid,

                    "count":
                    len(
                        live["viewers"]
                    )
                },
                room=creator_sid
            )



        # informer toute la salle

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
            "👀 Spectateur connecté :",
            request.sid
)
            # ==================================================
    # QUITTER UN LIVE
    # ==================================================

    @socketio.on("leave_live")
    def leave_live(data):


        room = data.get(
            "room"
        )


        if not room:

            return



        leave_room(room)



        if room in live_rooms:


            live = live_rooms[room]



            if request.sid in live["viewers"]:

                live["viewers"].remove(
                    request.sid
                )



            if request.sid in live["guests"]:

                live["guests"].remove(
                    request.sid
                )



            if request.sid in live["viewers_info"]:

                del live["viewers_info"][request.sid]



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
    # DEMANDE POUR DEVENIR INVITE
    # ==================================================

    @socketio.on("request_join_live")
    def request_join_live(data):


        room=data.get(
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


        room=data.get(
            "room"
        )


        guest=data.get(
            "guest"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



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


        guest=data.get(
            "guest"
        )


        if guest:


            emit(
                "guest_rejected",
                {},
                room=guest
            )



        print(
            "❌ Invité refusé"
        )





    # ==================================================
    # WEBRTC OFFER
    # CREATEUR -> SPECTATEUR
    # ==================================================

    @socketio.on("camera_offer")
    def camera_offer(data):


        target=data.get(
            "target"
        )


        offer=data.get(
            "offer"
        )



        if not target or not offer:

            return



        camera_peers[request.sid]=target



        if request.sid not in camera_connections:


            camera_connections[request.sid]={}



        camera_connections[request.sid][target]=True



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
    # SPECTATEUR -> CREATEUR
    # ==================================================

    @socketio.on("camera_answer")
    def camera_answer(data):


        target=data.get(
            "target"
        )


        answer=data.get(
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
            "✅ ANSWER reçue :",
            request.sid,
            "->",
            target
        )





    # ==================================================
    # WEBRTC ICE
    # ==================================================

    @socketio.on("camera_ice")
    def camera_ice(data):


        target=data.get(
            "target"
        )


        candidate=data.get(
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
            "🧊 ICE :",
            request.sid,
            "->",
            target
        )





    # ==================================================
    # FERMER UNE CONNEXION WEBRTC
    # ==================================================

    @socketio.on("close_peer")
    def close_peer(data):


        target=data.get(
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



        print(
            "💬 Message live :",
            message
        )





    # ==================================================
    # REACTIONS LIVE
    # ==================================================

    @socketio.on("live_reaction")
    def live_reaction(data):


        room=data.get(
            "room"
        )


        emoji=data.get(
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
                request.sid[:6]

            },
            room=room
        )



        print(
            "❤️ Réaction :",
            emoji
        )





    # ==================================================
    # DEMANDE STATISTIQUES LIVE
    # ==================================================

    @socketio.on("live_stats")
    def live_stats(data):


        room=data.get(
            "room"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



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
            "📊 Stats envoyées :",
            room
        )





    # ==================================================
    # COMPTEUR SPECTATEURS
    # ==================================================

    @socketio.on("viewer_count")
    def viewer_count(data):


        room=data.get(
            "room"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



        count=len(
            live["viewers"]
        )



        emit(
            "viewer_count",
            {

                "count":
                count

            },
            room=room
        )



        print(
            "👥 Spectateurs :",
            count
        )





    # ==================================================
    # EXPULSER UN INVITE
    # ==================================================

    @socketio.on("kick_guest")
    def kick_guest(data):


        room=data.get(
            "room"
        )


        guest=data.get(
            "guest"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



        # seulement le créateur

        if live["creator"] != request.sid:

            return



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
    # ARRET DU LIVE CAMERA
    # ==================================================

    @socketio.on("stop_camera")
    def stop_camera(data):


        room=data.get(
            "room"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



        # sécurité créateur

        if live["creator"] != request.sid:

            return



        emit(
            "camera_stopped",
            {

                "reason":
                "creator_stop"

            },
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
            # ==================================================
    # INFORMATIONS DU LIVE
    # ==================================================

    @socketio.on("get_live_info")
    def get_live_info(data):


        room=data.get(
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




        live=live_rooms[room]



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



        print(
            "ℹ️ Infos live envoyées :",
            room
        )





    # ==================================================
    # PING SERVEUR
    # ==================================================

    @socketio.on("ping_live")
    def ping_live():


        emit(
            "pong_live",
            {

                "time":
                request.sid

            },
            room=request.sid
        )





    # ==================================================
    # NETTOYAGE LIVE
    # ==================================================

    @socketio.on("cleanup_live")
    def cleanup_live(data):


        room=data.get(
            "room"
        )



        if not room:

            return



        if room in live_rooms:


            live=live_rooms[room]



            # seul le créateur peut nettoyer

            if live["creator"] == request.sid:


                emit(
                    "camera_stopped",
                    {
                        "reason":
                        "cleanup"
                    },
                    room=room
                )



                del live_rooms[room]



                print(
                    "🧹 Salle supprimée :",
                    room
                )





    # ==================================================
    # FERMETURE PEER WEBRTC
    # ==================================================

    @socketio.on("close_peer")
    def close_peer(data):


        target=data.get(
            "target"
        )



        if not target:

            return



        if target in camera_peers:

            del camera_peers[target]



        if target in pending_ice:

            del pending_ice[target]



        print(
            "🔌 Connexion WebRTC fermée :",
            target
        )





    # ==================================================
    # SYNCHRONISATION DES SPECTATEURS
    # (CORRECTION DU PROBLEME INVISIBLE)
    # ==================================================

    @socketio.on("request_viewers")
    def request_viewers(data):


        room=data.get(
            "room"
        )



        if room not in live_rooms:

            return



        live=live_rooms[room]



        viewers=list(
            live["viewers"]
        )



        emit(
            "viewer_list",
            {

                "viewers":
                viewers,

                "count":
                len(viewers)

            },
            room=request.sid
        )



        print(
            "👀 Liste spectateurs envoyée :",
            len(viewers)
        )





    # ==================================================
    # FORCER MISE A JOUR COMPTEUR
    # ==================================================

    def update_viewer_count(room):


        if room not in live_rooms:

            return



        count=len(
            live_rooms[room]["viewers"]
        )



        emit(
            "viewer_count",
            {

                "count":
                count

            },
            room=room
        )
            # ==================================================
    # VERIFICATION SALLE LIVE
    # ==================================================

    @socketio.on("check_live")
    def check_live(data):


        room=data.get(
            "room"
        )



        if not room:


            emit(
                "live_status",
                {
                    "online":False
                },
                room=request.sid
            )

            return



        if room in live_rooms:


            live=live_rooms[room]


            emit(
                "live_status",
                {

                    "online":True,


                    "creator":
                    live["creator"],


                    "viewers":
                    len(
                        live["viewers"]
                    )

                },
                room=request.sid
            )



        else:


            emit(
                "live_status",
                {

                    "online":False

                },
                room=request.sid
            )





    # ==================================================
    # REJOINDRE AUTOMATIQUEMENT APRES RECONNEXION
    # ==================================================

    @socketio.on("reconnect_live")
    def reconnect_live(data):


        room=data.get(
            "room"
        )



        if not room:

            return



        if room not in live_rooms:

            emit(
                "camera_stopped",
                {
                    "reason":
                    "live_not_found"
                },
                room=request.sid
            )

            return



        join_room(room)



        live=live_rooms[room]



        live["viewers"].add(
            request.sid
        )


        live["viewers_info"][request.sid]={

            "reconnected":True

        }



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



        if live["creator"]:


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
                room=live["creator"]
            )



        print(
            "🔄 Spectateur reconnecté :",
            request.sid
        )





    # ==================================================
    # ERREUR SOCKET
    # ==================================================

    @socketio.on_error()
    def socket_error(error):


        print(
            "⚠️ Erreur Socket.IO :",
            error
        )





    # ==================================================
    # FIN
    # ==================================================

    print(
        "✅ Socket Events MY TV chargés avec WebRTC + Live Camera + Spectateurs."
        )

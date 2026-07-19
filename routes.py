from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app
)

import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime

from database import db

from models import (
    User,
    Channel,
    Video,
    LiveStream,
    Program,
    History,
    Favorite,
    VideoLike
)

from broadcast_scheduler import (
    get_current_program
)


main = Blueprint(
    "main",
    __name__
)

# ==========================
# ACCUEIL
# ==========================
@main.route("/")
def home():

    channels = Channel.query.all()

    videos = Video.query.all()

    history_videos = []


    if "user_id" in session:

        histories = History.query.filter_by(
            user_id=session["user_id"]
        ).all()


        for item in histories:

            video = Video.query.get(
                item.video_id
            )

            if video:
                history_videos.append(video)



    return render_template(
        "home.html",
        channels=channels,
        videos=videos,
        history_videos=history_videos
    )

# ==========================
# VERIFICATION FICHIERS
# ==========================

ALLOWED_IMAGES = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


ALLOWED_VIDEOS = {
    "mp4",
    "mkv",
    "avi"
}



def file_extension(filename):

    return filename.rsplit(
        ".",
        1
    )[-1].lower()





def is_image(filename):

    return (
        "." in filename
        and
        file_extension(filename) in ALLOWED_IMAGES
    )





def is_video(filename):

    return (
        "." in filename
        and
        file_extension(filename) in ALLOWED_VIDEOS
    )





# ==========================
# CHAÎNES
# ==========================

@main.route("/channels")
def channels():


    channels = Channel.query.all()


    return render_template(
        "channels.html",
        channels=channels
    )





# ==========================
# PROFIL
# ==========================

@main.route("/profile")
def profile():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    user = User.query.get(
        session["user_id"]
    )


    return render_template(
        "profile.html",
        user=user
    )





# ==========================
# DIRECT TV
# ==========================

@main.route("/live")
def live():

    lives = LiveStream.query.filter_by(
        is_live=True
    ).all()


    return render_template(
        "live.html",
        lives=lives
    )
    # ==========================
# INSCRIPTION
# ==========================

@main.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]


        existing_email = User.query.filter_by(
            email=email
        ).first()


        existing_username = User.query.filter_by(
            username=username
        ).first()



        if existing_email:

            return "Email déjà utilisé"



        if existing_username:

            return "Nom d'utilisateur déjà utilisé"



        user = User(

            username=username,

            email=email,

            password=generate_password_hash(password)

        )


        db.session.add(user)

        db.session.commit()



        return redirect(
            url_for("main.login")
        )


    return render_template(
        "register.html"
    )
# ==========================
# CONNEXION
# ==========================

@main.route(
    "/login",
    methods=["GET", "POST"]
)
def login():


    if request.method == "POST":


        username = request.form["username"]

        password = request.form["password"]



        user = User.query.filter_by(
            username=username
        ).first()



        if user and check_password_hash(
            user.password,
            password
        ):


            session.permanent = True


            session["user_id"] = user.id



            return redirect(
                url_for("main.home")
            )



        return "Identifiants incorrects"



    return render_template(
        "login.html"
    )





# ==========================
# DECONNEXION
# ==========================

@main.route("/logout")
def logout():


    session.clear()


    return redirect(
        url_for("main.home")
    ) 


# ==========================
# CREER UNE CHAINE
# ==========================

@main.route(
    "/create-channel",
    methods=["GET", "POST"]
)
def create_channel():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )


    if request.method == "POST":


        name = request.form["name"]

        category = request.form["category"]

        description = request.form["description"]


        logo = request.files.get("logo")

        cover = request.files.get("cover")



        upload_folder = current_app.config["UPLOAD_FOLDER"]


        os.makedirs(
            os.path.join(upload_folder, "logos"),
            exist_ok=True
        )

        os.makedirs(
            os.path.join(upload_folder, "covers"),
            exist_ok=True
        )


        logo_name = None

        cover_name = None



        if logo and logo.filename:


            logo_name = secure_filename(
                logo.filename
            )


            logo.save(
                os.path.join(
                    upload_folder,
                    "logos",
                    logo_name
                )
            )



        if cover and cover.filename:


            cover_name = secure_filename(
                cover.filename
            )


            cover.save(
                os.path.join(
                    upload_folder,
                    "covers",
                    cover_name
                )
            )



        channel = Channel(

            user_id=session["user_id"],

            name=name,

            category=category,

            description=description,

            logo=(
                "uploads/logos/" + logo_name
                if logo_name else None
            ),

            cover=(
                "uploads/covers/" + cover_name
                if cover_name else None
            )

        )


        db.session.add(channel)

        db.session.commit()



        return redirect(
            url_for("main.channels")
        )


    return render_template(
        "create_channel.html"
        )
# ==========================
# UPLOAD VIDEO
# ==========================

@main.route(
    "/upload-video",
    methods=["GET", "POST"]
)
def upload_video():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    channels = Channel.query.filter_by(
        user_id=session["user_id"]
    ).all()



    if request.method == "POST":


        channel_id = request.form["channel_id"]

        title = request.form["title"]

        description = request.form["description"]

        category = request.form["category"]

        content_type = request.form["content_type"]



        video_file = request.files.get(
            "video"
        )

        thumbnail = request.files.get(
            "thumbnail"
        )



        upload_folder = current_app.config[
            "UPLOAD_FOLDER"
        ]



        video_name = None

        thumbnail_name = None



        if video_file and video_file.filename:


            video_name = secure_filename(
                video_file.filename
            )


            video_file.save(
                os.path.join(
                    upload_folder,
                    "videos",
                    video_name
                )
            )



        if thumbnail and thumbnail.filename:


            thumbnail_name = secure_filename(
                thumbnail.filename
            )


            thumbnail.save(
                os.path.join(
                    upload_folder,
                    "thumbnails",
                    thumbnail_name
                )
            )



        video = Video(

            channel_id=channel_id,

            title=title,

            description=description,

            category=category,

            content_type=content_type,

            file_path=(
                "uploads/videos/" + video_name
                if video_name else None
            ),

            thumbnail=(
                "uploads/thumbnails/" + thumbnail_name
                if thumbnail_name else None
            )

        )



        db.session.add(video)

        db.session.commit()



        return redirect(
            url_for("main.creator")
        )



    return render_template(
        "upload_video.html",
        channels=channels
    )
    # ==========================
# CREATOR STUDIO
# ==========================

@main.route("/creator")
def creator():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    channels = Channel.query.filter_by(
        user_id=session["user_id"]
    ).all()



    videos = Video.query.join(
        Channel
    ).filter(
        Channel.user_id == session["user_id"]
    ).all()



    return render_template(
        "creator.html",
        channels=channels,
        videos=videos
    )





# ==========================
# PROGRAMMATION AUTOMATIQUE
# ==========================

@main.route(
    "/schedule",
    methods=["GET", "POST"]
)
def schedule():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    channels = Channel.query.filter_by(
        user_id=session["user_id"]
    ).all()



    videos = Video.query.join(
        Channel
    ).filter(
        Channel.user_id == session["user_id"]
    ).all()



    if request.method == "POST":


        channel_id = request.form["channel_id"]

        video_id = request.form["video_id"]



        start_time = datetime.strptime(
            request.form["start_time"],
            "%Y-%m-%dT%H:%M"
        )


        end_time = datetime.strptime(
            request.form["end_time"],
            "%Y-%m-%dT%H:%M"
        )



        repeat = True if request.form.get(
            "repeat"
        ) else False



        program = Program(

            channel_id=channel_id,

            video_id=video_id,

            start_time=start_time,

            end_time=end_time,

            repeat=repeat

        )


        db.session.add(program)

        db.session.commit()



        return redirect(
            url_for("main.schedule")
        )



    programs = Program.query.join(
        Channel
    ).filter(
        Channel.user_id == session["user_id"]
    ).all()



    return render_template(
        "schedule.html",
        channels=channels,
        videos=videos,
        programs=programs
    )





# ==========================
# RECHERCHE
# ==========================

@main.route("/search")
def search():


    query = request.args.get(
        "q",
        ""
    )



    channels = Channel.query.filter(
        Channel.name.ilike(
            f"%{query}%"
        )
    ).all()



    videos = Video.query.filter(
        Video.title.ilike(
            f"%{query}%"
        )
    ).all()



    return render_template(
        "search.html",
        query=query,
        channels=channels,
        videos=videos
    )





# ==========================
# DETAIL CHAINE
# ==========================

@main.route(
    "/channel/<int:channel_id>"
)
def channel_detail(channel_id):


    channel = Channel.query.get_or_404(
        channel_id
    )



    videos = Video.query.filter_by(
        channel_id=channel.id
    ).all()



    programs = Program.query.filter_by(
        channel_id=channel.id
    ).all()



    live = LiveStream.query.filter_by(
        channel_id=channel.id,
        is_live=True
    ).first()



    return render_template(
        "channel.html",
        channel=channel,
        videos=videos,
        programs=programs,
        live=live
    )





# ==========================
# LECTURE VIDEO
# ==========================
@main.route(
    "/watch/<int:video_id>"
)
def watch(video_id):

    video = Video.query.get_or_404(
        video_id
    )


    # AJOUTER UNE VUE

    try:
        video.views += 1
        db.session.commit()

    except Exception:
        db.session.rollback()



    # AJOUT HISTORIQUE

    if "user_id" in session:

        history = History.query.filter_by(
            user_id=session["user_id"],
            video_id=video.id
        ).first()


        if not history:

            history = History(
                user_id=session["user_id"],
                video_id=video.id
            )

            db.session.add(history)

            db.session.commit()



    related_videos = Video.query.filter(
        Video.channel_id == video.channel_id,
        Video.id != video.id
    ).all()



    # URL VIDEO

    video_url = None


    if video.file_path:

        video_url = url_for(
            "static",
            filename=video.file_path
        )



    return render_template(
        "watch.html",
        video=video,
        video_url=video_url,
        related_videos=related_videos
    )
#==========================
# LIKE VIDEO
# ==========================

@main.route(
    "/like-video/<int:video_id>",
    methods=["POST"]
)
def like_video(video_id):

    video = Video.query.get_or_404(
        video_id
    )


    # Ajoute le like

    video.likes += 1


    db.session.commit()


    return redirect(
        url_for(
            "main.watch",
            video_id=video.id
        )
    )
   
# ==========================
# CREER UN LIVE AVEC URL
# ==========================

@main.route(
    "/create-live",
    methods=["GET", "POST"]
)
def create_live():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    channels = Channel.query.filter_by(
        user_id=session["user_id"]
    ).all()



    if request.method == "POST":


        channel_id = request.form["channel_id"]

        title = request.form["title"]

        stream_url = request.form["stream_url"]



        live = LiveStream(

            channel_id=channel_id,

            title=title,

            stream_url=stream_url,

            is_live=True,

            started_at=datetime.utcnow()

        )



        db.session.add(live)

        db.session.commit()



        return redirect(
            url_for("main.live")
        )



    return render_template(
        "create_live.html",
        channels=channels
    )
    # ==========================
# TV EN COURS
# ==========================

@main.route(
    "/tv/<int:channel_id>"
)
def tv_channel(channel_id):


    channel = Channel.query.get_or_404(
        channel_id
    )


    program = get_current_program(
        channel.id
    )


    if not program:

        program = Program.query.filter(
            Program.channel_id == channel.id,
            Program.start_time > datetime.utcnow()
        ).order_by(
            Program.start_time.asc()
        ).first()



    video = None


    if program:

        video = Video.query.get(
            program.video_id
        )



    return render_template(
        "tv.html",
        channel=channel,
        program=program,
        video=video
    )
# ==========================
# HISTORIQUE FILMS
# ==========================

@main.route("/history")
def history():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    histories = History.query.filter_by(
        user_id=session["user_id"]
    ).all()



    videos = []


    for item in histories:


        video = Video.query.get(
            item.video_id
        )


        if video:

            videos.append(video)



    return render_template(
        "history.html",
        videos=videos
    )




# ==========================
# LISTE DES CAMERAS EN DIRECT
# ==========================

@main.route("/camera-live")
def camera_live():

    cameras = LiveStream.query.filter_by(
        stream_url="camera",
        is_live=True
    ).all()


    return render_template(
        "camera_live.html",
        cameras=cameras
    )

# ==========================
# CREER LIVE CAMERA
# ==========================

@main.route(
    "/start-camera-live",
    methods=["POST"]
)
def create_camera_stream():


    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )



    channel = Channel.query.filter_by(
        user_id=session["user_id"]
    ).first()



    if not channel:

        return "Vous devez créer une chaîne"



    live = LiveStream(

        channel_id=channel.id,

        title="🎥 Live caméra",

        stream_url="camera",

        is_live=True,

        started_at=datetime.utcnow()

    )



    db.session.add(live)

    db.session.commit()



    return "Live caméra démarré"





# ==========================
# ARRETER LIVE CAMERA
# ==========================
@main.route(
    "/stop-camera-live",
    methods=["POST"]
)
def stop_camera_stream():


    live = LiveStream.query.filter_by(
        stream_url="camera",
        is_live=True
    ).first()



    if live:


        live.is_live = False

        live.stopped_at = datetime.utcnow()


        db.session.commit()



    return "Live caméra arrêté"





# ==========================
# REGARDER LIVE CAMERA
# ==========================

@main.route(
    "/watch-camera/<int:live_id>"
)
def watch_camera(live_id):


    live = LiveStream.query.get_or_404(
        live_id
    )


    return render_template(
        "watch_camera.html",
        live=live
    )
    # ==========================
# AJOUTER MA LISTE
# ==========================

@main.route(
    "/add-favorite/<int:video_id>"
)
def add_favorite(video_id):

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )


    existing = Favorite.query.filter_by(
        user_id=session["user_id"],
        video_id=video_id
    ).first()


    if not existing:

        favorite = Favorite(
            user_id=session["user_id"],
            video_id=video_id
        )

        db.session.add(favorite)

        db.session.commit()


    return redirect(
        request.referrer
    )
    # ==========================
# RETIRER DE MA LISTE
# ==========================

@main.route(
    "/remove-favorite/<int:video_id>"
)
def remove_favorite(video_id):

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )


    favorite = Favorite.query.filter_by(
        user_id=session["user_id"],
        video_id=video_id
    ).first()


    if favorite:

        db.session.delete(favorite)

        db.session.commit()



    return redirect(
        request.referrer
    )
    
    # ==========================
# MA LISTE (FAVORIS)
# ==========================

@main.route("/ma-liste")
def my_list():

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )

    favorites = Favorite.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_list.html",
        favorites=favorites
    )
    # ==========================
# SUPPRIMER VIDEO CREATEUR
# ==========================

@main.route(
    "/delete-video/<int:video_id>",
    methods=["POST"]
)
def delete_video(video_id):

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )


    video = Video.query.get_or_404(
        video_id
    )


    # Vérifier propriétaire de la chaîne

    if video.channel.user_id != session["user_id"]:
        return "Accès refusé"



    # Supprimer fichier vidéo

    if video.file_path:

        file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            video.file_path.replace("uploads/", "")
        )

        if os.path.exists(file_path):
            os.remove(file_path)



    # Supprimer miniature

    if video.thumbnail:

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            video.thumbnail.replace("uploads/", "")
        )

        if os.path.exists(image_path):
            os.remove(image_path)



    db.session.delete(video)

    db.session.commit()



    return redirect(
        url_for("main.creator")
    )
    # ==========================
# SUPPRIMER CHAINE CREATEUR
# ==========================

@main.route(
    "/delete-channel/<int:channel_id>",
    methods=["POST"]
)
def delete_channel(channel_id):

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )


    channel = Channel.query.get_or_404(
        channel_id
    )


    # Vérifier propriétaire

    if channel.user_id != session["user_id"]:
        return "Accès refusé"


    # Supprimer les vidéos liées

    for video in channel.videos:

        db.session.delete(video)


    # Supprimer les lives liés

    for live in channel.lives:

        db.session.delete(live)


    # Supprimer la chaîne

    db.session.delete(channel)

    db.session.commit()


    return redirect(
        url_for("main.creator")
    )
def delete_channel(channel_id):

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )


    channel = Channel.query.get_or_404(
        channel_id
    )


    # Vérifier que la chaîne appartient au créateur

    if channel.user_id != session["user_id"]:
        return "Accès refusé"



    # Supprimer toutes les vidéos de la chaîne

    videos = Video.query.filter_by(
        channel_id=channel.id
    ).all()


    for video in videos:

        # Supprimer fichier vidéo

        if video.file_path:

            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                video.file_path.replace(
                    "uploads/",
                    ""
                )
            )


            if os.path.exists(file_path):
                os.remove(file_path)



        # Supprimer miniature

        if video.thumbnail:

            image_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                video.thumbnail.replace(
                    "uploads/",
                    ""
                )
            )


            if os.path.exists(image_path):
                os.remove(image_path)



        db.session.delete(video)



    # Supprimer la chaîne

    db.session.delete(channel)

    db.session.commit()



    return redirect(
        url_for("main.creator")
    )
   

from database import db
from datetime import datetime



# ==========================
# UTILISATEURS
# ==========================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )


    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )


    password = db.Column(
        db.String(200),
        nullable=False
    )


    role = db.Column(
        db.String(50),
        default="user"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    channels = db.relationship(
        "Channel",
        backref="owner",
        lazy=True
    )





# ==========================
# CHAÎNES TV
# ==========================

class Channel(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    name = db.Column(
        db.String(150),
        nullable=False
    )


    logo = db.Column(
        db.String(255)
    )


    cover = db.Column(
        db.String(255)
    )


    description = db.Column(
        db.Text
    )


    category = db.Column(
        db.String(100)
    )


    number = db.Column(
        db.Integer
    )


    show_logo = db.Column(
        db.Boolean,
        default=True
    )


    logo_position = db.Column(
        db.String(50),
        default="top-left"
    )


    videos = db.relationship(
        "Video",
        backref="channel",
        lazy=True
    )


    programs = db.relationship(
        "Program",
        backref="channel",
        lazy=True
    )


    lives = db.relationship(
        "LiveStream",
        backref="channel",
        lazy=True
    )





# ==========================
# VIDEOS / FILMS
# ==========================

class Video(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    likes = db.Column(
        db.Integer,
        default=0
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )


    title = db.Column(
        db.String(200),
        nullable=False
    )


    description = db.Column(
        db.Text
    )


    file_path = db.Column(
        db.String(500)
    )
    video_url = db.Column(
        db.String(500)
    )
 


    thumbnail = db.Column(
        db.String(255)
    )


    content_type = db.Column(
        db.String(50)
    )


    category = db.Column(
        db.String(100)
    )


    duration = db.Column(
        db.String(50)
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    views = db.Column(
        db.Integer,
        default=0
    )


    favorites = db.relationship(
        "Favorite",
        back_populates="video",
        lazy=True,
        cascade="all, delete-orphan"
    )
    # ==========================
# LIVE CAMERA / DIRECT
# ==========================

class LiveStream(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )


    title = db.Column(
        db.String(200)
    )


    stream_url = db.Column(
        db.String(500)
    )


    stream_type = db.Column(
        db.String(50),
        default="hls"
    )


    is_live = db.Column(
        db.Boolean,
        default=False
    )


    started_at = db.Column(
        db.DateTime
    )


    stopped_at = db.Column(
        db.DateTime
    )





# ==========================
# FAVORIS VIDEOS
# ==========================

class Favorite(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


    video_id = db.Column(
        db.Integer,
        db.ForeignKey("video.id"),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    video = db.relationship(
        "Video",
        back_populates="favorites"
    )





# ==========================
# HISTORIQUE DES VIDEOS
# ==========================

class History(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    video_id = db.Column(
        db.Integer,
        db.ForeignKey("video.id")
    )


    watched_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )





# ==========================
# PROGRAMMATION TV
# ==========================

class Program(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )


    video_id = db.Column(
        db.Integer,
        db.ForeignKey("video.id")
    )


    start_time = db.Column(
        db.DateTime
    )


    end_time = db.Column(
        db.DateTime
    )


    repeat = db.Column(
        db.Boolean,
        default=False
    )


    video = db.relationship(
        "Video"
    )





# ==========================
# ABONNEMENTS
# ==========================

class Subscription(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    # ==========================
# MESSAGES / CHAT
# ==========================

class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    content = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )





# ==========================
# PORTEFEUILLE CREATEUR
# ==========================

class CreatorWallet(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    balance = db.Column(
        db.Float,
        default=0
    )


    total_earnings = db.Column(
        db.Float,
        default=0
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )





# ==========================
# PAIEMENTS
# ==========================

class Payment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    amount = db.Column(
        db.Float
    )


    method = db.Column(
        db.String(50)
    )


    status = db.Column(
        db.String(50),
        default="pending"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )





# ==========================
# PROGRAMMES FAVORIS
# ==========================

class FavoriteChannel(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )





# ==========================
# COMMENTAIRES
# ==========================

class Comment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    video_id = db.Column(
        db.Integer,
        db.ForeignKey("video.id")
    )


    text = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )





# ==========================
# STREAM CAMERA WEBRTC
# ==========================

class CameraStream(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    channel_id = db.Column(
        db.Integer,
        db.ForeignKey("channel.id")
    )


    creator_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    title = db.Column(
        db.String(200),
        default="Live caméra"
    )


    is_active = db.Column(
        db.Boolean,
        default=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    channel = db.relationship(
        "Channel"
    )


    creator = db.relationship(
        "User"
    )





# ==========================
# LIKES VIDEOS
# ==========================

class VideoLike(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    video_id = db.Column(
        db.Integer,
        db.ForeignKey("video.id")
    )

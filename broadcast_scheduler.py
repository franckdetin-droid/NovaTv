from datetime import datetime

from models import (
    Program,
    Video
)





# ==========================
# PROGRAMME ACTUEL
# ==========================

def get_current_program(channel_id):


    now = datetime.utcnow()



    program = Program.query.filter(

        Program.channel_id == channel_id,

        Program.start_time <= now,

        Program.end_time >= now

    ).first()



    return program





# ==========================
# VIDEO EN COURS
# ==========================

def get_current_video(channel_id):


    program = get_current_program(
        channel_id
    )



    if program:


        video = Video.query.get(
            program.video_id
        )


        return video



    return None





# ==========================
# PROCHAIN PROGRAMME
# ==========================

def get_next_program(channel_id):


    now = datetime.utcnow()



    program = Program.query.filter(

        Program.channel_id == channel_id,

        Program.start_time > now

    ).order_by(

        Program.start_time.asc()

    ).first()



    return program





# ==========================
# VERIFICATION DIFFUSION
# ==========================

def is_channel_live(channel_id):


    program = get_current_program(
        channel_id
    )


    if program:

        return True



    return False
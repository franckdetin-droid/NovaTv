from app import app
from database import db
from sqlalchemy import text


tables = [
    "user",
    "channel",
    "video",
    "program",
    "favorite",
    "live_stream"
]


with app.app_context():

    with db.engine.connect() as conn:

        for table in tables:

            print("\n📌 Table :", table)

            result = conn.execute(
                text(
                    f"PRAGMA table_info({table})"
                )
            )

            for column in result:
                print(
                    " -",
                    column[1],
                    column[2]
                )
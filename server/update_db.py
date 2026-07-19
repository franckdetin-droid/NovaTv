from app import app
from database import db
from sqlalchemy import text


with app.app_context():

    with db.engine.connect() as conn:

        try:

            conn.execute(
                text(
                    "ALTER TABLE favorite ADD COLUMN created_at DATETIME"
                )
            )

            conn.commit()

            print("✅ Colonne created_at ajoutée dans favorite")


        except Exception as e:

            print("Erreur :", e)

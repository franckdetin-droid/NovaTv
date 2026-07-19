from app import app
from database import db
from sqlalchemy import text


def check_database():

    with app.app_context():

        print("🔍 Vérification de la base de données...")

        try:

            with db.engine.connect() as conn:

                tables = conn.execute(
                    text(
                        """
                        SELECT name 
                        FROM sqlite_master
                        WHERE type='table';
                        """
                    )
                ).fetchall()


                print("\n📋 Tables trouvées :")

                for table in tables:
                    print("✅", table[0])


            print("\n✅ Vérification terminée")


        except Exception as e:

            print(
                "❌ Erreur :",
                e
            )



if __name__ == "__main__":

    check_database()

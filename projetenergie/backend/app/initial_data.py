import os
import logging
import time
from sqlalchemy import text
from app.models.energy_system import Centrale
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.services.excel_service import excel_service
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if data is already imported
    if db.query(Centrale).first():
        logger.info("Data already imported, skipping initialization.")
        return
    
    data_dir = "/data"
    if not os.path.exists(data_dir):
        logger.warning(f"Répertoire {data_dir} non trouvé.")
        return

    import_order = [
        ("centrale", ["centrales.xlsx", "centrale.xlsx"]),
        ("production", ["production.xlsx", "production_mensuelle.xlsx"]),
        ("rendement", ["rendement.xlsx", "rendements.xlsx"]),
        ("recap", ["recap.xlsx", "recap_energie.xlsx"])
    ]

    for table_type, filenames in import_order:
        for filename in filenames:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                logger.info(f"Importation de {filename}...")
                try:
                    result = excel_service.import_excel(file_path, table_type, db)
                    logger.info(f"Succès: {result['rows']} lignes importées.")
                except Exception as e:
                    logger.error(f"Erreur sur {filename}: {e}")

def main() -> None:
    logger.info("Attente de la base de données...")
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            db = SessionLocal()
            # Try a simple query to check connection
            db.execute(text("SELECT 1"))
            logger.info("Connexion à la base de données réussie.")
            init_db(db)
            db.close()
            break
        except OperationalError:
            retry_count += 1
            logger.info(f"Base de données non prête (essai {retry_count}/{max_retries})...")
            time.sleep(5)
    else:
        logger.error("Impossible de se connecter à la base de données après plusieurs essais.")

if __name__ == "__main__":
    main()

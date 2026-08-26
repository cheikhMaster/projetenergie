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

# Mapping table_type -> mots-clés à chercher dans le nom de fichier (en minuscules, sans accents/underscores)
# On utilise "startswith" sur le nom normalisé pour matcher les fichiers avec suffixes de date
# (ex: "Rendement_01012023_31032023.xlsx" -> "rendement...")
IMPORT_ORDER = [
    ("type_reseau", ["typereseauproducteur"]),
    ("centrale", ["centrale"]),
    ("production", ["productionmensuelle", "production"]),
    ("rendement", ["rendement"]),
    ("recap", ["recapenergie", "recap"]),
    ("groupe", ["groupe"]),
    ("deplacement_groupe", ["deplacementgroupe"]),
]


def _normalize(name: str) -> str:
    """Normalise un nom de fichier pour la comparaison : minuscules, sans extension, sans underscores/espaces/accents basiques."""
    base = os.path.splitext(name)[0].lower()
    replacements = {
        "é": "e", "è": "e", "ê": "e", "à": "a", "ô": "o", "î": "i", "ç": "c",
        "_": "", "-": "", " ": "",
    }
    for old, new in replacements.items():
        base = base.replace(old, new)
    return base


def _find_matching_file(data_dir: str, keywords: list) -> str:
    """Cherche dans data_dir un fichier .xlsx dont le nom normalisé commence par un des mots-clés."""
    try:
        files = os.listdir(data_dir)
    except OSError:
        return None

    for filename in files:
        if not filename.lower().endswith(".xlsx"):
            continue
        normalized = _normalize(filename)
        for keyword in keywords:
            if normalized.startswith(keyword):
                return filename
    return None


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

    all_files = os.listdir(data_dir)
    logger.info(f"Fichiers trouvés dans {data_dir}: {all_files}")

    matched_filenames = set()

    for table_type, keywords in IMPORT_ORDER:
        filename = _find_matching_file(data_dir, keywords)
        if not filename:
            logger.warning(
                f"Aucun fichier trouvé pour le type '{table_type}' "
                f"(mots-clés cherchés: {keywords})."
            )
            continue

        file_path = os.path.join(data_dir, filename)
        logger.info(f"Importation de '{filename}' -> table '{table_type}'...")
        try:
            result = excel_service.import_excel(file_path, table_type, db)
            logger.info(f"Succès: {result['rows_inserted']}/{result['rows_read']} lignes insérées/lues depuis '{filename}'.")
            matched_filenames.add(filename)
        except Exception as e:
            logger.error(f"Erreur lors de l'import de '{filename}': {e}")

    # Fichiers présents dans /data mais non importés (pas encore de table_type correspondant)
    unmatched = [f for f in all_files if f.lower().endswith(".xlsx") and f not in matched_filenames]
    if unmatched:
        logger.warning(
            f"Fichiers Excel présents mais non importés (pas de mapping table_type défini): {unmatched}"
        )


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
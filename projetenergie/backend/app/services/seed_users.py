import logging
from sqlalchemy.orm import Session
from app.models.user import Role, Utilisateur
from app.core.security_password import hash_password

logger = logging.getLogger(__name__)


def seed_users_and_roles(db: Session) -> None:
    """Crée le rôle 'admin' et un premier utilisateur admin si nécessaire.
    Idempotent : sans effet si les données existent déjà (peut être appelé
    à chaque démarrage sans risque de doublon)."""

    # 1. Créer le rôle "admin" s'il n'existe pas encore
    admin_role = db.query(Role).filter(Role.nom_role == "admin").first()
    if not admin_role:
        admin_role = Role(
            nom_role="admin",
            description="Accès complet : gestion des utilisateurs et des données"
        )
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)  # récupère l'id généré par la base (auto-incrément)
        logger.info("Rôle 'admin' créé.")

    # 2. Créer un utilisateur admin par défaut s'il n'y a encore aucun utilisateur
    if db.query(Utilisateur).first():
        logger.info("Des utilisateurs existent déjà, pas de création par défaut.")
        return

    default_admin = Utilisateur(
        nom="Admin",
        prenom="Smart Senelec",
        email="admin@senelec.sn",  # <- changez ceci selon vos besoins
        mot_de_passe_hash=hash_password("admin123"),  # <- changez ce mot de passe !
        ldap=False,
        role_id=admin_role.id,
    )
    db.add(default_admin)
    db.commit()
    logger.info("Utilisateur admin par défaut créé (email: admin@senelec.sn / mdp: admin123).")
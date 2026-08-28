from passlib.context import CryptContext

# CryptContext gère l'algorithme de hachage. On utilise bcrypt,
# un standard de l'industrie, conçu pour être volontairement LENT
# (résistant aux attaques par force brute qui testent des millions
# de mots de passe par seconde).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Transforme un mot de passe en clair en une empreinte irréversible.
    Utilisé UNE FOIS à la création d'un compte."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond à un hash stocké.
    Utilisé À CHAQUE connexion. Ne "dé-hache" jamais rien : bcrypt
    re-hache le mot de passe saisi et compare les deux empreintes."""
    return pwd_context.verify(plain_password, hashed_password)
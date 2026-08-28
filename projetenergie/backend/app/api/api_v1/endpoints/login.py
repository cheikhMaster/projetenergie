from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import Utilisateur
from app.core.security_password import verify_password

router = APIRouter()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),  # <- injecte une session de base de données
):
    # 1. On cherche l'utilisateur par email (ou par "nom" si vous préférez
    #    vous connecter avec un identifiant plutôt qu'un email - à adapter).
    #    NB: OAuth2PasswordRequestForm attend un champ "username" dans le
    #    formulaire, on y met l'email de l'utilisateur.
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()

    # 2. On vérifie que l'utilisateur existe ET que le mot de passe correspond.
    #    On regroupe les deux vérifications dans un seul "if" pour ne PAS
    #    révéler si c'est l'email ou le mot de passe qui est faux
    #    (bonne pratique de sécurité : moins d'info pour un attaquant).
    if not user or not verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(status_code=400, detail="Identifiants incorrects")

    # 3. On construit le token avec le rôle réel de l'utilisateur
    #    (récupéré via la relation user.role grâce au relationship() défini
    #    dans le modèle - SQLAlchemy va chercher la ligne correspondante
    #    dans la table "roles" automatiquement).
    to_encode = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role.nom_role,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    encoded_jwt = jwt.encode(to_encode, "a_secret_key", algorithm="HS256")

    return {"access_token": encoded_jwt, "token_type": "bearer"}
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.core.config import settings
import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_keycloak_public_key():
    try:
        url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        return f"-----BEGIN PUBLIC KEY-----\n{response.json()['public_key']}\n-----END PUBLIC KEY-----"
    except Exception:
        return None

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        public_key = get_keycloak_public_key()
        if not public_key:
            raise HTTPException(status_code=503, detail="Auth service not ready")
        
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"], 
            audience=["account", settings.KEYCLOAK_CLIENT_ID]
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: dict = Depends(verify_token)):
        user_roles = token_data.get("realm_access", {}).get("roles", [])
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions"
            )
        return True

# Predefined role checkers
admin_only = RoleChecker(["admin"])
analyst_only = RoleChecker(["admin", "analyste"])
operator_only = RoleChecker(["admin", "operateur"])
manager_only = RoleChecker(["admin", "manager"])

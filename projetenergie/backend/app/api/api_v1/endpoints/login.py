from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app.core.config import settings
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "admin123":
        to_encode = {
            "sub": form_data.username,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "realm_access": {
                "roles": ["admin", "analyste", "manager", "operateur"]
            }
        }
        # For simplicity, using a hardcoded secret and HS256. 
        # This should be replaced with a proper key and RS256 to match the verification.
        encoded_jwt = jwt.encode(to_encode, "a_secret_key", algorithm="HS256")
        return {"access_token": encoded_jwt, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

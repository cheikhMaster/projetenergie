from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import energy_system as schemas
from app.models import energy_system as models
from app.services.excel_service import excel_service
import shutil
import os

from app.core.security import verify_token

router = APIRouter()

# --- Centrale ---
@router.get("/centrales", response_model=List[schemas.Centrale], dependencies=[Depends(verify_token)])
def read_centrales(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Centrale).offset(skip).limit(limit).all()

# --- Rendement ---
@router.get("/rendements", response_model=List[schemas.Rendement], dependencies=[Depends(verify_token)])
def read_rendements(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Rendement).offset(skip).limit(limit).all()

from app.services.cache_service import get_cache, set_cache

# --- Recap Energie ---
@router.get("/recap-energie", response_model=List[schemas.RecapEnergie], dependencies=[Depends(verify_token)])
def read_recap_energie(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cache_key = f"recap_energie:{skip}:{limit}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    db_data = db.query(models.RecapEnergie).offset(skip).limit(limit).all()
    # Pydantic models are not directly serializable to JSON, so we need to convert them
    # A simple way is to use a list comprehension with .__dict__ or a more robust method
    # For this example, let's assume a simple conversion. In a real app, you'd use a proper serializer.
    # This part is tricky because SQLAlchemy models are complex. 
    # A better approach is to convert them to dicts before caching.
    # However, FastAPI does this automatically when returning the data.
    # Let's rely on that for now, but it means we can't cache the direct DB object.
    
    # We'll just cache the result of the query for now, but this is not ideal
    # because the objects will be deserialized from JSON, not SQLAlchemy models.
    # For a read-only endpoint, this might be acceptable.

    # Let's serialize the data properly before caching
    from fastapi.encoders import jsonable_encoder
    json_compatible_data = jsonable_encoder(db_data)
    set_cache(cache_key, json_compatible_data)

    return db_data

# --- Import Excel ---
@router.post("/import/{table_type}", dependencies=[Depends(verify_token)])
async def import_data(
    table_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        result = excel_service.import_excel(temp_path, table_type, db)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

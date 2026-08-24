from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import energy_system as schemas
from app.models import energy_system as models
from app.services.excel_service import excel_service
import shutil
import os

from app.core.security import admin_only, analyst_only, manager_only

router = APIRouter()

# --- Centrale ---
@router.get("/centrales", response_model=List[schemas.Centrale], dependencies=[Depends(analyst_only)])
def read_centrales(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Centrale).offset(skip).limit(limit).all()

# --- Rendement ---
@router.get("/rendements", response_model=List[schemas.Rendement], dependencies=[Depends(manager_only)])
def read_rendements(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Rendement).offset(skip).limit(limit).all()

# --- Recap Energie ---
@router.get("/recap-energie", response_model=List[schemas.RecapEnergie], dependencies=[Depends(analyst_only)])
def read_recap_energie(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.RecapEnergie).offset(skip).limit(limit).all()

# --- Import Excel ---
@router.post("/import/{table_type}", dependencies=[Depends(admin_only)])
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

from typing import List, Callable, Any
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import energy_system as schemas
from app.models import energy_system as models
from app.services.excel_service import excel_service
from app.services.cache_service import get_cache, set_cache
import shutil
import os

from app.core.security import verify_token

router = APIRouter()

CACHE_TTL = 3600  # secondes


def _cached_list(cache_key: str, query_fn: Callable[[], Any], ttl: int = CACHE_TTL):
    """
    Sert une liste depuis Redis si présente, sinon exécute query_fn(),
    met le résultat en cache, puis le retourne.
    query_fn doit retourner une liste d'objets SQLAlchemy.
    """
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    db_data = query_fn()
    json_compatible_data = jsonable_encoder(db_data)
    set_cache(cache_key, json_compatible_data, ex=ttl)
    return db_data


# --- Centrale ---
@router.get("/centrales", response_model=List[schemas.Centrale], dependencies=[Depends(verify_token)])
def read_centrales(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cache_key = f"centrales:{skip}:{limit}"
    return _cached_list(
        cache_key,
        lambda: db.query(models.Centrale).order_by(models.Centrale.id).offset(skip).limit(limit).all()
    )

# --- Rendement ---
@router.get("/rendements", response_model=List[schemas.Rendement], dependencies=[Depends(verify_token)])
def read_rendements(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cache_key = f"rendements:{skip}:{limit}"
    return _cached_list(
        cache_key,
        lambda: db.query(models.Rendement).order_by(models.Rendement.id).offset(skip).limit(limit).all()
    )

# --- Recap Energie ---
@router.get("/recap-energie", response_model=List[schemas.RecapEnergie], dependencies=[Depends(verify_token)])
def read_recap_energie(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cache_key = f"recap_energie:{skip}:{limit}"
    return _cached_list(
        cache_key,
        lambda: db.query(models.RecapEnergie).order_by(models.RecapEnergie.id).offset(skip).limit(limit).all()
    )

# --- Production Mensuelle ---
@router.get("/production", response_model=List[schemas.ProductionMensuelle], dependencies=[Depends(verify_token)])
def read_production(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    centrale_id: int | None = None,
):
    cache_key = f"production:{skip}:{limit}:{centrale_id}"

    def query_fn():
        query = db.query(models.ProductionMensuelle)
        if centrale_id is not None:
            query = query.filter(models.ProductionMensuelle.centrale_id == centrale_id)
        return query.order_by(models.ProductionMensuelle.id).offset(skip).limit(limit).all()

    return _cached_list(cache_key, query_fn)

# --- Groupes ---
@router.get("/groupes", response_model=List[schemas.Groupe], dependencies=[Depends(verify_token)])
def read_groupes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    centrale_id: int | None = None,
):
    cache_key = f"groupes:{skip}:{limit}:{centrale_id}"

    def query_fn():
        query = db.query(models.Groupe)
        if centrale_id is not None:
            query = query.filter(models.Groupe.centrale_id == centrale_id)
        return query.order_by(models.Groupe.id).offset(skip).limit(limit).all()

    return _cached_list(cache_key, query_fn)

# --- Deplacement Groupes ---
@router.get("/deplacement-groupes", response_model=List[schemas.DeplacementGroupe], dependencies=[Depends(verify_token)])
def read_deplacement_groupes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    groupe_id: int | None = None,
):
    cache_key = f"deplacement_groupes:{skip}:{limit}:{groupe_id}"

    def query_fn():
        query = db.query(models.DeplacementGroupe)
        if groupe_id is not None:
            query = query.filter(models.DeplacementGroupe.groupe_id == groupe_id)
        return query.order_by(models.DeplacementGroupe.id).offset(skip).limit(limit).all()

    return _cached_list(cache_key, query_fn)

# --- Type Reseau Producteur ---
@router.get("/type-reseau-producteurs", response_model=List[schemas.TypeReseauProducteur], dependencies=[Depends(verify_token)])
def read_type_reseau_producteurs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    cache_key = f"type_reseau_producteurs:{skip}:{limit}"
    return _cached_list(
        cache_key,
        lambda: db.query(models.TypeReseauProducteur).order_by(models.TypeReseauProducteur.id).offset(skip).limit(limit).all()
    )

# --- Import Excel ---
@router.post("/import/{table_type}", dependencies=[Depends(verify_token)])
async def import_data(
    table_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = excel_service.import_excel(temp_path, table_type, db)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
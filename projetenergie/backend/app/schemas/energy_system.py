from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# --- Centrale ---
class CentraleBase(BaseModel):
    nom: str
    type_centrale: str
    centrale_mere: Optional[str] = None
    reseau_producteur: str
    lieu: str
    parc: str
    type_ipp: Optional[str] = None
    service_production: str

class CentraleCreate(CentraleBase):
    pass

class Centrale(CentraleBase):
    id: int
    class Config:
        from_attributes = True

# --- Production Mensuelle ---
class ProductionMensuelleBase(BaseModel):
    centrale_id: int
    reseau_producteur: str
    consommation_auxiliaire: float
    date: date
    valeur_production: float

class ProductionMensuelleCreate(ProductionMensuelleBase):
    pass

class ProductionMensuelle(ProductionMensuelleBase):
    id: int
    class Config:
        from_attributes = True

# --- Rendement ---
class RendementBase(BaseModel):
    date: date
    vente_woyofal: float
    vente_classique: float
    production_senelec: float
    production_ipp: float
    energie_hta: float
    energie_htb: float
    producteur_hta: float
    producteur_htb: float
    client_hta: float
    client_htb: float
    rendement_global: float
    rendement_hta: float
    rendement_htb: float

class RendementCreate(RendementBase):
    pass

class Rendement(RendementBase):
    id: int
    class Config:
        from_attributes = True

# --- Recap Energie ---
class RecapEnergieBase(BaseModel):
    poste_source: str
    depart_30kv: str
    transformateur_htb_hta: str
    sccn_scada: float
    dms: float
    desa: float
    taux_energie: float
    source_donnees: str
    energie_validee: float
    date: date

class RecapEnergieCreate(RecapEnergieBase):
    pass

class RecapEnergie(RecapEnergieBase):
    id: int
    class Config:
        from_attributes = True

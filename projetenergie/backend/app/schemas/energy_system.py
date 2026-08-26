from datetime import date
from typing import Optional
from pydantic import BaseModel


class OrmBase(BaseModel):
    class Config:
        from_attributes = True  # pydantic v2 (remplace orm_mode)


# --- Centrale ---
class Centrale(OrmBase):
    id: int
    id_centrale_externe: Optional[int] = None
    nom: str
    type_centrale: Optional[str] = None
    centrale_mere: Optional[str] = None
    reseau_producteur: Optional[str] = None
    lieu: Optional[str] = None
    parc: Optional[str] = None
    type_ipp: Optional[str] = None
    service_production: Optional[str] = None
    senelec_fournit_comb_lub: Optional[bool] = None
    centrale_declassee: Optional[bool] = None


# --- Production Mensuelle ---
class ProductionMensuelle(OrmBase):
    id: int
    centrale_id: int
    reseau_producteur: Optional[str] = None
    consommation_auxiliaire: Optional[float] = None
    date: date
    valeur_production: Optional[float] = None


# --- Rendement ---
class Rendement(OrmBase):
    id: int
    id_rendement_externe: Optional[int] = None
    date: date
    vente_woyofal: Optional[float] = None
    vente_classique: Optional[float] = None
    production_senelec: Optional[float] = None
    production_ipp: Optional[float] = None
    energie_hta: Optional[float] = None
    energie_htb: Optional[float] = None
    producteur_hta: Optional[float] = None
    producteur_htb: Optional[float] = None
    client_hta: Optional[float] = None
    client_htb: Optional[float] = None
    rendement_global: Optional[float] = None
    rendement_hta: Optional[float] = None
    rendement_htb: Optional[float] = None


# --- Recap Energie ---
class RecapEnergie(OrmBase):
    id: int
    id_recap_externe: Optional[int] = None
    poste_source: Optional[str] = None
    depart_30kv: Optional[str] = None
    transformateur_htb_hta: Optional[str] = None
    sccn_scada: Optional[float] = None
    dms: Optional[float] = None
    desa: Optional[float] = None
    taux_energie: Optional[float] = None
    source_donnees: Optional[str] = None
    energie_validee: Optional[float] = None
    date: date


# --- Groupe ---
class Groupe(OrmBase):
    id: int
    id_groupe_externe: Optional[int] = None
    nom: Optional[str] = None
    centrale_id: Optional[int] = None
    moteur: Optional[str] = None
    alternateur: Optional[str] = None
    type_production: Optional[str] = None
    puissance_nominale: Optional[float] = None
    compteur_energie: Optional[str] = None


# --- Deplacement Groupe ---
class DeplacementGroupe(OrmBase):
    id: int
    groupe_id: int
    centrale_source_id: Optional[int] = None
    date_debut: date
    date_fin: Optional[date] = None


# --- Type Reseau Producteur ---
class TypeReseauProducteur(OrmBase):
    id: int
    type_reseau: Optional[str] = None
    producteur: Optional[str] = None
    libelle: Optional[str] = None
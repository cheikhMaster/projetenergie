import pandas as pd
from sqlalchemy.orm import Session
from app.models.energy_system import (
    Centrale, ProductionMensuelle, Rendement, RecapEnergie,
    TypeReseauProducteur, Groupe, DeplacementGroupe,
)
import os


def _clean(value):
    """Convertit les NaN pandas en None pour éviter des valeurs invalides en base."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _to_str(value):
    v = _clean(value)
    return str(v) if v is not None else None


def _to_int(value):
    v = _clean(value)
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


class ExcelService:
    # --- Centrale ---
    @staticmethod
    def process_centrales(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        seen_ids = set()  # évite les doublons DANS le même fichier (pas encore committés en base)
        for _, row in df.iterrows():
            id_externe = _to_int(row.get('IDCentrale'))
            nom = _clean(row.get('NomCentrale'))
            if id_externe is None or nom is None:
                continue
            if id_externe in seen_ids:
                continue
            seen_ids.add(id_externe)

            if db.query(Centrale).filter(Centrale.id_centrale_externe == id_externe).first():
                continue

            obj = Centrale(
                id_centrale_externe=id_externe,
                nom=str(nom),
                type_centrale=_to_str(row.get('IDTypeCentrale')),
                centrale_mere=_to_str(row.get('IDCentraleMere')),
                reseau_producteur=_to_str(row.get('IDTypeReseauProducteur')) or _to_str(row.get('IDTypeReseau')),
                senelec_fournit_comb_lub=bool(_clean(row.get('SenlecFournitCombLub'))) if _clean(row.get('SenlecFournitCombLub')) is not None else None,
                centrale_declassee=bool(_clean(row.get('CentraleDeclassee'))) if _clean(row.get('CentraleDeclassee')) is not None else None,
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Production mensuelle ---
    @staticmethod
    def process_production(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        for _, row in df.iterrows():
            id_centrale_externe = _to_int(row.get('ID_Centrale'))
            if id_centrale_externe is None:
                continue

            centrale = db.query(Centrale).filter(Centrale.id_centrale_externe == id_centrale_externe).first()
            if not centrale:
                continue

            obj = ProductionMensuelle(
                centrale_id=centrale.id,
                date=_clean(row.get('Date_FinDuMois')),
                valeur_production=_clean(row.get('Production_Centrale')),
                consommation_auxiliaire=_clean(row.get('ConsAux')),
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Rendement ---
    @staticmethod
    def process_rendement(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        seen_ids = set()
        for _, row in df.iterrows():
            id_externe = _to_int(row.get('ID_Rendement'))
            date_val = _clean(row.get('Date_Rendement'))
            if id_externe is None or date_val is None:
                continue
            if id_externe in seen_ids:
                continue
            seen_ids.add(id_externe)

            if db.query(Rendement).filter(Rendement.id_rendement_externe == id_externe).first():
                continue

            obj = Rendement(
                id_rendement_externe=id_externe,
                date=date_val,
                vente_woyofal=_clean(row.get('Vente_Woyofal')),
                vente_classique=_clean(row.get('Vente_Energie_Classique_MT_BT')),
                production_senelec=_clean(row.get('Production_Senelec')),
                production_ipp=_clean(row.get('Production_IPP')),
                energie_hta=_clean(row.get('Energie_ReseauHTA')),
                energie_htb=_clean(row.get('Energie_ReseauHTB')),
                producteur_hta=_clean(row.get('Producteur_HTA')),
                producteur_htb=_clean(row.get('Producteur_HTB')),
                client_hta=_clean(row.get('Client_HTA')),
                client_htb=_clean(row.get('Client_HTB')),
                rendement_global=_clean(row.get('Rendement_Global')),
                rendement_hta=_clean(row.get('Rendement_HTA')),
                rendement_htb=_clean(row.get('Rendement_HTB')),
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Recap Energie ---
    # NOTE: le fichier réel contient plusieurs colonnes similaires (TRANSFOHTBHTA,
    # TRANSFOHTBHTADMS, TRANSFOHTBHTADESA...) alors que le modèle n'a qu'un seul champ.
    # Mapping fait au mieux - à valider/affiner une fois les données visibles en base.
    @staticmethod
    def process_recap_energie(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        seen_ids = set()
        for _, row in df.iterrows():
            id_externe = _to_int(row.get('IDRecapEnergie'))
            date_val = _clean(row.get('Date_Debut'))
            if id_externe is None or date_val is None:
                continue
            if id_externe in seen_ids:
                continue
            seen_ids.add(id_externe)

            if db.query(RecapEnergie).filter(RecapEnergie.id_recap_externe == id_externe).first():
                continue

            obj = RecapEnergie(
                id_recap_externe=id_externe,
                poste_source=_to_str(row.get('Poste Source')),
                depart_30kv=_to_str(row.get('DEPART30KV')),
                transformateur_htb_hta=_to_str(row.get('TRANSFOHTBHTA')),
                sccn_scada=_clean(row.get('SCCNSCADA')),
                dms=_clean(row.get('DEPART30KVDMS')),
                desa=_clean(row.get('TRANSFOHTBHTADESA')),
                taux_energie=_clean(row.get('TAUXDEPART30KV')),
                source_donnees=_to_str(row.get('SOURCEDONNEES')),
                energie_validee=_clean(row.get('EnergieValidee')),
                date=date_val,
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Type Reseau Producteur ---
    @staticmethod
    def process_type_reseau_producteur(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        for _, row in df.iterrows():
            libelle = _clean(row.get('LibelleTypeReseauProducteur'))
            if libelle is None:
                continue

            if db.query(TypeReseauProducteur).filter(TypeReseauProducteur.libelle == libelle).first():
                continue

            obj = TypeReseauProducteur(
                type_reseau=_to_str(row.get('IDTypeReseau')),
                producteur=_to_str(row.get('IDProducteur')),
                libelle=str(libelle),
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Groupe ---
    @staticmethod
    def process_groupe(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        seen_ids = set()
        for _, row in df.iterrows():
            id_groupe_externe = _to_int(row.get('IDGroupe'))
            if id_groupe_externe is None:
                continue
            if id_groupe_externe in seen_ids:
                continue
            seen_ids.add(id_groupe_externe)

            if db.query(Groupe).filter(Groupe.id_groupe_externe == id_groupe_externe).first():
                continue

            id_centrale_externe = _to_int(row.get('IDCentrale'))
            centrale = None
            if id_centrale_externe is not None:
                centrale = db.query(Centrale).filter(Centrale.id_centrale_externe == id_centrale_externe).first()

            obj = Groupe(
                id_groupe_externe=id_groupe_externe,
                nom=_to_str(row.get('NomGroupe')),
                centrale_id=centrale.id if centrale else None,
                moteur=_to_str(row.get('IDMoteur')),
                alternateur=_to_str(row.get('IDAlternateur')),
                type_production=_to_str(row.get('IDTypeDeProduction')),
                puissance_nominale=_clean(row.get('PuissanceNominale')),
                compteur_energie=_to_str(row.get('DernierIndexEnergie')),
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    # --- Deplacement Groupe ---
    @staticmethod
    def process_deplacement_groupe(df: pd.DataFrame, db: Session) -> int:
        inserted = 0
        for _, row in df.iterrows():
            date_debut = _clean(row.get('DateDebut'))
            id_groupe_externe = _to_int(row.get('IDGroupe'))
            if date_debut is None or id_groupe_externe is None:
                continue

            groupe = db.query(Groupe).filter(Groupe.id_groupe_externe == id_groupe_externe).first()
            if not groupe:
                continue

            id_centrale_externe = _to_int(row.get('IDCentrale'))
            centrale = None
            if id_centrale_externe is not None:
                centrale = db.query(Centrale).filter(Centrale.id_centrale_externe == id_centrale_externe).first()

            obj = DeplacementGroupe(
                groupe_id=groupe.id,
                centrale_source_id=centrale.id if centrale else None,
                date_debut=date_debut,
                date_fin=_clean(row.get('DateFin')),
            )
            db.add(obj)
            inserted += 1
        db.commit()
        return inserted

    @classmethod
    def import_excel(cls, file_path: str, table_type: str, db: Session):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")

        df = pd.read_excel(file_path)
        df.dropna(how='all', inplace=True)

        processors = {
            "centrale": cls.process_centrales,
            "production": cls.process_production,
            "rendement": cls.process_rendement,
            "recap": cls.process_recap_energie,
            "type_reseau": cls.process_type_reseau_producteur,
            "groupe": cls.process_groupe,
            "deplacement_groupe": cls.process_deplacement_groupe,
        }

        processor = processors.get(table_type)
        if not processor:
            raise ValueError(f"Type de table inconnu: {table_type}")

        inserted = processor(df, db)
        return {"status": "success", "rows_read": len(df), "rows_inserted": inserted}


excel_service = ExcelService()
import pandas as pd
from sqlalchemy.orm import Session
from app.models.energy_system import Centrale, ProductionMensuelle, Rendement, RecapEnergie
import os
from datetime import datetime

class ExcelService:
    @staticmethod
    def process_centrales(df: pd.DataFrame, db: Session):
        for _, row in df.iterrows():
            nom = row.get('Centrale')
            if nom:
                centrale = db.query(Centrale).filter(Centrale.nom == nom).first()
                if not centrale:
                    obj = Centrale(
                        nom=nom,
                        type_centrale=row.get('Type de centrale'),
                        centrale_mere=row.get('Centrale mère'),
                        reseau_producteur=row.get('Réseau producteur'),
                        lieu=row.get('Lieu'),
                        parc=row.get('Parc'),
                        type_ipp=row.get('Type de centrale IPP'),
                        service_production=row.get('Service de production')
                    )
                    db.add(obj)
        db.commit()

    @staticmethod
    def process_production(df: pd.DataFrame, db: Session):
        for _, row in df.iterrows():
            # Find centrale by name first
            centrale = db.query(Centrale).filter(Centrale.nom == row.get('Centrale')).first()
            if centrale:
                obj = ProductionMensuelle(
                    centrale_id=centrale.id,
                    reseau_producteur=row.get('Réseau producteur'),
                    consommation_auxiliaire=row.get('Consommation auxiliaire'),
                    date=row.get('Date'),
                    valeur_production=row.get('Production mensuelle')
                )
                db.add(obj)
        db.commit()

    @staticmethod
    def process_rendement(df: pd.DataFrame, db: Session):
        for _, row in df.iterrows():
            obj = Rendement(
                date=row.get('Date'),
                vente_woyofal=row.get('Vente Woyofal'),
                vente_classique=row.get('Vente énergie classique'),
                production_senelec=row.get('Production SENELEC'),
                production_ipp=row.get('Production IPP'),
                energie_hta=row.get('Énergie HTA'),
                energie_htb=row.get('Énergie HTB'),
                producteur_hta=row.get('Producteur HTA'),
                producteur_htb=row.get('Producteur HTB'),
                client_hta=row.get('Client HTA'),
                client_htb=row.get('Client HTB'),
                rendement_global=row.get('Rendement global'),
                rendement_hta=row.get('Rendement HTA'),
                rendement_htb=row.get('Rendement HTB')
            )
            db.add(obj)
        db.commit()

    @staticmethod
    def process_recap_energie(df: pd.DataFrame, db: Session):
        for _, row in df.iterrows():
            obj = RecapEnergie(
                poste_source=row.get('Poste source'),
                depart_30kv=row.get('Départ 30 kV'),
                transformateur_htb_hta=row.get('Transformateur HTB/HTA'),
                sccn_scada=row.get('SCCN SCADA'),
                dms=row.get('DMS'),
                desa=row.get('DESA'),
                taux_energie=row.get('Taux énergie'),
                source_donnees=row.get('Source de données'),
                energie_validee=row.get('Énergie validée'),
                date=row.get('Date')
            )
            db.add(obj)
        db.commit()

    @classmethod
    def import_excel(cls, file_path: str, table_type: str, db: Session):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        df = pd.read_excel(file_path)
        df.dropna(how='all', inplace=True)
        
        if table_type == "centrale":
            cls.process_centrales(df, db)
        elif table_type == "production":
            cls.process_production(df, db)
        elif table_type == "rendement":
            cls.process_rendement(df, db)
        elif table_type == "recap":
            cls.process_recap_energie(df, db)
        else:
            raise ValueError(f"Type de table inconnu: {table_type}")
        
        return {"status": "success", "rows": len(df)}

excel_service = ExcelService()

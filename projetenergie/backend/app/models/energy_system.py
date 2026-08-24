from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class Centrale(Base):
    __tablename__ = "centrales"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), unique=True, index=True)
    type_centrale = Column(String(100))
    centrale_mere = Column(String(255), nullable=True)
    reseau_producteur = Column(String(100))
    lieu = Column(String(255))
    parc = Column(String(100))
    type_ipp = Column(String(100), nullable=True)
    service_production = Column(String(100))
    
    groupes = relationship("Groupe", back_populates="centrale")
    productions = relationship("ProductionMensuelle", back_populates="centrale")

class TypeReseauProducteur(Base):
    __tablename__ = "type_reseau_producteurs"
    id = Column(Integer, primary_key=True, index=True)
    type_reseau = Column(String(100))
    producteur = Column(String(100))
    libelle = Column(String(255))

class ProductionMensuelle(Base):
    __tablename__ = "production_mensuelle"
    id = Column(Integer, primary_key=True, index=True)
    centrale_id = Column(Integer, ForeignKey("centrales.id"))
    reseau_producteur = Column(String(100))
    consommation_auxiliaire = Column(Float)
    date = Column(Date)
    valeur_production = Column(Float)
    
    centrale = relationship("Centrale", back_populates="productions")

class Groupe(Base):
    __tablename__ = "groupes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    centrale_id = Column(Integer, ForeignKey("centrales.id"))
    moteur = Column(String(100))
    alternateur = Column(String(100))
    type_production = Column(String(100))
    puissance_nominale = Column(Float)
    compteur_energie = Column(String(100))
    
    centrale = relationship("Centrale", back_populates="groupes")
    deplacements = relationship("DeplacementGroupe", back_populates="groupe")

class DeplacementGroupe(Base):
    __tablename__ = "deplacement_groupes"
    id = Column(Integer, primary_key=True, index=True)
    groupe_id = Column(Integer, ForeignKey("groupes.id"))
    centrale_source_id = Column(Integer, ForeignKey("centrales.id"))
    date_debut = Column(Date)
    date_fin = Column(Date, nullable=True)
    
    groupe = relationship("Groupe", back_populates="deplacements")

class Rendement(Base):
    __tablename__ = "rendements"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    vente_woyofal = Column(Float)
    vente_classique = Column(Float)
    production_senelec = Column(Float)
    production_ipp = Column(Float)
    energie_hta = Column(Float)
    energie_htb = Column(Float)
    producteur_hta = Column(Float)
    producteur_htb = Column(Float)
    client_hta = Column(Float)
    client_htb = Column(Float)
    rendement_global = Column(Float)
    rendement_hta = Column(Float)
    rendement_htb = Column(Float)

class RecapEnergie(Base):
    __tablename__ = "recap_energie"
    id = Column(Integer, primary_key=True, index=True)
    poste_source = Column(String(255))
    depart_30kv = Column(String(100))
    transformateur_htb_hta = Column(String(100))
    sccn_scada = Column(Float)
    dms = Column(Float)
    desa = Column(Float)
    taux_energie = Column(Float)
    source_donnees = Column(String(100))
    energie_validee = Column(Float)
    date = Column(Date)

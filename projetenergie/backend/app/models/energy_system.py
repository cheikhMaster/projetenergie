from sqlalchemy import Column, Integer, BigInteger, Float, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Centrale(Base):
    __tablename__ = "centrales"
    id = Column(Integer, primary_key=True, index=True)
    id_centrale_externe = Column(BigInteger, unique=True, index=True, nullable=True)  # IDCentrale du fichier Excel
    nom = Column(String(255), index=True)  # pas unique: plusieurs centrales peuvent partager un nom
    type_centrale = Column(String(100), nullable=True)
    centrale_mere = Column(String(255), nullable=True)
    reseau_producteur = Column(String(100), nullable=True)
    lieu = Column(String(255), nullable=True)
    parc = Column(String(100), nullable=True)
    type_ipp = Column(String(100), nullable=True)
    service_production = Column(String(100), nullable=True)
    senelec_fournit_comb_lub = Column(Boolean, nullable=True)
    centrale_declassee = Column(Boolean, nullable=True)

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
    reseau_producteur = Column(String(100), nullable=True)
    consommation_auxiliaire = Column(Float, nullable=True)
    date = Column(Date)
    valeur_production = Column(Float, nullable=True)

    centrale = relationship("Centrale", back_populates="productions")

class Groupe(Base):
    __tablename__ = "groupes"
    id = Column(Integer, primary_key=True, index=True)
    id_groupe_externe = Column(BigInteger, unique=True, index=True, nullable=True)
    nom = Column(String(100), nullable=True)
    centrale_id = Column(Integer, ForeignKey("centrales.id"), nullable=True)
    moteur = Column(String(100), nullable=True)
    alternateur = Column(String(100), nullable=True)
    type_production = Column(String(100), nullable=True)
    puissance_nominale = Column(Float, nullable=True)
    compteur_energie = Column(String(100), nullable=True)

    centrale = relationship("Centrale", back_populates="groupes")
    deplacements = relationship("DeplacementGroupe", back_populates="groupe")

class DeplacementGroupe(Base):
    __tablename__ = "deplacement_groupes"
    id = Column(Integer, primary_key=True, index=True)
    groupe_id = Column(Integer, ForeignKey("groupes.id"))
    centrale_source_id = Column(Integer, ForeignKey("centrales.id"), nullable=True)
    date_debut = Column(Date)
    date_fin = Column(Date, nullable=True)

    groupe = relationship("Groupe", back_populates="deplacements")

class Rendement(Base):
    __tablename__ = "rendements"
    id = Column(Integer, primary_key=True, index=True)
    id_rendement_externe = Column(BigInteger, unique=True, index=True, nullable=True)  # ID_Rendement du fichier Excel
    date = Column(Date, index=True)  # pas unique: plusieurs lignes par date (une par centrale/réseau)
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
    id_recap_externe = Column(BigInteger, unique=True, index=True, nullable=True)  # IDRecapEnergie du fichier Excel
    poste_source = Column(String(255))
    depart_30kv = Column(String(100))
    transformateur_htb_hta = Column(String(100))
    sccn_scada = Column(Float)
    dms = Column(Float)
    desa = Column(Float)
    taux_energie = Column(Float)
    source_donnees = Column(String(100))
    energie_validee = Column(Float)
    date = Column(Date, index=True)
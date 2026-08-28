from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, index=True)  # correspond à idRole
    nom_role = Column(String(50), unique=True, nullable=False)  # correspond à nomRole
    description = Column(String(255), nullable=True)

    # Un rôle peut être partagé par plusieurs utilisateurs -> relation "un vers plusieurs"
    utilisateurs = relationship("Utilisateur", back_populates="role")


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(BigInteger, primary_key=True, index=True)  # correspond à idUtilisateur
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)  # jamais le mot de passe en clair, voir §2
    date_creation = Column(DateTime, default=datetime.utcnow)
    ldap = Column(Boolean, default=False)

    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False)  # correspond à FK idRole
    role = relationship("Role", back_populates="utilisateurs")

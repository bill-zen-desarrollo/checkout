from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    token_pago = Column(String(255), nullable=True)  # Hash del método de pago guardado

    ordenes = relationship("OrdenCompra", back_populates="usuario")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, index=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)


class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    estado = Column(String(20), nullable=False)  # "aprobado" | "rechazado"

    usuario = relationship("Usuario", back_populates="ordenes")

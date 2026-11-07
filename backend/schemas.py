from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- Esquemas de Producto ---
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


# --- Esquemas de One-Click Checkout ---
class OneClickCheckoutRequest(BaseModel):
    usuario_id: int = Field(..., gt=0, description="ID del usuario que realiza la compra")
    producto_id: int = Field(..., gt=0, description="ID del producto a comprar")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades a comprar (mínimo 1)")


class OrdenCompraResponse(BaseModel):
    id: int
    usuario_id: int
    total: float
    fecha: datetime
    estado: str

    model_config = ConfigDict(from_attributes=True)


class OneClickCheckoutResponse(BaseModel):
    mensaje: str
    orden: OrdenCompraResponse
    stock_restante: int

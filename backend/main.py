from contextlib import asynccontextmanager
from typing import Generator

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
import models
import schemas
from security import generar_hash, validar_token_pago_guardado


def inicializar_datos_prueba(db: Session) -> None:
    """Inserta datos semilla iniciales si la base de datos está recién creada."""
    if db.query(models.Usuario).count() == 0:
        usuario_demo = models.Usuario(
            nombre="Cliente Black Friday",
            email="cliente@checkout.com",
            password_hash=generar_hash("PasswordSegura123!"),
            token_pago=generar_hash("tok_visa_4242_blackfriday"),
        )
        usuario_sin_token = models.Usuario(
            nombre="Usuario Sin Tarjeta",
            email="sintarjeta@checkout.com",
            password_hash=generar_hash("PasswordSegura123!"),
            token_pago=None,
        )
        db.add_all([usuario_demo, usuario_sin_token])

    if db.query(models.Producto).count() == 0:
        productos_demo = [
            models.Producto(nombre="Monitor Gamer 27\" 144Hz", precio=249.99, stock=15),
            models.Producto(nombre="Teclado Mecánico RGB", precio=89.50, stock=30),
            models.Producto(nombre="Mouse Inalámbrico Pro", precio=59.90, stock=25),
            models.Producto(nombre="Tarjeta Gráfica RTX Edición Limitada", precio=799.00, stock=0),
        ]
        db.add_all(productos_demo)

    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea automáticamente checkout_software.db y todas las tablas al iniciar el servidor
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        inicializar_datos_prueba(db)
    yield


app = FastAPI(
    title="Checkout Software API - One-Click Checkout",
    description="Backend optimizado para compras a 1 clic en eventos de alto tráfico (Black Friday).",
    version="1.0.0",
    lifespan=lifespan,
)


# Inyección de dependencias para obtener la sesión de BD
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/api/productos",
    response_model=list[schemas.ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos con stock disponible",
)
def listar_productos_disponibles(db: Session = Depends(get_db)):
    """Retorna únicamente los productos cuyo stock sea mayor a 0."""
    productos = (
        db.query(models.Producto)
        .filter(models.Producto.stock > 0)
        .all()
    )
    return productos


@app.post(
    "/api/checkout/one-click",
    response_model=schemas.OneClickCheckoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Procesar compra instantánea a 1 clic",
)
def procesar_one_click_checkout(
    payload: schemas.OneClickCheckoutRequest,
    db: Session = Depends(get_db),
):
    """
    Ejecuta el flujo de compra a 1 clic:
    1. Verifica que el usuario exista y tenga un `token_pago` válido.
    2. Verifica que el producto exista y cuente con stock suficiente.
    3. Descuenta el stock, registra la orden como 'aprobado' y retorna 200 OK.
    """
    # 1. Validar existencia del usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.id == payload.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con ID {payload.usuario_id} no existe.",
        )

    # 2. Validar token de pago guardado
    if not validar_token_pago_guardado(usuario.token_pago):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene un método de pago (token_pago) válido configurado para One-Click Checkout.",
        )

    # 3. Validar existencia del producto
    producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto con ID {payload.producto_id} no existe.",
        )

    # 4. Verificar disponibilidad de stock
    if producto.stock < payload.cantidad:
        # Registramos el intento fallido como orden rechazada para trazabilidad
        orden_rechazada = models.OrdenCompra(
            usuario_id=usuario.id,
            total=round(producto.precio * payload.cantidad, 2),
            estado="rechazado",
        )
        db.add(orden_rechazada)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente para '{producto.nombre}'. Stock disponible: {producto.stock}, solicitado: {payload.cantidad}.",
        )

    # 5. Descontar stock, calcular total y crear la Orden de Compra aprobada
    producto.stock -= payload.cantidad
    total_compra = round(producto.precio * payload.cantidad, 2)

    nueva_orden = models.OrdenCompra(
        usuario_id=usuario.id,
        total=total_compra,
        estado="aprobado",
    )
    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)

    return schemas.OneClickCheckoutResponse(
        mensaje="Compra a 1 clic procesada exitosamente",
        orden=nueva_orden,
        stock_restante=producto.stock,
    )

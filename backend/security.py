from passlib.context import CryptContext

# Usamos pbkdf2_sha256 y bcrypt para máxima compatibilidad en entornos Windows/Linux
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def generar_hash(secreto: str) -> str:
    """Encripta una contraseña o un token de pago en texto plano."""
    return pwd_context.hash(secreto)


def verificar_hash(secreto_plano: str, secreto_hasheado: str) -> bool:
    """Verifica si un texto plano coincide con su hash."""
    return pwd_context.verify(secreto_plano, secreto_hasheado)


def validar_token_pago_guardado(token_hasheado: str | None) -> bool:
    """
    Valida que el usuario posea un token_pago registrado y con estructura de hash reconocida
    por passlib para autorizar compras a 1 clic.
    """
    if not token_hasheado or not token_hasheado.strip():
        return False
    return pwd_context.identify(token_hasheado) is not None

from typing import Any, Dict
import requests


class APIClient:
    """Cliente HTTP encargado de centralizar la comunicación con el backend FastAPI."""

    BASE_URL = "http://localhost:8000/api"

    def __init__(self, base_url: str | None = None, timeout: int = 10) -> None:
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout

    def get_productos(self) -> Dict[str, Any]:
        """Obtiene el catálogo de productos disponibles desde GET /api/productos."""
        endpoint = f"{self.base_url}/productos"
        try:
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json(),
                "error": None,
            }
        except requests.exceptions.RequestException as exc:
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "error": str(exc),
            }

    def process_one_click_checkout(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envía la petición POST de 'Pagar con 1 Clic' al endpoint /api/checkout/one-click.

        Args:
            payload: Diccionario compatible con schemas.OneClickCheckoutRequest:
                {
                    "usuario_id": int,
                    "producto_id": int,
                    "cantidad": int
                }
        """
        endpoint = f"{self.base_url}/checkout/one-click"

        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            response.raise_for_status()

            data = response.json() if response.content else {}
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": data,
                "error": None,
            }

        except requests.exceptions.HTTPError as exc:
            error_detail = f"Error del servidor (HTTP {exc.response.status_code})"
            try:
                body = exc.response.json()
                if isinstance(body, dict) and "detail" in body:
                    error_detail = str(body["detail"])
            except ValueError:
                pass
            return {
                "success": False,
                "status_code": exc.response.status_code,
                "data": None,
                "error": error_detail,
            }

        except requests.exceptions.RequestException as exc:
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "error": f"No se pudo conectar con el servidor ({endpoint}): {exc}",
            }

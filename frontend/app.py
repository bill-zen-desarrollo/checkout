from typing import Any, Dict
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES

from api_client import APIClient
from views.carrito_view import CarritoView
from views.success_view import SuccessView


class CheckoutApp(ttk.Window):
    """Ventana principal y controlador de vistas para el flujo 'Pagar con 1 Clic'."""

    def __init__(self) -> None:
        super().__init__(
            title="Black Friday E-Commerce — Checkout 1 Clic",
            themename="darkly",
            size=(780, 520),
            minsize=(680, 460),
        )
        self.place_window_center()

        # Inicializar capa de red
        self.api_client = APIClient()

        # Contenedor raíz donde se apilan e intercambian los Frames (Vistas)
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=YES)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Registro e instanciación de vistas
        self.views: Dict[str, ttk.Frame] = {}
        self._register_views()

        # Mostrar vista inicial
        self.show_view("carrito")

    def _register_views(self) -> None:
        """Instancia las vistas de la aplicación y las ubica en el contenedor."""
        carrito_view = CarritoView(
            master=self.container,
            api_client=self.api_client,
            on_checkout_success=self._on_checkout_success,
        )
        success_view = SuccessView(
            master=self.container,
            on_back_to_cart=lambda: self.show_view("carrito"),
        )

        self.views["carrito"] = carrito_view
        self.views["success"] = success_view

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def show_view(self, view_name: str) -> None:
        """Eleva al frente la vista solicitada (`carrito` o `success`)."""
        view = self.views.get(view_name)
        if view is None:
            raise KeyError(f"La vista '{view_name}' no está registrada.")
        view.tkraise()

    def _on_checkout_success(self, response_data: Dict[str, Any]) -> None:
        """Callback ejecutado cuando la API responde HTTP 200 OK al pago con 1 Clic."""
        success_view: SuccessView = self.views["success"]  # type: ignore[assignment]
        success_view.set_order_details(response_data)
        self.show_view("success")


if __name__ == "__main__":
    app = CheckoutApp()
    app.mainloop()

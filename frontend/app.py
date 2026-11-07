import tkinter as tk
from datetime import datetime, timedelta
from typing import Any, Dict

import ttkbootstrap as ttk

from api_client import APIClient
from ui.logo import build_logo
from ui.theme import Fonts, Palette, dpi_factor
from views.carrito_view import CarritoView
from views.success_view import SuccessView


class CheckoutApp(ttk.Window):
    """Ventana principal y controlador de vistas para el flujo 'Pagar con 1 Clic'."""

    def __init__(self) -> None:
        super().__init__(
            title="checkout — Black Friday · Pagar con 1 Clic",
            themename="darkly",
        )
        self.configure(bg=Palette.BG)
        self._fit_to_screen(base_size=(1180, 760))

        # Logo de checkout como ícono de la ventana y de la barra de tareas
        self._icon_img = build_logo(64)
        self._header_logo = build_logo(42)
        self.iconphoto(True, self._icon_img)

        if self.state() != "zoomed":
            self.place_window_center()

        # Inicializar capa de red
        self.api_client = APIClient()

        self._build_header()

        # Contenedor raíz donde se apilan e intercambian los Frames (Vistas)
        self.container = tk.Frame(self, bg=Palette.BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Registro e instanciación de vistas
        self.views: Dict[str, tk.Frame] = {}
        self._register_views()

        # Mostrar vista inicial y sincronizar stock real con el backend
        self.show_view("carrito")
        self.after(300, self.views["carrito"].refresh_stock)  # type: ignore[attr-defined]
        self._tick_countdown()

    # ------------------------------------------------------------------ #
    # Tamaño de ventana adaptado al DPI
    # ------------------------------------------------------------------ #
    def _fit_to_screen(self, base_size: tuple[int, int]) -> None:
        """Escala el tamaño según el DPI; si no cabe en pantalla, abre maximizada."""
        f = dpi_factor(self)
        width, height = int(base_size[0] * f), int(base_size[1] * f)
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.minsize(min(width, screen_w) - 160, min(height, screen_h) - 160)

        if width >= screen_w - 40 or height >= screen_h - 80:
            self.geometry(f"{min(width, screen_w - 80)}x{min(height, screen_h - 120)}")
            self.state("zoomed")
        else:
            self.geometry(f"{width}x{height}")

    # ------------------------------------------------------------------ #
    # Header de marca
    # ------------------------------------------------------------------ #
    def _build_header(self) -> None:
        header = tk.Frame(self, bg=Palette.HEADER, padx=28, pady=14)
        header.pack(fill="x")

        # Marca: logo + wordmark
        brand = tk.Frame(header, bg=Palette.HEADER)
        brand.pack(side="left")
        tk.Label(brand, image=self._header_logo, bg=Palette.HEADER).pack(side="left", padx=(0, 12))

        wordmark = tk.Frame(brand, bg=Palette.HEADER)
        wordmark.pack(side="left")
        tk.Label(wordmark, text="checkout", bg=Palette.HEADER, fg=Palette.TEXT,
                 font=Fonts.BRAND).pack(anchor="w")
        tk.Label(wordmark, text="ONE-CLICK PAYMENTS", bg=Palette.HEADER, fg=Palette.PRIMARY,
                 font=(Fonts.FAMILY_BOLD, 8)).pack(anchor="w", pady=(0, 0))

        # Estado de conexión con la API
        self.api_status_lbl = tk.Label(header, text="●  Conectando con la API...", bg=Palette.HEADER,
                                       fg=Palette.TEXT_MUTED, font=Fonts.SMALL_BOLD)
        self.api_status_lbl.pack(side="right")

        tk.Frame(header, bg=Palette.BORDER, width=1, height=28).pack(side="right", padx=18)

        # Contador regresivo de ofertas
        countdown = tk.Frame(header, bg=Palette.SURFACE, padx=14, pady=6,
                             highlightthickness=1, highlightbackground=Palette.BORDER)
        countdown.pack(side="right")
        tk.Label(countdown, text="⏱  Las ofertas terminan en", bg=Palette.SURFACE,
                 fg=Palette.TEXT_MUTED, font=Fonts.SMALL).pack(side="left")
        self.countdown_lbl = tk.Label(countdown, text="--:--:--", bg=Palette.SURFACE,
                                      fg=Palette.ACCENT, font=(Fonts.FAMILY_BOLD, 11))
        self.countdown_lbl.pack(side="left", padx=(8, 0))

        tk.Frame(self, bg=Palette.BORDER, height=1).pack(fill="x")

    def _tick_countdown(self) -> None:
        """Actualiza cada segundo el tiempo restante hasta la medianoche."""
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        remaining = int((midnight - now).total_seconds())
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        self.countdown_lbl.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self._tick_countdown)

    def set_api_status(self, online: bool) -> None:
        """Indicador visual del estado del backend FastAPI."""
        if online:
            self.api_status_lbl.configure(text="●  API conectada", fg=Palette.PRIMARY)
        else:
            self.api_status_lbl.configure(text="●  API desconectada · modo demo", fg=Palette.DANGER)

    # ------------------------------------------------------------------ #
    # Gestión de vistas
    # ------------------------------------------------------------------ #
    def _register_views(self) -> None:
        """Instancia las vistas de la aplicación y las ubica en el contenedor."""
        carrito_view = CarritoView(
            master=self.container,
            api_client=self.api_client,
            on_checkout_success=self._on_checkout_success,
            on_connection_change=self.set_api_status,
        )
        success_view = SuccessView(
            master=self.container,
            on_back_to_cart=self._on_back_to_cart,
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
        self.set_api_status(True)
        success_view: SuccessView = self.views["success"]  # type: ignore[assignment]
        success_view.set_order_details(response_data)
        self.show_view("success")

    def _on_back_to_cart(self) -> None:
        """Regresa al carrito y sincroniza el stock actualizado desde el backend."""
        self.show_view("carrito")
        self.views["carrito"].refresh_stock()  # type: ignore[attr-defined]


if __name__ == "__main__":
    app = CheckoutApp()
    app.mainloop()

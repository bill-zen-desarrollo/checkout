from typing import Any, Callable, Dict
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, CENTER, INFO, SUCCESS, YES


class SuccessView(ttk.Frame):
    """Vista de confirmación de orden tras un pago exitoso con 1 Clic en Black Friday."""

    def __init__(
        self,
        master: ttk.Window | ttk.Frame,
        on_back_to_cart: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, padding=36, **kwargs)
        self.on_back_to_cart = on_back_to_cart
        self._build_ui()

    def _build_ui(self) -> None:
        """Construye los widgets centrados con el resumen de confirmación."""
        container = ttk.Frame(self)
        container.pack(fill=BOTH, expand=YES)

        icon_label = ttk.Label(
            container,
            text="✅",
            font=("Segoe UI Emoji", 44),
            anchor=CENTER,
        )
        icon_label.pack(pady=(16, 10))

        title_label = ttk.Label(
            container,
            text="¡Transacción de Black Friday Procesada!",
            font=("Segoe UI", 20, "bold"),
            bootstyle=SUCCESS,
            anchor=CENTER,
        )
        title_label.pack(pady=(0, 8))

        subtitle_label = ttk.Label(
            container,
            text="Tu compra con 1 Clic se ha completado exitosamente y está en preparación.",
            font=("Segoe UI", 11),
            bootstyle="secondary",
            anchor=CENTER,
        )
        subtitle_label.pack(pady=(0, 20))

        # Tarjeta resaltada con el ID de la orden
        card = ttk.Labelframe(
            container,
            text=" Detalles de la Orden ",
            padding=(28, 18),
            bootstyle=INFO,
        )
        card.pack(pady=(0, 24))

        self.order_id_label = ttk.Label(
            card,
            text="ID de Orden: —",
            font=("Consolas", 15, "bold"),
            bootstyle="light",
            anchor=CENTER,
        )
        self.order_id_label.pack(pady=(0, 6))

        self.details_label = ttk.Label(
            card,
            text="",
            font=("Segoe UI", 10),
            bootstyle="info",
            anchor=CENTER,
        )
        self.details_label.pack(pady=(0, 6))

        self.message_label = ttk.Label(
            card,
            text="Recibirás el comprobante electrónico en tu correo registrado.",
            font=("Segoe UI", 10),
            bootstyle="secondary",
            anchor=CENTER,
        )
        self.message_label.pack()

        if self.on_back_to_cart:
            back_btn = ttk.Button(
                container,
                text="← Volver al Carrito",
                bootstyle="outline-light",
                padding=(16, 8),
                command=self.on_back_to_cart,
            )
            back_btn.pack()

    def set_order_details(self, order_data: Dict[str, Any]) -> None:
        """Actualiza la vista leyendo schemas.OneClickCheckoutResponse del backend de Camilo."""
        orden = order_data.get("orden") if isinstance(order_data.get("orden"), dict) else {}

        order_id = (
            orden.get("id")
            or order_data.get("order_id")
            or order_data.get("id")
            or "BF-ORD-2026-0001"
        )
        total = orden.get("total")
        estado = str(orden.get("estado", "aprobado")).upper()
        stock_restante = order_data.get("stock_restante")
        mensaje = order_data.get(
            "mensaje",
            order_data.get("message", "Compra a 1 clic procesada exitosamente"),
        )

        self.order_id_label.configure(text=f"ID de Orden: #{order_id}")

        extra_parts = [f"Estado: {estado}"]
        if total is not None:
            extra_parts.append(f"Total pagado: ${float(total):,.2f} USD")
        if stock_restante is not None:
            extra_parts.append(f"Stock restante: {stock_restante}")
        self.details_label.configure(text="  |  ".join(extra_parts))

        self.message_label.configure(text=str(mensaje))

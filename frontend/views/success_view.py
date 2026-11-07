import tkinter as tk
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from ui.logo import build_success_badge
from ui.theme import Fonts, Palette
from ui.widgets import Card, FlatButton, Pill


class SuccessView(tk.Frame):
    """Vista de confirmación (recibo) tras un pago exitoso con 1 Clic en Black Friday."""

    def __init__(
        self,
        master: tk.Misc,
        on_back_to_cart: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=Palette.BG, **kwargs)
        self.on_back_to_cart = on_back_to_cart
        self._badge_img = build_success_badge(104)
        self.value_labels: Dict[str, tk.Label] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Construye una columna centrada con insignia, título y recibo."""
        column = tk.Frame(self, bg=Palette.BG)
        column.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(column, image=self._badge_img, bg=Palette.BG).pack(pady=(0, 14))
        tk.Label(column, text="¡Pago aprobado!", bg=Palette.BG, fg=Palette.TEXT, font=Fonts.H1).pack()
        tk.Label(
            column,
            text="Tu transacción de Black Friday fue procesada con 1 clic.",
            bg=Palette.BG, fg=Palette.TEXT_MUTED, font=Fonts.BODY,
        ).pack(pady=(4, 22))

        # Recibo
        receipt = Card(column, padding=26)
        receipt.pack(fill="x")
        receipt.columnconfigure(1, weight=1)

        head = tk.Frame(receipt, bg=Palette.CARD)
        head.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(head, text="RECIBO DE COMPRA", bg=Palette.CARD, fg=Palette.TEXT_DIM,
                 font=Fonts.SMALL_BOLD).pack(side="left")
        self.status_pill = Pill(head, text="APROBADO", bg=Palette.SUCCESS_BG, fg=Palette.PRIMARY)
        self.status_pill.pack(side="right")

        self.order_id_label = tk.Label(receipt, text="Orden #—", bg=Palette.CARD, fg=Palette.TEXT,
                                       font=(Fonts.FAMILY_BOLD, 24), anchor="w")
        self.order_id_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 14))

        rows = [
            ("producto", "Producto"),
            ("cantidad", "Cantidad"),
            ("metodo", "Método de pago"),
            ("fecha", "Fecha"),
            ("stock", "Stock restante"),
        ]
        for i, (key, label) in enumerate(rows, start=2):
            tk.Label(receipt, text=label, bg=Palette.CARD, fg=Palette.TEXT_MUTED,
                     font=Fonts.BODY).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 40))
            value = tk.Label(receipt, text="—", bg=Palette.CARD, fg=Palette.TEXT, font=Fonts.H3, anchor="e")
            value.grid(row=i, column=1, sticky="e", pady=4)
            self.value_labels[key] = value

        # Línea punteada estilo ticket
        dashes = tk.Canvas(receipt, height=2, bg=Palette.CARD, highlightthickness=0)
        dashes.grid(row=10, column=0, columnspan=2, sticky="ew", pady=16)
        dashes.bind("<Configure>", lambda e: self._draw_dashes(dashes, e.width))

        tk.Label(receipt, text="Total pagado", bg=Palette.CARD, fg=Palette.TEXT,
                 font=Fonts.H3).grid(row=11, column=0, sticky="w")
        self.total_label = tk.Label(receipt, text="$0.00", bg=Palette.CARD, fg=Palette.PRIMARY, font=Fonts.PRICE)
        self.total_label.grid(row=11, column=1, sticky="e")

        self.message_label = tk.Label(column, text="", bg=Palette.BG, fg=Palette.TEXT_MUTED, font=Fonts.SMALL)
        self.message_label.pack(pady=(14, 18))

        if self.on_back_to_cart:
            FlatButton(column, text="←  Seguir comprando", command=self.on_back_to_cart).pack(fill="x")

    @staticmethod
    def _draw_dashes(canvas: tk.Canvas, width: int) -> None:
        canvas.delete("all")
        for x in range(0, width, 12):
            canvas.create_line(x, 1, x + 6, 1, fill=Palette.BORDER, width=2)

    @staticmethod
    def _format_date(raw: Any) -> str:
        """Convierte la fecha ISO (UTC) del backend a hora local legible."""
        if not raw:
            return datetime.now().strftime("%d/%m/%Y  %I:%M %p")
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone().strftime("%d/%m/%Y  %I:%M %p")
        except ValueError:
            return str(raw)

    def set_order_details(self, order_data: Dict[str, Any]) -> None:
        """Actualiza el recibo leyendo schemas.OneClickCheckoutResponse del backend de Camilo."""
        orden = order_data.get("orden") if isinstance(order_data.get("orden"), dict) else {}

        order_id = orden.get("id") or order_data.get("order_id") or order_data.get("id") or "—"
        estado = str(orden.get("estado", "aprobado")).upper()
        total = orden.get("total")
        stock = order_data.get("stock_restante")

        self.order_id_label.configure(text=f"Orden #{order_id}")
        self.status_pill.configure(text=f"✔ {estado}")
        self.value_labels["producto"].configure(text=order_data.get("_producto", "—"))
        self.value_labels["cantidad"].configure(text=str(order_data.get("_cantidad", "—")))
        self.value_labels["metodo"].configure(text=order_data.get("_metodo", "Tarjeta guardada"))
        self.value_labels["fecha"].configure(text=self._format_date(orden.get("fecha")))
        self.value_labels["stock"].configure(text="—" if stock is None else f"{stock} unidades")
        self.total_label.configure(text="$—" if total is None else f"${float(total):,.2f}")
        self.message_label.configure(
            text=order_data.get("mensaje", "Compra a 1 clic procesada exitosamente")
            + "  ·  El comprobante llegará a tu correo."
        )

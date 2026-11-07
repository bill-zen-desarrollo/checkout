from typing import Any, Callable, Dict, List
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, CENTER, E, END, EW, LEFT, RIGHT, SUCCESS, W, X, YES
from ttkbootstrap.dialogs import Messagebox

from api_client import APIClient


class CarritoView(ttk.Frame):
    """Vista del carrito de compras conectada con el backend FastAPI de Camilo."""

    # Datos dummy alineados con los productos semilla de backend/main.py
    MOCK_PRODUCTS: List[Dict[str, Any]] = [
        {"id": 1, "nombre": 'Monitor Gamer 27" 144Hz', "cantidad": 1, "precio": 249.99},
        {"id": 2, "nombre": "Teclado Mecánico RGB", "cantidad": 1, "precio": 89.50},
        {"id": 3, "nombre": "Mouse Inalámbrico Pro", "cantidad": 2, "precio": 59.90},
    ]

    DEFAULT_USUARIO_ID = 1  # ID de 'Cliente Black Friday' con token_pago válido en el backend

    def __init__(
        self,
        master: ttk.Window | ttk.Frame,
        api_client: APIClient,
        on_checkout_success: Callable[[Dict[str, Any]], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, padding=24, **kwargs)
        self.api_client = api_client
        self.on_checkout_success = on_checkout_success

        self._build_ui()
        self._load_mock_data()

    def _build_ui(self) -> None:
        """Construye y posiciona los widgets de la vista del carrito."""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 16))

        title_label = ttk.Label(
            header_frame,
            text="🛒 Carrito de Compras — Black Friday Express",
            font=("Segoe UI", 18, "bold"),
        )
        title_label.pack(side=LEFT)

        badge_label = ttk.Label(
            header_frame,
            text="🔥 OFERTAS RELÁMPAGO",
            bootstyle="warning-inverse",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 4),
        )
        badge_label.pack(side=RIGHT)

        # Tabla de productos (Treeview)
        table_container = ttk.Frame(self)
        table_container.pack(fill=BOTH, expand=YES, pady=(0, 16))

        columns = ("id", "nombre", "cantidad", "precio")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=8,
            bootstyle="info",
            selectmode="browse",
        )

        self.tree.heading("id", text="ID", anchor=CENTER)
        self.tree.heading("nombre", text="Nombre del Producto", anchor=W)
        self.tree.heading("cantidad", text="Cantidad", anchor=CENTER)
        self.tree.heading("precio", text="Precio Unitario ($)", anchor=E)

        self.tree.column("id", width=80, anchor=CENTER, stretch=False)
        self.tree.column("nombre", width=360, anchor=W, stretch=True)
        self.tree.column("cantidad", width=100, anchor=CENTER, stretch=False)
        self.tree.column("precio", width=140, anchor=E, stretch=False)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill="y")

        # Panel inferior: Resumen y botón de 1 Clic
        footer_frame = ttk.Frame(self)
        footer_frame.pack(fill=X, pady=(8, 0))
        footer_frame.columnconfigure(0, weight=1)

        self.total_label = ttk.Label(
            footer_frame,
            text="Total del carrito: $0.00",
            font=("Segoe UI", 15, "bold"),
            bootstyle="light",
        )
        self.total_label.grid(row=0, column=0, sticky=W, pady=(0, 8))

        self.status_label = ttk.Label(
            footer_frame,
            text="Selecciona un producto (o procesa el primero) para comprar al instante con tu tarjeta guardada.",
            font=("Segoe UI", 9),
            bootstyle="secondary",
        )
        self.status_label.grid(row=1, column=0, sticky=W, pady=(0, 14))

        self.one_click_btn = ttk.Button(
            footer_frame,
            text="⚡ Pagar con 1 Clic",
            bootstyle=SUCCESS,
            padding=(20, 12),
            command=self._handle_one_click_checkout,
        )
        self.one_click_btn.grid(row=2, column=0, sticky=EW)

    def _load_mock_data(self) -> None:
        """Puebla el Treeview con datos iniciales y selecciona la primera fila por defecto."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0.0
        first_row_id = None
        for product in self.MOCK_PRODUCTS:
            subtotal = product["cantidad"] * product["precio"]
            total += subtotal
            row_id = self.tree.insert(
                "",
                END,
                values=(
                    product["id"],
                    product["nombre"],
                    product["cantidad"],
                    f"{product['precio']:.2f}",
                ),
            )
            if first_row_id is None:
                first_row_id = row_id

        if first_row_id is not None:
            self.tree.selection_set(first_row_id)
            self.tree.focus(first_row_id)

        self.total_label.configure(text=f"Total del carrito: ${total:,.2f} USD")

    def _build_checkout_payload(self) -> Dict[str, Any] | None:
        """Empaqueta los datos en el formato exacto de schemas.OneClickCheckoutRequest."""
        children = self.tree.get_children()
        if not children:
            return None

        selected = self.tree.selection()
        target_row = selected[0] if selected else children[0]
        prod_id, _nombre, cantidad, _precio = self.tree.item(target_row, "values")

        return {
            "usuario_id": self.DEFAULT_USUARIO_ID,
            "producto_id": int(prod_id),
            "cantidad": int(cantidad),
        }

    def _handle_one_click_checkout(self) -> None:
        """Empaqueta el carrito y delega la petición POST al APIClient."""
        payload = self._build_checkout_payload()

        if payload is None:
            Messagebox.show_warning(
                "El carrito está vacío.",
                title="Carrito vacío",
                parent=self,
            )
            return

        self.one_click_btn.configure(state="disabled", text="⏳ Procesando orden...")
        self.status_label.configure(
            text="Conectando con http://localhost:8000/api/checkout/one-click...",
            bootstyle="info",
        )
        self.update_idletasks()

        result = self.api_client.process_one_click_checkout(payload)

        self.one_click_btn.configure(state="normal", text="⚡ Pagar con 1 Clic")

        if result["success"] and result["status_code"] == 200:
            self.status_label.configure(
                text="¡Orden procesada con éxito!",
                bootstyle="success",
            )
            self.on_checkout_success(result["data"] or {})
        else:
            error_msg = result.get("error") or "Error desconocido al procesar el pago."
            self.status_label.configure(
                text=f"Error en el pago: {error_msg}",
                bootstyle="danger",
            )
            Messagebox.show_error(
                error_msg,
                title="Error en Pagar con 1 Clic",
                parent=self,
            )

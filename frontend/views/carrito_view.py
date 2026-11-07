import tkinter as tk
import tkinter.font as tkfont
from typing import Any, Callable, Dict, List, Optional

import ttkbootstrap as ttk

from api_client import APIClient
from ui.logo import build_gradient_banner
from ui.theme import Fonts, Palette, dpi_factor
from ui.widgets import Card, FlatButton, SelectableCard


class CarritoView(tk.Frame):
    """Vista del carrito de compras (Black Friday) conectada con el backend FastAPI de Camilo."""

    # Datos dummy alineados con los 4 productos semilla de backend/main.py
    MOCK_PRODUCTS: List[Dict[str, Any]] = [
        {"id": 1, "nombre": 'Monitor Gamer 27" 144Hz', "cantidad": 1, "precio": 249.99, "stock": 15},
        {"id": 2, "nombre": "Teclado Mecánico RGB", "cantidad": 1, "precio": 89.50, "stock": 30},
        {"id": 3, "nombre": "Mouse Inalámbrico Pro", "cantidad": 2, "precio": 59.90, "stock": 25},
        {"id": 4, "nombre": "Tarjeta Gráfica RTX Edición Limitada", "cantidad": 1, "precio": 799.00, "stock": 0},
    ]

    # Perfiles semilla del backend (usuario_id → datos de presentación)
    PROFILES: Dict[int, Dict[str, str]] = {
        1: {"titulo": "Cliente Black Friday", "metodo": "VISA •••• 4242", "icono": "💳"},
        2: {"titulo": "Usuario Sin Tarjeta", "metodo": "Sin método guardado", "icono": "⚠"},
    }

    MAX_QTY = 99

    def __init__(
        self,
        master: tk.Misc,
        api_client: APIClient,
        on_checkout_success: Callable[[Dict[str, Any]], None],
        on_connection_change: Optional[Callable[[bool], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=Palette.BG, padx=24, pady=16, **kwargs)
        self.api_client = api_client
        self.on_checkout_success = on_checkout_success
        self.on_connection_change = on_connection_change

        self._f = dpi_factor(self)  # Escala de píxeles según el DPI de Windows
        self.products: List[Dict[str, Any]] = [dict(p) for p in self.MOCK_PRODUCTS]
        self.usuario_id = 1
        self._banner_img: Optional[tk.PhotoImage] = None
        self._banner_job: Optional[str] = None

        self._configure_styles()
        self._build_ui()
        self._render_products()
        self._select_profile(1)

    # ------------------------------------------------------------------ #
    # Estilos
    # ------------------------------------------------------------------ #
    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.configure(
            "Cart.Treeview",
            background=Palette.CARD,
            fieldbackground=Palette.CARD,
            foreground=Palette.TEXT,
            rowheight=int(36 * self._f),
            borderwidth=0,
            relief="flat",
            font=Fonts.BODY,
        )
        style.map(
            "Cart.Treeview",
            background=[("selected", Palette.SUCCESS_BG)],
            foreground=[("selected", Palette.PRIMARY_HOVER)],
        )
        style.configure(
            "Cart.Treeview.Heading",
            background=Palette.SURFACE,
            foreground=Palette.TEXT_MUTED,
            font=Fonts.SMALL_BOLD,
            relief="flat",
            borderwidth=0,
            padding=(10, 10),
        )
        style.map("Cart.Treeview.Heading", background=[("active", Palette.SURFACE)])

    # ------------------------------------------------------------------ #
    # Construcción de la interfaz
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2, minsize=int(340 * self._f))
        self.rowconfigure(1, weight=1)

        self._build_banner()
        self._build_cart_panel()
        self._build_summary_panel()

    def _build_banner(self) -> None:
        """Banner promocional con degradado y textos superpuestos."""
        # Alturas reales de cada línea según la fuente (evita superposición con DPI alto)
        self._lh_small = tkfont.Font(font=Fonts.SMALL_BOLD).metrics("linespace")
        self._lh_hero = tkfont.Font(font=Fonts.HERO).metrics("linespace")
        self._lh_body = tkfont.Font(font=Fonts.BODY).metrics("linespace")
        self._banner_pad = int(14 * self._f)
        height = self._banner_pad * 2 + self._lh_small + self._lh_hero + self._lh_body - int(6 * self._f)

        self.banner = tk.Canvas(self, height=height, bg=Palette.BG, highlightthickness=0, bd=0)
        self.banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, int(14 * self._f)))
        self.banner.bind("<Configure>", self._schedule_banner_redraw)

    def _schedule_banner_redraw(self, _event: tk.Event) -> None:
        if self._banner_job:
            self.after_cancel(self._banner_job)
        self._banner_job = self.after(60, self._draw_banner)

    def _draw_banner(self) -> None:
        width = self.banner.winfo_width()
        height = self.banner.winfo_height()
        if width < 10:
            return

        self._banner_img = build_gradient_banner(width, height)
        c = self.banner
        c.delete("all")
        c.create_image(0, 0, image=self._banner_img, anchor="nw")

        x = int(28 * self._f)
        y = self._banner_pad
        c.create_text(x + 2, y, text="⚡ EVENTO EXCLUSIVO · SOLO HOY", anchor="nw",
                      fill="#FFE3F6", font=Fonts.SMALL_BOLD)
        y += self._lh_small - int(4 * self._f)
        c.create_text(x, y, text="BLACK FRIDAY", anchor="nw", fill="white", font=Fonts.HERO)
        y += self._lh_hero - int(4 * self._f)
        c.create_text(x + 2, y, text="Compra en 1 clic con tu tarjeta guardada  ·  Envío gratis en todo el catálogo",
                      anchor="nw", fill="#F6D9FF", font=Fonts.BODY)

        right = width - int(32 * self._f)
        c.create_text(right, height / 2, text="-40%", anchor="e", fill="white", font=(Fonts.FAMILY_BLACK, 34))
        c.create_text(right - 4, height / 2 - int(30 * self._f), text="HASTA", anchor="se",
                      fill="#FFE3F6", font=Fonts.SMALL_BOLD)

    def _build_cart_panel(self) -> None:
        """Panel izquierdo: tabla del carrito + selección de método de pago."""
        panel = Card(self, padding=22)
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 18))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        # Encabezado del panel
        head = tk.Frame(panel, bg=Palette.CARD)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        tk.Label(head, text="Tu carrito", bg=Palette.CARD, fg=Palette.TEXT, font=Fonts.H2).pack(side="left")
        self.items_lbl = tk.Label(head, text="", bg=Palette.CARD, fg=Palette.TEXT_MUTED, font=Fonts.SMALL)
        self.items_lbl.pack(side="left", padx=(10, 0), pady=(4, 0))

        FlatButton(
            head, text="↻  Sincronizar stock", command=self.refresh_stock,
            bg=Palette.SURFACE, hover_bg=Palette.CARD_HOVER, fg=Palette.TEXT_MUTED,
            font=Fonts.SMALL_BOLD, padx=12, pady=6,
        ).pack(side="right")

        # Tabla de productos (Treeview)
        table_wrap = tk.Frame(panel, bg=Palette.BORDER, padx=1, pady=1)
        table_wrap.grid(row=1, column=0, sticky="nsew")

        columns = ("id", "nombre", "cantidad", "precio", "stock")
        self.tree = ttk.Treeview(
            table_wrap, columns=columns, show="headings", style="Cart.Treeview", selectmode="browse", height=5
        )
        headings = {
            "id": ("ID", "center", 44, False),
            "nombre": ("PRODUCTO", "w", 230, True),
            "cantidad": ("CANT.", "center", 64, False),
            "precio": ("PRECIO", "e", 90, False),
            "stock": ("DISPONIBILIDAD", "center", 130, False),
        }
        for col, (title, anchor, width, stretch) in headings.items():
            self.tree.heading(col, text=title, anchor=anchor)
            self.tree.column(col, width=int(width * self._f), minwidth=int(width * self._f * 0.8),
                             anchor=anchor, stretch=stretch)

        self.tree.tag_configure("even", background=Palette.CARD)
        self.tree.tag_configure("odd", background="#1A1E2E")
        self.tree.tag_configure("agotado", foreground=Palette.DANGER)
        self.tree.tag_configure("bajo", foreground=Palette.ACCENT)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_summary())

        # Método de pago (perfiles de prueba)
        tk.Label(
            panel, text="MÉTODO DE PAGO  ·  PERFIL DE PRUEBA", bg=Palette.CARD,
            fg=Palette.TEXT_DIM, font=Fonts.SMALL_BOLD,
        ).grid(row=2, column=0, sticky="w", pady=(20, 8))

        profiles_row = tk.Frame(panel, bg=Palette.CARD)
        profiles_row.grid(row=3, column=0, sticky="ew")
        profiles_row.columnconfigure((0, 1), weight=1, uniform="profiles")

        self.profile_cards: Dict[int, SelectableCard] = {}
        for col, (uid, accent) in enumerate(((1, Palette.PRIMARY), (2, Palette.DANGER))):
            info = self.PROFILES[uid]
            card = SelectableCard(
                profiles_row,
                title=info["titulo"],
                subtitle=f"{info['metodo']}  ·  Usuario #{uid}",
                icon=info["icono"],
                accent=accent,
                on_select=lambda u=uid: self._select_profile(u),
            )
            card.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col == 0 else (0, 0))
            self.profile_cards[uid] = card

    def _build_summary_panel(self) -> None:
        """Panel derecho: resumen del producto seleccionado y botón de 1 Clic."""
        panel = Card(self, padding=20)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        tk.Label(panel, text="Resumen del pedido", bg=Palette.CARD, fg=Palette.TEXT,
                 font=Fonts.H2, anchor="w").grid(row=0, column=0, sticky="ew")

        # Producto seleccionado
        self.sel_name_lbl = tk.Label(panel, text="", bg=Palette.CARD, fg=Palette.TEXT, font=Fonts.H3,
                                     anchor="w", justify="left", wraplength=int(290 * self._f))
        self.sel_name_lbl.grid(row=1, column=0, sticky="ew", pady=(10, 2))
        self.sel_meta_lbl = tk.Label(panel, text="", bg=Palette.CARD, fg=Palette.TEXT_MUTED,
                                     font=Fonts.SMALL, anchor="w")
        self.sel_meta_lbl.grid(row=2, column=0, sticky="ew")

        # Selector de cantidad
        qty_row = tk.Frame(panel, bg=Palette.CARD)
        qty_row.grid(row=3, column=0, sticky="ew", pady=(10, 2))
        tk.Label(qty_row, text="Cantidad", bg=Palette.CARD, fg=Palette.TEXT_MUTED, font=Fonts.BODY).pack(side="left")

        stepper = tk.Frame(qty_row, bg=Palette.SURFACE, highlightthickness=1, highlightbackground=Palette.BORDER)
        stepper.pack(side="right")
        step_kwargs = dict(bg=Palette.SURFACE, hover_bg=Palette.CARD_HOVER, fg=Palette.TEXT,
                           font=(Fonts.FAMILY_BOLD, 12), padx=12, pady=2)
        FlatButton(stepper, text="−", command=lambda: self._change_qty(-1), **step_kwargs).pack(side="left")
        self.qty_lbl = tk.Label(stepper, text="1", width=3, bg=Palette.SURFACE, fg=Palette.TEXT, font=Fonts.H3)
        self.qty_lbl.pack(side="left")
        FlatButton(stepper, text="+", command=lambda: self._change_qty(1), **step_kwargs).pack(side="left")

        tk.Frame(panel, bg=Palette.BORDER, height=1).grid(row=4, column=0, sticky="ew", pady=10)

        # Desglose de precios
        breakdown = tk.Frame(panel, bg=Palette.CARD)
        breakdown.grid(row=5, column=0, sticky="ew")
        breakdown.columnconfigure(1, weight=1)
        self.unit_lbl = self._summary_row(breakdown, 0, "Precio unitario")
        self.subtotal_lbl = self._summary_row(breakdown, 1, "Subtotal")
        self._summary_row(breakdown, 2, "Envío", value="GRATIS", fg=Palette.PRIMARY)
        self.method_lbl = self._summary_row(breakdown, 3, "Pago con")

        tk.Frame(panel, bg=Palette.BORDER, height=1).grid(row=6, column=0, sticky="ew", pady=10)

        total_row = tk.Frame(panel, bg=Palette.CARD)
        total_row.grid(row=7, column=0, sticky="ew")
        tk.Label(total_row, text="Total a pagar", bg=Palette.CARD, fg=Palette.TEXT,
                 font=Fonts.H3).pack(side="left", anchor="s", pady=(0, 6))
        self.total_lbl = tk.Label(total_row, text="$0.00", bg=Palette.CARD, fg=Palette.PRIMARY, font=Fonts.PRICE)
        self.total_lbl.pack(side="right")

        # Botón principal "Pagar con 1 Clic"
        self.one_click_btn = FlatButton(panel, text="⚡  Pagar con 1 Clic", command=self._handle_one_click_checkout)
        self.one_click_btn.grid(row=8, column=0, sticky="ew", pady=(14, 8))

        # Alerta inline (errores / progreso)
        self.alert_lbl = tk.Label(panel, text="", bg=Palette.CARD, fg=Palette.TEXT_MUTED, font=Fonts.SMALL,
                                  anchor="w", justify="left", wraplength=int(290 * self._f), padx=12, pady=8)
        self.alert_lbl.grid(row=9, column=0, sticky="ew")
        self.alert_lbl.grid_remove()

        tk.Label(panel, text="🔒  Pago cifrado  ·  Token de tarjeta protegido con hash",
                 bg=Palette.CARD, fg=Palette.TEXT_DIM, font=Fonts.SMALL).grid(row=10, column=0, pady=(6, 0))

    @staticmethod
    def _summary_row(parent: tk.Frame, row: int, label: str, value: str = "", fg: str = Palette.TEXT) -> tk.Label:
        tk.Label(parent, text=label, bg=Palette.CARD, fg=Palette.TEXT_MUTED, font=Fonts.BODY).grid(
            row=row, column=0, sticky="w", pady=2
        )
        value_lbl = tk.Label(parent, text=value, bg=Palette.CARD, fg=fg, font=Fonts.H3)
        value_lbl.grid(row=row, column=1, sticky="e", pady=2)
        return value_lbl

    # ------------------------------------------------------------------ #
    # Datos y estado
    # ------------------------------------------------------------------ #
    def _render_products(self) -> None:
        """Pinta los productos en el Treeview conservando la selección actual."""
        selected_id = self._selected_product()["id"] if self.tree.selection() else None
        self.tree.delete(*self.tree.get_children())

        for index, product in enumerate(self.products):
            stock = product["stock"]
            if stock <= 0:
                disponibilidad, tag = "● Agotado", "agotado"
            elif stock <= 5:
                disponibilidad, tag = f"● Últimas {stock}", "bajo"
            else:
                disponibilidad, tag = f"● {stock} en stock", ""

            tags = ("even" if index % 2 == 0 else "odd",) + ((tag,) if tag else ())
            self.tree.insert(
                "", "end", iid=str(product["id"]), tags=tags,
                values=(product["id"], product["nombre"], product["cantidad"],
                        f"${product['precio']:,.2f}", disponibilidad),
            )

        target = str(selected_id) if selected_id is not None else str(self.products[0]["id"])
        self.tree.selection_set(target)
        self.tree.focus(target)
        self.items_lbl.configure(text=f"{len(self.products)} productos")
        self._update_summary()

    def _selected_product(self) -> Dict[str, Any]:
        selection = self.tree.selection()
        product_id = int(selection[0]) if selection else self.products[0]["id"]
        return next(p for p in self.products if p["id"] == product_id)

    def _change_qty(self, delta: int) -> None:
        product = self._selected_product()
        product["cantidad"] = max(1, min(self.MAX_QTY, product["cantidad"] + delta))
        self.tree.set(str(product["id"]), "cantidad", product["cantidad"])
        self._update_summary()

    def _select_profile(self, usuario_id: int) -> None:
        self.usuario_id = usuario_id
        for uid, card in self.profile_cards.items():
            card.set_selected(uid == usuario_id)
        self._update_summary()

    def _update_summary(self) -> None:
        if not self.tree.get_children():
            return
        product = self._selected_product()
        total = product["precio"] * product["cantidad"]

        self.sel_name_lbl.configure(text=product["nombre"])
        stock_txt = "Agotado" if product["stock"] <= 0 else f"{product['stock']} disponibles"
        self.sel_meta_lbl.configure(text=f"SKU #{product['id']}  ·  {stock_txt}")
        self.qty_lbl.configure(text=str(product["cantidad"]))
        self.unit_lbl.configure(text=f"${product['precio']:,.2f}")
        self.subtotal_lbl.configure(text=f"${total:,.2f}")
        self.method_lbl.configure(text=self.PROFILES[self.usuario_id]["metodo"])
        self.total_lbl.configure(text=f"${total:,.2f}")
        self._hide_alert()

    def refresh_stock(self) -> bool:
        """Consulta GET /api/productos y actualiza el stock real (los ausentes = agotados)."""
        result = self.api_client.get_productos()
        online = bool(result["success"])
        if online:
            stock_by_id = {p["id"]: p["stock"] for p in result["data"] or []}
            for product in self.products:
                product["stock"] = stock_by_id.get(product["id"], 0)
            self._render_products()
        if self.on_connection_change:
            self.on_connection_change(online)
        return online

    # ------------------------------------------------------------------ #
    # Alertas inline
    # ------------------------------------------------------------------ #
    def _show_alert(self, message: str, kind: str = "error") -> None:
        colors = {
            "error": (Palette.DANGER_BG, Palette.DANGER, "✖  "),
            "info": (Palette.SURFACE, Palette.TEXT_MUTED, "⏳  "),
        }
        bg, fg, icon = colors[kind]
        self.alert_lbl.configure(text=f"{icon}{message}", bg=bg, fg=fg)
        self.alert_lbl.grid()

    def _hide_alert(self) -> None:
        self.alert_lbl.grid_remove()

    # ------------------------------------------------------------------ #
    # Flujo "Pagar con 1 Clic"
    # ------------------------------------------------------------------ #
    def _build_checkout_payload(self) -> Optional[Dict[str, Any]]:
        """Empaqueta los datos en el formato exacto de schemas.OneClickCheckoutRequest."""
        if not self.tree.get_children():
            return None
        product = self._selected_product()
        return {
            "usuario_id": self.usuario_id,
            "producto_id": int(product["id"]),
            "cantidad": int(product["cantidad"]),
        }

    def _handle_one_click_checkout(self) -> None:
        """Empaqueta el carrito y delega la petición POST al APIClient."""
        payload = self._build_checkout_payload()
        if payload is None:
            self._show_alert("El carrito está vacío.")
            return

        self.one_click_btn.set_enabled(False, text="Procesando pago...")
        self._show_alert("Conectando con la pasarela de pago...", kind="info")
        self.update_idletasks()

        result = self.api_client.process_one_click_checkout(payload)
        self.one_click_btn.set_enabled(True, text="⚡  Pagar con 1 Clic")

        if result["success"] and result["status_code"] == 200:
            self._hide_alert()
            product = self._selected_product()
            data = dict(result["data"] or {})
            data["_producto"] = product["nombre"]
            data["_cantidad"] = product["cantidad"]
            data["_metodo"] = self.PROFILES[self.usuario_id]["metodo"]
            if "stock_restante" in data:
                product["stock"] = data["stock_restante"]
                self._render_products()
            self.on_checkout_success(data)
        else:
            if result["status_code"] is None and self.on_connection_change:
                self.on_connection_change(False)
            self._show_alert(result.get("error") or "Error desconocido al procesar el pago.")

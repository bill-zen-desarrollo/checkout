"""Widgets personalizados con estilo moderno (botones planos con hover, tarjetas, pills)."""

import tkinter as tk
from typing import Any, Callable, Optional

from ui.theme import Fonts, Palette


class FlatButton(tk.Label):
    """Botón plano con efecto hover, cursor de mano y estado deshabilitado."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Optional[Callable[[], None]] = None,
        bg: str = Palette.PRIMARY,
        hover_bg: str = Palette.PRIMARY_HOVER,
        fg: str = "#06140F",
        font: Any = Fonts.BUTTON,
        padx: int = 24,
        pady: int = 14,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            text=text,
            bg=bg,
            fg=fg,
            font=font,
            padx=padx,
            pady=pady,
            cursor="hand2",
            **kwargs,
        )
        self._command = command
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._enabled = True

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def _on_enter(self, _event: tk.Event) -> None:
        if self._enabled:
            self.configure(bg=self._hover_bg)

    def _on_leave(self, _event: tk.Event) -> None:
        if self._enabled:
            self.configure(bg=self._bg)

    def _on_click(self, _event: tk.Event) -> None:
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, enabled: bool, text: Optional[str] = None) -> None:
        """Habilita/deshabilita el botón cambiando su apariencia."""
        self._enabled = enabled
        if text is not None:
            self.configure(text=text)
        if enabled:
            self.configure(bg=self._bg, fg=self._fg, cursor="hand2")
        else:
            self.configure(bg=Palette.BORDER, fg=Palette.TEXT_MUTED, cursor="watch")


class Card(tk.Frame):
    """Contenedor tipo tarjeta con fondo elevado y borde sutil."""

    def __init__(
        self,
        master: tk.Misc,
        bg: str = Palette.CARD,
        border: str = Palette.BORDER,
        padding: int = 20,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            bg=bg,
            highlightbackground=border,
            highlightcolor=border,
            highlightthickness=1,
            padx=padding,
            pady=padding,
            **kwargs,
        )


class Pill(tk.Label):
    """Etiqueta redondeada visualmente (badge) para estados y promociones."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        bg: str = Palette.ACCENT,
        fg: str = "#1A1200",
        font: Any = Fonts.SMALL_BOLD,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, text=text, bg=bg, fg=fg, font=font, padx=10, pady=3, **kwargs)


class SelectableCard(tk.Frame):
    """Tarjeta seleccionable (tipo radio button) usada para elegir el perfil de pago."""

    def __init__(
        self,
        master: tk.Misc,
        title: str,
        subtitle: str,
        icon: str,
        accent: str,
        on_select: Callable[[], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            bg=Palette.CARD,
            highlightthickness=2,
            highlightbackground=Palette.BORDER,
            cursor="hand2",
            padx=14,
            pady=10,
            **kwargs,
        )
        self._accent = accent
        self._selected = False
        self._on_select = on_select

        self.icon_lbl = tk.Label(self, text=icon, bg=Palette.CARD, fg=accent, font=("Segoe UI Emoji", 18))
        self.icon_lbl.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 12))

        self.title_lbl = tk.Label(self, text=title, bg=Palette.CARD, fg=Palette.TEXT, font=Fonts.H3, anchor="w")
        self.title_lbl.grid(row=0, column=1, sticky="w")

        self.subtitle_lbl = tk.Label(
            self, text=subtitle, bg=Palette.CARD, fg=Palette.TEXT_MUTED, font=Fonts.SMALL, anchor="w"
        )
        self.subtitle_lbl.grid(row=1, column=1, sticky="w")

        self.check_lbl = tk.Label(self, text="○", bg=Palette.CARD, fg=Palette.TEXT_DIM, font=(Fonts.FAMILY, 16))
        self.check_lbl.grid(row=0, column=2, rowspan=2, sticky="e", padx=(12, 0))
        self.columnconfigure(1, weight=1)

        for widget in (self, self.icon_lbl, self.title_lbl, self.subtitle_lbl, self.check_lbl):
            widget.bind("<ButtonRelease-1>", lambda _e: self._on_select())
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _paint(self, bg: str) -> None:
        for widget in (self, self.icon_lbl, self.title_lbl, self.subtitle_lbl, self.check_lbl):
            widget.configure(bg=bg)

    def _on_enter(self, _event: tk.Event) -> None:
        if not self._selected:
            self._paint(Palette.CARD_HOVER)

    def _on_leave(self, _event: tk.Event) -> None:
        if not self._selected:
            self._paint(Palette.CARD)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        if selected:
            self.configure(highlightbackground=self._accent)
            self.check_lbl.configure(text="●", fg=self._accent)
            self._paint(Palette.CARD_HOVER)
        else:
            self.configure(highlightbackground=Palette.BORDER)
            self.check_lbl.configure(text="○", fg=Palette.TEXT_DIM)
            self._paint(Palette.CARD)

"""Paleta de colores y tipografías de la marca checkout (Black Friday Edition)."""

import tkinter as tk


def dpi_factor(widget: tk.Misc) -> float:
    """Factor de escala respecto a 96 DPI (1.0 = 100 %, 1.25 = 125 %, etc.).

    Las fuentes de Tk se escalan solas con el DPI de Windows, pero las medidas en
    píxeles (anchos de columna, wraplength, alturas) no; este factor las ajusta.
    """
    try:
        return max(1.0, float(widget.tk.call("tk", "scaling")) / (96 / 72))
    except tk.TclError:
        return 1.0


class Palette:
    """Colores centralizados para mantener consistencia visual en todas las vistas."""

    # Fondos (de más oscuro a más claro)
    BG = "#0E1018"
    HEADER = "#090B11"
    SURFACE = "#161926"
    CARD = "#1D2133"
    CARD_HOVER = "#252A40"
    BORDER = "#2C3149"

    # Texto
    TEXT = "#F4F5FA"
    TEXT_MUTED = "#8B90A7"
    TEXT_DIM = "#5D627A"

    # Marca y estados
    PRIMARY = "#00D68F"        # Verde checkout
    PRIMARY_HOVER = "#00F0A0"
    PRIMARY_DARK = "#00A36C"
    SECONDARY = "#4C6FFF"      # Azul eléctrico
    ACCENT = "#FFB020"         # Dorado Black Friday
    DANGER = "#FF4D6A"
    DANGER_BG = "#3A1A24"
    SUCCESS_BG = "#0F3328"

    # Degradado del banner Black Friday
    GRADIENT_START = "#7B2FF7"
    GRADIENT_END = "#F107A3"


class Fonts:
    """Tipografías basadas en Segoe UI (nativa en Windows)."""

    FAMILY = "Segoe UI"
    FAMILY_BOLD = "Segoe UI Semibold"
    FAMILY_BLACK = "Segoe UI Black"

    BRAND = (FAMILY_BOLD, 20)
    HERO = (FAMILY_BLACK, 30)
    H1 = (FAMILY_BOLD, 22)
    H2 = (FAMILY_BOLD, 15)
    H3 = (FAMILY_BOLD, 12)
    BODY = (FAMILY, 11)
    SMALL = (FAMILY, 9)
    SMALL_BOLD = (FAMILY_BOLD, 9)
    PRICE = (FAMILY_BOLD, 26)
    BUTTON = (FAMILY_BOLD, 14)
    MONO = ("Consolas", 12)

"""Generación programática del logo de checkout y recursos gráficos con Pillow.

Se dibuja todo con supersampling (8x) y luego se reduce con LANCZOS para obtener
bordes suaves (antialiasing) sin depender de archivos de imagen externos.
"""

from functools import lru_cache
from typing import Tuple

from PIL import Image, ImageDraw, ImageTk

from ui.theme import Palette

_SUPERSAMPLE = 8
_BASE = 100  # Lienzo lógico de 100x100 unidades


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _gradient(size: Tuple[int, int], start: str, end: str, angle: int = 0) -> Image.Image:
    """Crea un degradado lineal RGBA entre dos colores (angle=0 → horizontal, 45 → diagonal)."""
    vertical = Image.linear_gradient("L")            # 0 arriba → 255 abajo
    horizontal = vertical.rotate(90)                 # 0 derecha → 255 izquierda
    mask = Image.blend(horizontal, vertical.rotate(180), 0.5) if angle == 45 else horizontal
    mask = mask.resize(size)
    img_start = Image.new("RGBA", size, _hex_to_rgb(start) + (255,))
    img_end = Image.new("RGBA", size, _hex_to_rgb(end) + (255,))
    return Image.composite(img_start, img_end, mask)


def _stroke(draw: ImageDraw.ImageDraw, points, width: float, fill, s: int) -> None:
    """Dibuja una polilínea con extremos redondeados (round caps)."""
    scaled = [(x * s, y * s) for x, y in points]
    w = int(width * s)
    draw.line(scaled, fill=fill, width=w, joint="curve")
    r = w / 2
    for x, y in (scaled[0], scaled[-1]):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


@lru_cache(maxsize=8)
def build_logo_pil(size: int = 48) -> Image.Image:
    """Logo de checkout: carrito blanco con check sobre un squircle degradado verde → azul."""
    s = _SUPERSAMPLE
    canvas_px = _BASE * s

    # Fondo: squircle con degradado diagonal
    background = _gradient((canvas_px, canvas_px), Palette.PRIMARY, Palette.SECONDARY, angle=45)
    mask = Image.new("L", (canvas_px, canvas_px), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, canvas_px - 1, canvas_px - 1), radius=26 * s, fill=255
    )
    logo = Image.new("RGBA", (canvas_px, canvas_px), (0, 0, 0, 0))
    logo.paste(background, (0, 0), mask)

    draw = ImageDraw.Draw(logo)
    white = (255, 255, 255, 255)

    # Asa y base del carrito
    _stroke(draw, [(15, 27), (26, 27), (35, 64), (76, 64)], width=7, fill=white, s=s)

    # Canasta del carrito (rellena)
    draw.polygon(
        [(30 * s, 35 * s), (85 * s, 35 * s), (78 * s, 57 * s), (35 * s, 57 * s)],
        fill=white,
    )

    # Check dentro de la canasta (símbolo de compra confirmada)
    _stroke(draw, [(46, 46), (53, 52), (67, 40)], width=5.5, fill=_hex_to_rgb(Palette.PRIMARY_DARK), s=s)

    # Ruedas
    for cx, cy in ((42, 77), (71, 77)):
        r = 6.5 * s
        draw.ellipse((cx * s - r, cy * s - r, cx * s + r, cy * s + r), fill=white)

    return logo.resize((size, size), Image.LANCZOS)


def build_logo(size: int = 48) -> ImageTk.PhotoImage:
    """Retorna el logo como PhotoImage listo para usar en widgets Tkinter."""
    return ImageTk.PhotoImage(build_logo_pil(size))


def build_gradient_banner(width: int, height: int, radius: int = 18) -> ImageTk.PhotoImage:
    """Banner horizontal con degradado púrpura → magenta y esquinas redondeadas."""
    width, height = max(width, 2), max(height, 2)
    s = 2
    banner = _gradient((width * s, height * s), Palette.GRADIENT_START, Palette.GRADIENT_END)

    # Destellos decorativos (círculos translúcidos)
    overlay = Image.new("RGBA", banner.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    w, h = banner.size
    od.ellipse((w * 0.72, -h * 0.6, w * 0.72 + h * 1.6, h * 1.0), fill=(255, 255, 255, 28))
    od.ellipse((w * 0.86, h * 0.35, w * 0.86 + h * 1.2, h * 1.55), fill=(255, 255, 255, 20))
    od.ellipse((w * 0.55, h * 0.55, w * 0.55 + h * 0.7, h * 1.25), fill=(255, 255, 255, 14))
    banner = Image.alpha_composite(banner, overlay)

    # Esquinas redondeadas fundidas con el color de fondo de la app
    mask = Image.new("L", banner.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius * s, fill=255)
    final = Image.new("RGBA", banner.size, _hex_to_rgb(Palette.BG) + (255,))
    final.paste(banner, (0, 0), mask)

    return ImageTk.PhotoImage(final.resize((width, height), Image.LANCZOS))


def build_success_badge(size: int = 110) -> ImageTk.PhotoImage:
    """Insignia circular con check para la pantalla de orden confirmada."""
    s = _SUPERSAMPLE
    px = _BASE * s
    img = Image.new("RGBA", (px, px), _hex_to_rgb(Palette.BG) + (255,))
    draw = ImageDraw.Draw(img)

    # Halo exterior
    draw.ellipse((0, 0, px - 1, px - 1), fill=_hex_to_rgb(Palette.SUCCESS_BG) + (255,))
    # Círculo principal con degradado
    inner = _gradient((px, px), Palette.PRIMARY, Palette.PRIMARY_DARK, angle=45)
    mask = Image.new("L", (px, px), 0)
    ImageDraw.Draw(mask).ellipse((14 * s, 14 * s, 86 * s, 86 * s), fill=255)
    img.paste(inner, (0, 0), mask)

    _stroke(draw, [(33, 51), (45, 63), (68, 39)], width=8, fill=(255, 255, 255, 255), s=s)
    return ImageTk.PhotoImage(img.resize((size, size), Image.LANCZOS))

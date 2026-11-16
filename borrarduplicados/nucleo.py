"""Busca fotos iguales o parecidas.

Cada foto recibe una huella visual (dHash de 64 bits): una miniatura de 9×8 en gris donde
cada bit dice si un píxel es más claro que su vecino. Dos fotos con huellas que difieren en
pocos bits se ven iguales aunque tengan otro tamaño, otra calidad u otro formato.
Con «Idénticas» se compara en cambio el contenido exacto del archivo.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageOps

EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

# Bits de diferencia aceptados entre huellas; None = mismo contenido exacto.
SENSIBILIDAD: dict[str, int | None] = {
    "Idénticas (copias exactas)": None,
    "Muy parecidas (recomendado)": 4,
    "Parecidas (más resultados, revisa bien)": 10,
}


@dataclass
class Foto:
    ruta: Path
    tamano: int
    fecha: float
    ancho: int = 0
    alto: int = 0
    huella: int = 0

    @property
    def pixeles(self) -> int:
        return self.ancho * self.alto


def huella(img: Image.Image) -> int:
    g = ImageOps.exif_transpose(img).convert("L").resize((9, 8), Image.LANCZOS).tobytes()
    bits = 0
    for f in range(8):
        for c in range(8):
            bits = bits << 1 | (g[f * 9 + c] > g[f * 9 + c + 1])
    return bits


def leer(ruta: Path, con_huella: bool = True) -> Foto:
    st = ruta.stat()
    with Image.open(ruta) as img:
        ancho, alto = img.size
        if img.getexif().get(0x0112, 1) in (5, 6, 7, 8):  # foto girada 90° según la cámara
            ancho, alto = alto, ancho
        if not con_huella:
            return Foto(ruta, st.st_size, st.st_mtime, ancho, alto)
        img.draft("RGB", (128, 128))  # JPEG: decodifica a tamaño reducido, mucho más rápido
        return Foto(ruta, st.st_size, st.st_mtime, ancho, alto, huella(img))


def recolectar(carpetas: Iterable[Path]) -> list[Path]:
    vistas: set[Path] = set()
    for base in carpetas:
        for raiz, dirs, archivos in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith(".")]  # papelera, cachés, .git…
            for a in archivos:
                r = Path(raiz) / a
                if r.suffix.lower() in EXTENSIONES and not r.is_symlink():
                    vistas.add(r.resolve())
    return sorted(vistas)


def _sha1(ruta: Path) -> str:
    h = hashlib.sha1()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def agrupar(fotos: list[Foto], umbral: int | None) -> list[list[Foto]]:
    """Grupos de 2 o más fotos; la primera de cada grupo es la que conviene conservar."""
    if umbral is None:
        por_tamano: dict[int, list[Foto]] = {}
        for f in fotos:
            por_tamano.setdefault(f.tamano, []).append(f)
        grupos_d: dict[str, list[Foto]] = {}
        for mismos in por_tamano.values():
            if len(mismos) > 1:
                for f in mismos:
                    grupos_d.setdefault(_sha1(f.ruta), []).append(f)
        grupos = list(grupos_d.values())
    else:
        # shortcut: compara todas contra todas (n²/2); va bien hasta ~20 000 fotos, más allá usar un BK-tree
        padre = list(range(len(fotos)))

        def raiz(i: int) -> int:
            while padre[i] != i:
                padre[i] = padre[padre[i]]
                i = padre[i]
            return i

        hs = [f.huella for f in fotos]
        for i, a in enumerate(hs):
            for j in range(i + 1, len(hs)):
                if (a ^ hs[j]).bit_count() <= umbral:
                    padre[raiz(j)] = raiz(i)
        por_raiz: dict[int, list[Foto]] = {}
        for i, f in enumerate(fotos):
            por_raiz.setdefault(raiz(i), []).append(f)
        grupos = list(por_raiz.values())
    grupos = [sorted(g, key=orden_calidad) for g in grupos if len(g) > 1]
    return sorted(grupos, key=lambda g: str(g[0].ruta).lower())


def orden_calidad(f: Foto):
    """Mejor primero: más resolución, archivo más grande (menos compresión), la más antigua."""
    return (-f.pixeles, -f.tamano, f.fecha, str(f.ruta))


def buscar(carpetas: Iterable[Path], umbral: int | None,
           avance: Callable[[int, int, str], None] | None = None,
           cancelado: Callable[[], bool] | None = None) -> tuple[list[list[Foto]], list[str]]:
    """(grupos de duplicados, archivos que no se pudieron leer)."""
    rutas = recolectar(carpetas)
    fotos: list[Foto] = []
    errores: list[str] = []
    for i, r in enumerate(rutas):
        if cancelado and cancelado():
            return [], errores
        if avance and i % 10 == 0:
            avance(i, len(rutas), str(r))
        try:
            fotos.append(leer(r, con_huella=umbral is not None))
        except Exception:
            errores.append(str(r))
    if avance:
        avance(len(rutas), len(rutas), "Comparando…")
    return agrupar(fotos, umbral), errores

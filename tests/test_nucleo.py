import random
import shutil
from pathlib import Path

from PIL import Image

from borrarduplicados import nucleo


def foto_falsa(semilla: int) -> Image.Image:
    """Imagen suave (cuadrícula aleatoria ampliada), como una foto: resiste reducirla o comprimirla."""
    rnd = random.Random(semilla)
    chica = Image.new("RGB", (8, 6))
    chica.putdata([tuple(rnd.randrange(256) for _ in range(3)) for _ in range(48)])
    return chica.resize((800, 600), Image.BILINEAR)


def escenario(tmp_path: Path) -> dict[str, Path]:
    a = foto_falsa(1)
    r = {
        "original": tmp_path / "viaje" / "IMG_001.png",
        "copia": tmp_path / "viaje" / "copia" / "IMG_001 (1).png",
        "chica": tmp_path / "whatsapp" / "IMG-WA0001.png",
        "jpg": tmp_path / "whatsapp" / "foto.jpg",
        "otra": tmp_path / "viaje" / "IMG_002.png",
        "oculta": tmp_path / ".cache" / "IMG_001.png",
    }
    for p in r.values():
        p.parent.mkdir(parents=True, exist_ok=True)
    a.save(r["original"])
    shutil.copy(r["original"], r["copia"])
    a.resize((400, 300)).save(r["chica"])
    a.save(r["jpg"], quality=40)
    foto_falsa(2).save(r["otra"])
    a.save(r["oculta"])
    (tmp_path / "notas.txt").write_text("no es foto")
    (tmp_path / "rota.jpg").write_bytes(b"no es un jpg")
    return r


def test_parecidas_agrupa_copias_reducidas_y_recomprimidas(tmp_path):
    r = escenario(tmp_path)
    grupos, errores = nucleo.buscar([tmp_path], nucleo.SENSIBILIDAD["Muy parecidas (recomendado)"])
    assert len(grupos) == 1
    rutas = [f.ruta for f in grupos[0]]
    assert set(rutas) == {r["original"].resolve(), r["copia"].resolve(), r["chica"].resolve(), r["jpg"].resolve()}
    assert grupos[0][0].pixeles == 800 * 600  # se conserva una de resolución completa
    assert grupos[0][-1].ruta == r["chica"].resolve()  # la reducida, la última
    assert errores == [str((tmp_path / "rota.jpg").resolve())]  # el archivo dañado se informa, no rompe


def test_identicas_solo_copias_exactas(tmp_path):
    r = escenario(tmp_path)
    grupos, _ = nucleo.buscar([tmp_path], nucleo.SENSIBILIDAD["Idénticas (copias exactas)"])
    assert [sorted(f.ruta for f in g) for g in grupos] == [sorted([r["copia"].resolve(), r["original"].resolve()])]


def test_carpetas_repetidas_no_duplican_resultados(tmp_path):
    escenario(tmp_path)
    grupos, _ = nucleo.buscar([tmp_path, tmp_path / "viaje"], 4)
    assert len(grupos) == 1 and len(grupos[0]) == 4


def test_foto_girada_por_la_camara_cuenta_su_tamano_real(tmp_path):
    img = foto_falsa(3)
    exif = Image.Exif()
    exif[0x0112] = 6  # rotar 90°
    ruta = tmp_path / "girada.jpg"
    img.save(ruta, exif=exif)
    f = nucleo.leer(ruta)
    assert (f.ancho, f.alto) == (600, 800)

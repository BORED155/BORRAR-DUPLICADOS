"""Ventana principal: carpetas, sensibilidad, grupos de fotos con miniaturas y papelera."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, QSize, QStandardPaths, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QImage, QImageReader, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel,
                               QListWidget, QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from .. import nucleo

MINI = 150
NOMBRE_APP = "Borrar duplicados"
EXTRA = """
QFrame#tarjeta { background:white; border:1px solid #e2e8f0; border-radius:10px; }
QFrame#tarjeta[conservar="true"] { border:2px solid #16a34a; }
QFrame#tarjeta[borrar="true"] { border:2px solid #dc2626; }
QLabel#detalle { color:#64748b; font-size:9pt; }
QLabel#conservar { color:#15803d; font-weight:600; font-size:9pt; }
QPushButton#peligro { background:#dc2626; color:white; border:none; font-weight:600; padding:7px 16px; }
QPushButton#peligro:hover { background:#b91c1c; }
QPushButton#peligro:disabled { background:#fca5a5; }
QPushButton#principal { background:#2563eb; color:white; border:none; font-weight:600; padding:7px 16px; }
QPushButton#principal:hover { background:#1d4ed8; }
"""


def tamano_legible(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}".replace(".", ",")
        n /= 1024
    return ""


def miniatura(ruta: Path) -> QImage:
    r = QImageReader(str(ruta))
    r.setAutoTransform(True)  # respeta el giro de la cámara
    t = r.size()
    if t.isValid():
        r.setScaledSize(t.scaled(QSize(MINI, MINI), Qt.KeepAspectRatio))
    return r.read()


class Buscador(QThread):
    avance = Signal(int, int, str)
    listo = Signal(object, object, object)  # grupos, errores, miniaturas

    def __init__(self, carpetas: list[Path], umbral: int | None):
        super().__init__()
        self.carpetas, self.umbral = carpetas, umbral
        self.cancelar = False

    def run(self):
        grupos, errores = nucleo.buscar(self.carpetas, self.umbral, self.avance.emit, lambda: self.cancelar)
        minis: dict[Path, QImage] = {}
        total = sum(len(g) for g in grupos)
        for g in grupos:
            for f in g:
                if self.cancelar:
                    return self.listo.emit([], errores, {})
                if len(minis) % 10 == 0:
                    self.avance.emit(len(minis), total, "Preparando miniaturas…")
                minis[f.ruta] = miniatura(f.ruta)
        self.listo.emit(grupos, errores, minis)


class Tarjeta(QFrame):
    cambio = Signal()

    def __init__(self, foto: nucleo.Foto, mini: QImage, mejor: bool):
        super().__init__()
        self.foto = foto
        self.setObjectName("tarjeta")
        self.setProperty("conservar", mejor)
        self.setFixedWidth(MINI + 30)
        lay = QVBoxLayout(self)
        imagen = QLabel()
        imagen.setFixedSize(MINI, MINI)
        imagen.setAlignment(Qt.AlignCenter)
        if not mini.isNull():
            imagen.setPixmap(QPixmap.fromImage(mini))
        else:
            imagen.setText("(sin vista previa)")
        imagen.setCursor(Qt.PointingHandCursor)
        imagen.setToolTip(f"{foto.ruta}\n\nClic para abrir la foto")
        imagen.mousePressEvent = lambda _e: QDesktopServices.openUrl(QUrl.fromLocalFile(str(foto.ruta)))
        lay.addWidget(imagen, 0, Qt.AlignHCenter)
        nombre = QLabel(foto.ruta.name)
        nombre.setToolTip(str(foto.ruta))
        nombre.setFixedWidth(MINI)
        nombre.setText(nombre.fontMetrics().elidedText(foto.ruta.name, Qt.ElideMiddle, MINI))
        lay.addWidget(nombre)
        carpeta = QLabel()
        carpeta.setObjectName("detalle")
        carpeta.setToolTip(str(foto.ruta.parent))
        carpeta.setText(carpeta.fontMetrics().elidedText(str(foto.ruta.parent), Qt.ElideLeft, MINI))
        lay.addWidget(carpeta)
        detalle = QLabel(f"{foto.ancho}×{foto.alto} · {tamano_legible(foto.tamano)}")
        detalle.setObjectName("detalle")
        lay.addWidget(detalle)
        if mejor:
            et = QLabel("★ Mejor calidad")
            et.setObjectName("conservar")
            lay.addWidget(et)
        self.chk = QCheckBox("Borrar")
        self.chk.setChecked(not mejor)
        self.chk.toggled.connect(self._marcar)
        lay.addWidget(self.chk)
        self._marcar(self.chk.isChecked())

    def _marcar(self, borrar: bool):
        self.setProperty("borrar", borrar)
        self.style().unpolish(self)
        self.style().polish(self)
        self.cambio.emit()


class Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOMBRE_APP)
        self.resize(1100, 760)
        self.ajustes = QSettings()
        self.buscador: Buscador | None = None
        self.tarjetas: list[Tarjeta] = []
        self.cajas: list[QGroupBox] = []

        central = QWidget()
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(16, 12, 16, 12)

        arriba = QHBoxLayout()
        g = QGroupBox("Carpetas donde buscar")
        gl = QHBoxLayout(g)
        self.lista = QListWidget()
        self.lista.setMaximumHeight(90)
        guardadas = self.ajustes.value("carpetas", []) or []
        if not guardadas:
            fotos = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
            guardadas = [fotos] if fotos and Path(fotos).is_dir() else []
        self.lista.addItems([str(c) for c in (guardadas if isinstance(guardadas, list) else [guardadas])])
        gl.addWidget(self.lista, 1)
        botones = QVBoxLayout()
        b = QPushButton("Agregar…")
        b.clicked.connect(self._agregar)
        botones.addWidget(b)
        b = QPushButton("Quitar")
        b.clicked.connect(lambda: [self.lista.takeItem(self.lista.row(i)) for i in self.lista.selectedItems()])
        botones.addWidget(b)
        botones.addStretch(1)
        gl.addLayout(botones)
        arriba.addWidget(g, 3)

        g = QGroupBox("¿Qué tan parecidas?")
        gl = QVBoxLayout(g)
        self.cmb = QComboBox()
        self.cmb.addItems(list(nucleo.SENSIBILIDAD))
        self.cmb.setCurrentText(str(self.ajustes.value("sensibilidad", "Muy parecidas (recomendado)")))
        gl.addWidget(self.cmb)
        self.btn_buscar = QPushButton("Buscar duplicados")
        self.btn_buscar.setObjectName("principal")
        self.btn_buscar.clicked.connect(self._buscar)
        gl.addWidget(self.btn_buscar)
        arriba.addWidget(g, 2)
        raiz.addLayout(arriba)

        self.barra = QProgressBar()
        self.barra.setTextVisible(False)
        self.barra.setMaximumHeight(8)
        self.barra.hide()
        raiz.addWidget(self.barra)
        self.estado = QLabel("Elige las carpetas y pulsa «Buscar duplicados». No se borra nada sin que lo confirmes.")
        self.estado.setObjectName("detalle")
        raiz.addWidget(self.estado)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.contenido = QWidget()
        self.lay_grupos = QVBoxLayout(self.contenido)
        self.lay_grupos.addStretch(1)
        self.scroll.setWidget(self.contenido)
        raiz.addWidget(self.scroll, 1)

        abajo = QHBoxLayout()
        self.resumen = QLabel("")
        abajo.addWidget(self.resumen, 1)
        b = QPushButton("Desmarcar todo")
        b.clicked.connect(lambda: [t.chk.setChecked(False) for t in self.tarjetas])
        abajo.addWidget(b)
        self.btn_borrar = QPushButton("Mandar a la papelera")
        self.btn_borrar.setObjectName("peligro")
        self.btn_borrar.clicked.connect(self._borrar)
        abajo.addWidget(self.btn_borrar)
        raiz.addLayout(abajo)
        self._resumir()

    # --- búsqueda ---------------------------------------------------------------------

    def _agregar(self):
        c = QFileDialog.getExistingDirectory(self, "Carpeta donde buscar")
        if c and c not in self._carpetas_texto():
            self.lista.addItem(c)

    def _carpetas_texto(self) -> list[str]:
        return [self.lista.item(i).text() for i in range(self.lista.count())]

    def _buscar(self):
        if self.buscador:
            self.buscador.cancelar = True
            self.estado.setText("Deteniendo…")
            return
        carpetas = [Path(c) for c in self._carpetas_texto() if Path(c).is_dir()]
        if not carpetas:
            QMessageBox.information(self, NOMBRE_APP, "Agrega al menos una carpeta que exista.")
            return
        self.ajustes.setValue("carpetas", self._carpetas_texto())
        self.ajustes.setValue("sensibilidad", self.cmb.currentText())
        self._limpiar()
        self.buscador = Buscador(carpetas, nucleo.SENSIBILIDAD[self.cmb.currentText()])
        self.buscador.avance.connect(self._avance)
        self.buscador.listo.connect(self._mostrar)
        self.btn_buscar.setText("Detener")
        self.barra.show()
        self.barra.setRange(0, 0)
        self.estado.setText("Buscando fotos…")
        self.buscador.start()

    def _avance(self, i: int, total: int, texto: str):
        self.barra.setRange(0, max(total, 1))
        self.barra.setValue(i)
        self.estado.setText(f"{i:,} de {total:,} · {texto}".replace(",", "."))

    def _mostrar(self, grupos, errores, minis):
        cancelado = self.buscador.cancelar
        self.buscador.wait()
        self.buscador = None
        self.btn_buscar.setText("Buscar duplicados")
        self.barra.hide()
        for n, g in enumerate(grupos, 1):
            caja = QGroupBox(f"Grupo {n} · {len(g)} fotos")
            fila = QHBoxLayout(caja)
            for k, f in enumerate(g):
                t = Tarjeta(f, minis.get(f.ruta, QImage()), mejor=k == 0)
                t.cambio.connect(self._resumir)
                self.tarjetas.append(t)
                fila.addWidget(t)
            fila.addStretch(1)
            self.cajas.append(caja)
            self.lay_grupos.insertWidget(self.lay_grupos.count() - 1, caja)
        if cancelado:
            self.estado.setText("Búsqueda detenida.")
        elif not grupos:
            self.estado.setText("No se encontraron fotos repetidas. 🎉")
        else:
            self.estado.setText(f"{len(grupos)} grupo(s) de fotos repetidas. En cada grupo queda sin marcar la de "
                                "mejor calidad (borde verde); las marcadas en rojo irán a la papelera. Revísalas.")
        if errores:
            self.estado.setText(self.estado.text() + f"  ({len(errores)} archivo(s) no se pudieron leer.)")
        self._resumir()

    def _limpiar(self):
        for c in self.cajas:
            c.deleteLater()
        self.cajas, self.tarjetas = [], []
        self._resumir()

    def _resumir(self):
        marcadas = [t for t in self.tarjetas if t.chk.isChecked()]
        peso = sum(t.foto.tamano for t in marcadas)
        self.resumen.setText(f"Marcadas: {len(marcadas)} foto(s) · {tamano_legible(peso)}" if marcadas else
                             ("Nada marcado." if self.tarjetas else ""))
        self.btn_borrar.setEnabled(bool(marcadas) and self.buscador is None)

    # --- papelera ---------------------------------------------------------------------

    def _borrar(self):
        marcadas = [t for t in self.tarjetas if t.chk.isChecked()]
        if not marcadas:
            return
        sin_copia = [c for c in self.cajas if all(t.chk.isChecked() for t in c.findChildren(Tarjeta))]
        aviso = (f"\n\n⚠ En {len(sin_copia)} grupo(s) marcaste TODAS las fotos: no quedará ninguna copia."
                 if sin_copia else "")
        if QMessageBox.question(self, NOMBRE_APP, f"¿Mandar {len(marcadas)} foto(s) a la papelera?\n"
                                "Podrás recuperarlas desde la papelera." + aviso) != QMessageBox.Yes:
            return
        from PySide6.QtCore import QFile
        fallidas = []
        for t in marcadas:
            if QFile.moveToTrash(str(t.foto.ruta)):
                t.deleteLater()
                self.tarjetas.remove(t)
            else:
                fallidas.append(t.foto.ruta.name)
        for c in list(self.cajas):  # grupos que ya no tienen nada que comparar
            if sum(1 for t in self.tarjetas if t.parent() is c) < 2:
                for t in [t for t in self.tarjetas if t.parent() is c]:
                    self.tarjetas.remove(t)
                c.deleteLater()
                self.cajas.remove(c)
        movidas = len(marcadas) - len(fallidas)
        self.estado.setText(f"{movidas} foto(s) enviadas a la papelera.")
        if fallidas:
            QMessageBox.warning(self, NOMBRE_APP, f"No se pudieron mandar a la papelera {len(fallidas)} archivo(s):\n"
                                + "\n".join(fallidas[:10]) + ("\n…" if len(fallidas) > 10 else ""))
        self._resumir()

    def closeEvent(self, e):
        if self.buscador:
            self.buscador.cancelar = True
            self.buscador.wait()
        super().closeEvent(e)

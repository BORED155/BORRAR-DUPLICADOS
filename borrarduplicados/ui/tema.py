"""Tema visual (el mismo de Buscador Ágil, Descargas SRI, RESU y ATS): fondo claro, tarjetas blancas, bordes redondeados."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

TEMA = """
QWidget { font-size:10pt; color:#1f2937; }
QMainWindow, QDialog { background:#f3f5f9; }
QToolTip { background:#111827; color:white; border:none; padding:6px 8px; border-radius:6px; }
QStatusBar { color:#64748b; }

QGroupBox { background:white; border:1px solid #e2e8f0; border-radius:12px;
            margin-top:22px; padding:6px 10px 8px 10px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:4px; top:4px;
                   color:#475569; font-weight:600; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background:white; border:1px solid #cbd5e1; border-radius:8px;
                                 padding:5px 8px; selection-background-color:#2563eb; }
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover { border-color:#94a3b8; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border:1px solid #2563eb; }
QLineEdit:disabled { background:#f1f5f9; color:#94a3b8; }
QComboBox::drop-down { border:none; width:26px; }
QComboBox::down-arrow, QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image:url("@ABAJO@"); width:10px; height:10px; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image:url("@ARRIBA@"); width:10px; height:10px; }
QSpinBox, QDoubleSpinBox { padding-right:24px; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    border:none; background:transparent; width:22px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-position:top right; margin-top:3px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-position:bottom right; margin-bottom:3px; }
QComboBox QAbstractItemView { background:white; border:1px solid #e2e8f0; border-radius:8px;
                              selection-background-color:#eff6ff; selection-color:#1d4ed8; padding:4px; }

QPushButton, QToolButton { background:white; border:1px solid #cbd5e1; border-radius:8px;
                           padding:5px 14px; font-weight:500; }
QPushButton:hover, QToolButton:hover { background:#f8fafc; border-color:#94a3b8; }
QPushButton:pressed, QToolButton:pressed, QToolButton:checked { background:#e2e8f0; }
QPushButton:disabled { color:#94a3b8; background:#f8fafc; border-color:#e2e8f0; }

QCheckBox, QRadioButton { spacing:8px; }

QScrollBar:vertical { background:transparent; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:#cbd5e1; border-radius:4px; min-height:30px; }
QScrollBar:horizontal { background:transparent; height:10px; margin:2px; }
QScrollBar::handle:horizontal { background:#cbd5e1; border-radius:4px; min-width:30px; }
QScrollBar::handle:hover { background:#94a3b8; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }
"""


def aplicar_tema(app: QApplication, extra: str = "") -> None:
    """extra: reglas propias que se suman al tema (p. ej. las de los menús)."""
    app.setStyle("Fusion")
    pal = app.palette()
    pal.setColor(QPalette.Highlight, QColor("#2563eb"))  # casillas marcadas y selección
    pal.setColor(QPalette.Window, QColor("#f3f5f9"))
    pal.setColor(QPalette.Base, QColor("white"))
    pal.setColor(QPalette.Text, QColor("#1f2937"))
    pal.setColor(QPalette.WindowText, QColor("#1f2937"))
    pal.setColor(QPalette.ButtonText, QColor("#1f2937"))
    app.setPalette(pal)
    # flechas como SVG en la carpeta de datos: así no dependen de cómo se empaquete la app
    carpeta = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    flechas = {}
    for nombre, puntos in (("ABAJO", "1,3 5,7 9,3"), ("ARRIBA", "1,7 5,3 9,7")):
        ruta = carpeta / f"flecha-{nombre.lower()}.svg"
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
            ruta.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><polyline '
                            f'points="{puntos}" fill="none" stroke="#64748b" stroke-width="1.6" '
                            'stroke-linecap="round" stroke-linejoin="round"/></svg>', encoding="utf-8")
        except OSError:
            pass  # sin flechas dibujadas, pero las listas siguen funcionando
        flechas[nombre] = ruta.as_posix()
    app.setStyleSheet(TEMA.replace("@ABAJO@", flechas["ABAJO"]).replace("@ARRIBA@", flechas["ARRIBA"]) + extra)

"""Punto de entrada."""

from __future__ import annotations

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from .ui.tema import aplicar_tema
    from .ui.ventana import EXTRA, NOMBRE_APP, Ventana

    app = QApplication(sys.argv)
    app.setApplicationName(NOMBRE_APP)
    app.setOrganizationName("BorrarDuplicados")
    aplicar_tema(app, EXTRA)
    v = Ventana()
    v.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

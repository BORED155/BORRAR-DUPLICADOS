# Borrar duplicados

Encuentra **fotos iguales o parecidas** (copias, versiones reducidas, reenviadas por WhatsApp,
guardadas con otra calidad o formato) y manda las sobrantes a la **papelera**.

## Cómo se usa
1. Agrega las carpetas donde buscar (por defecto, *Imágenes*).
2. Elige qué tan parecidas:
   - **Idénticas**: solo copias exactas del mismo archivo.
   - **Muy parecidas** (recomendado): la misma foto con otro tamaño, calidad o formato.
   - **Parecidas**: también fotos casi iguales (ráfagas); revisa bien antes de borrar.
3. En cada grupo queda **sin marcar la de mejor calidad** (más resolución; borde verde).
   Las marcadas (borde rojo) van a la papelera al pulsar «Mandar a la papelera».
   Clic en una miniatura para abrir la foto.

Nada se borra sin confirmar, y todo va a la papelera: se puede recuperar.
Si en un grupo marcas todas las fotos, la app avisa antes.

Formatos: JPG, PNG, WEBP, BMP, GIF, TIFF. Se saltan carpetas ocultas (las que empiezan con punto).

## Cómo funciona
Cada foto recibe una huella visual de 64 bits (dHash): una miniatura de 9×8 en gris donde cada
bit dice si un píxel es más claro que su vecino. Fotos con huellas casi iguales se agrupan.
«Idénticas» compara en cambio el contenido exacto (SHA-1).

## Desarrollo
```
python3 -m venv .venv && .venv/bin/pip install -e .[dev]
.venv/bin/python -m pytest
.venv/bin/borrarduplicados
```
## Windows

Descarga **`BorrarDuplicados-instalador.exe`** desde [Releases](../../releases/latest), ábrelo y sigue
los pasos. No pide permisos de administrador, crea el acceso directo en el escritorio y se desinstala
desde «Agregar o quitar programas». Si Windows muestra «Windows protegió su PC», pulsa
*Más información → Ejecutar de todas formas* (el instalador no está firmado).

También hay una versión portable (`BorrarDuplicados-portable.zip`): descomprímela y abre
`BorrarDuplicados.exe`.

Para publicar una versión nueva: sube una etiqueta `v*` (por ejemplo `git tag v1.0.1 && git push --tags`).

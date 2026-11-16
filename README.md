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
Versión Windows: GitHub Actions → «Versión Windows» → Run workflow (o una etiqueta `v*`);
deja `BorrarDuplicados-windows.zip` como artefacto.

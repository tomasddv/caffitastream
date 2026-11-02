# Períodos de venta automáticos — DDV

El tablero permite ver solo dos períodos: **mes corriente** y **cierre del mes anterior**. La selección se actualiza automáticamente según la fecha de Argentina (ejemplo 02/11/2026 → noviembre progresivo y octubre cerrado). Todos los KPI, compras por promotor, ranking, alertas de combos y descargas respetan el período seleccionado. Los KPI siguen excluyendo CLIE PEOPLE del `reporte de clientes.xlsx`.

## Nombres de archivo en la carpeta de Drive `planificacion`

### Mes corriente (se sobreescriben periódicamente los datos, nunca el identificador de su archivo si es posible)

- `ventadiaria.txt`: volumen del mes actual.
- `ventadiaria bultos.txt`: bultos del **mismo mes y mismo corte**.

### Mes cerrado (se conservan los dos archivos)

- `ventadiaria octubre.txt`: volumen de octubre.
- `ventadiaria bultos octubre.txt`: bultos de octubre (también acepta `ventadiaria octubre bultos.txt`).

El sistema busca automáticamente estos nombres en la carpeta compartida a través de `gdown.download_folder(skip_download=True)`. Si el listado público falla, emplea únicamente IDs verificados para **noviembre/octubre de 2026**, y muestra una advertencia: no se adivinan IDs futuros.

No se calcula un período si contiene ventas de otro mes. Si los dos TXT del mes no corresponden al mismo conjunto de operaciones (fecha/cliente/SKU/importe), esa vista se bloquea; la otra permanece operativa.

## Advertencia importante en la situación actual

En Drive se comprobó `ventadiaria octubre.txt` (36.790 registros) pero no `ventadiaria bultos octubre.txt`. Para visualizar algo del cierre, el tablero presenta la opción con etiqueta **provisional** y calcula los CCC/TBD a partir de volúmenes (hL), usando signo del importe para los combos con volumen 0. Esta aproximación **no sustituye el informe definitivo**, sobre todo si existen bonificaciones a cero o devoluciones. Los campos de cantidad se etiquetan como volumen neto (hL), no como bultos.

**Para certificar el cierre, subí a esa carpeta el TXT de bultos de octubre** (exportado del mismo corte) con el nombre `ventadiaria bultos octubre.txt`. Entonces el tablero comprobará automáticamente las dos fuentes y mostrará el cierre validado, sin actualizar archivos de código ni seleccionar columnas.

Para el cambio de mes de diciembre, deberás conservar los TXT de noviembre como `ventadiaria noviembre.txt` y `ventadiaria bultos noviembre.txt`, y actualizar los TXT activos con las ventas de diciembre. Solo se consulta diciembre y noviembre; octubre deja de estar disponible en el selector.

## Validación del avance de noviembre

El 02/11/2026, los archivos activos registrados en Drive contienen **739 filas cada uno**, todas del 2 de noviembre de 2026, y la conciliación de operaciones coincide.

## Seguridad

No cambian `GITHUB_TOKEN`, `COMBO_EDITOR_PIN`, `GITHUB_REPO` ni `GITHUB_BRANCH` de Streamlit Secrets. No colocar tokens en los archivos públicos de GitHub. El guardado de componentes de combos conserva su funcionalidad.

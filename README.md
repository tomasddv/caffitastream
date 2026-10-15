# Tablero DDV — ventas automáticas desde Google Drive

## Apertura en Windows

1. Extraé **todo** el ZIP a una carpeta de Windows (no ejecutar el BAT dentro del ZIP).
2. Doble clic en **ABRIR_TABLERO.bat**.
3. El iniciador Python (iniciar_dashboard.py) elegirá automáticamente un puerto libre desde 8501 hasta 8599, sin comandos FOR /F de Windows. Consultá el enlace exacto que aparece en la ventana negra (por ejemplo, http://127.0.0.1:8502). El primer inicio requiere Python 3.10+ y conexión para instalar dependencias. No cierres la consola mientras uses el tablero.
4. El dashboard lee automáticamente **ventadiaria.txt** y **ventadiaria bultos.txt** directamente de tu carpeta Google Drive. Ninguna columna se elige a mano. Se lee al abrir y cuando presionás **Actualizar desde Drive**; se almacenan los resultados en caché durante hasta 5 minutos.

Los archivos deben continuar accesibles por el enlace de solo lectura de Google Drive. Si Drive bloquea un archivo o cambia el formato de CHESS, la aplicación detiene los cálculos y muestra un error en lugar de datos inválidos.

## Fuentes y reglas

- Drive: `ventadiaria.txt` y `ventadiaria bultos.txt` (IDs incluidos en `motor.py`). Se comprueba que coincidan los registros por fecha, cliente, código e importe para que no se mezclen cortes distintos.
- Se utilizan las **cantidades netas positivas** para validar la compra, nunca como magnitud de TBD UNG. **TBD UNG = número de pares únicos cliente–SKU comprado** (bultos no ponderan); las compras de combos aportan sus componentes identificados por código.
- Los clientes P1+P4 son los 942 códigos únicos de los dos padrones que enviaste. Objetivo 1890 = 941, cobertura del padrón = compradores únicos sobre 942.
- Un cliente que compra el mismo producto directo y/o a través de varios combos **cuenta una sola vez** para el KPI de cobertura.
- Se incluyen combos identificados en el catálogo histórico del proyecto DDV: por ejemplo Stella Pure Gold (900381, 900393, 900429, 900430, 900463), Michelob (900407), cervezas 0.0 (900399, 900461), Red Bull (900423, 900424, 900439, 900441, 900455, 900456) y latones (900299, 900311, 900428).
- Los códigos de combo cuyo contenido no está suficientemente definido **no se asignan por suposición** a todos los indicadores: aparecen en **Auditoría de combos incluidos y pendientes**.
- Un combo puede sumar un cliente en más de un indicador, sin duplicarse dentro del mismo.

## Qué está confirmado y qué falta

**Confirmado automáticamente:** lectura de columnas de CHESS, cruce de clientes, conteos de compradores directos, filtro de fecha, objetivos comerciales e inclusión de combos identificados. Las reglas se basan en códigos, marcas y catálogo de combos conocido, pero todavía deben cotejarse con el esquema comercial oficial para considerarlas resultados certificados.

**Pendiente de regla comercial:**

- **CCC INNOVACIONES CORE**: incluye Brahma 269 cc (15624), Quilmes Clásica 269 cc (63068) y Brahma FT sabores Limón y Pomelo, reconocidos automáticamente por marca, descripción y sabor cuando aparezcan en Drive. Cuenta **clientes únicos con compra neta positiva** (no bultos), conserva objetivo 376 y ofrece detalle descargable cliente-SKU. Los combos sólo se incluyen cuando sus componentes SKU están documentados en `combo_componentes.csv`; los combos sin desglose no se atribuyen por nombre.
- **TBD UNG**: objetivo 10.113 pares únicos `cliente + código SKU` de la unidad de negocio UNG, sin ponderar los bultos. Se incluyen SKU directos y componentes ERP conocidos de combos; cada par solo suma una vez. El Real se etiqueta **PARCIAL** mientras haya combos UNG con SKU componentes aún no documentados. Se muestra un detalle descargable cliente–SKU y una auditoría de combos pendientes.
- **Cobertura 1890 P1+P4**: los SKU directos 29740, 29743 y 51290 se detectaron en las ventas. No se agregan combos de latones cuyo contenido de 1890 no esté confirmado por composición.
- **Cobertura fuera de 1890**: el denominador/universo no está definido por las fuentes compartidas; se presenta `—` sin inventar un porcentaje.

## Archivos

- `app.py`: vista de Streamlit y descargas.
- `motor.py`: lectura automática y reglas de negocio.
- `padron.py`, `clientes_p1_p4.csv`: padrón deduplicado.
- `assets/`: diez imágenes de las familias tomadas de las capturas.
- `ABRIR_TABLERO.bat`: iniciador para Windows.
- `VISTA_PREVIA.html`: maqueta estática sin conexión a Drive; **no** muestra el Real automático, que solo funciona dentro de Streamlit.

## Pruebas

Motor ejecutado con los dos TXT descargados del 14/10/2026, **17.740 filas** cada uno, fuentes alineadas y 942 clientes en padrón. Los resultados pueden variar al actualizarse Drive. El motor no valida por sí mismo los KPI comerciales sin definiciones de producto.

## Corrección de inicio (14/10/2026)

Se eliminó el comando `for /f` de Windows que interpretaba incorrectamente las comillas de `.venv\Scripts\python.exe`. `ABRIR_TABLERO.bat` ahora invoca directamente `iniciar_dashboard.py`, y Python selecciona el puerto y lanza Streamlit mediante `subprocess` sin pasar por el intérprete de comandos.

## Ajuste TBD UNG — 14/10/2026

- Cuenta **distribución por código de SKU y cliente**, no cantidades, bultos ni el número de clientes únicos. Ej.: clientes con 2, 3 y 3 SKU diferentes generan un TBD de 8.
- Expande los siguientes combos de composición UNG documentada en ERP: 900398, 900438, 900439, 900440, 900441, 900444 (solo componentes UNG), 900455, 900456 y 900459.
- Si el mismo SKU fue comprado suelto y en combo, se deduplica.
- Descarga separada de `tbd_ung_cliente_sku.csv` y lista de combos de UNG cuyo contenido en códigos aún no está confirmado; por eso se informa **PARCIAL** cuando corresponda.

## Ajuste Innovaciones Core — 15/10/2026

- Productos: Quilmes Clásica 269 cc (SKU 63068), Brahma 269 cc (SKU 15624), Brahma FT Limón y Brahma FT Pomelo (códigos aún no visibles en el corte descargado).
- Identificación automática de nuevas ventas desde Drive por código para 269 y marca + FT/Fresh Twist + sabor para Brahma FT.
- Real: número de **clientes únicos** con compra neta positiva de esos productos. Un cliente comprador de varias innovaciones suma **1** en CCC Innovaciones Core.
- Auditoría detallada por cliente, SKU, familia y origen, descargable en CSV.
- Combos: únicamente se incluyen si `combo_componentes.csv` confirma SKU componentes de las innovaciones. El catálogo actual sólo desglosa el combo 900444 (sin innovaciones). Los otros combos no se atribuyen como innovaciones por su nombre.
- Para integrar cambios del `app.py` modificado localmente después de la versión que se entregó en el chat, enviá ese `app.py`: el script `audit_combos(1).py` compartido no contiene la aplicación Streamlit.

## Solapas por promotor y ranking — 15/10/2026

- **Indicadores generales:** conserva los diez KPI, objetivos, imágenes, conexión automática a Drive, desglose de innovaciones, TBD UNG por par cliente-SKU, detalle P1/P4 y auditoría.
- **CCC y TBD por promotor:** muestra los **diez KPI** sin selección manual de columnas. Agrupa por `Descripción Vendedor` de la venta, presenta alias comerciales de promotor, barras proporcionales, fila `Totales`, fila `Sin promotor` cuando hay registros sin asignación y descarga CSV.
- **Ranking:** permite elegir **uno de los diez indicadores**, muestra un gráfico horizontal, clasificación descendente, empates con el mismo puesto y descarga CSV; excluye la fila `Sin promotor` y la fila `Totales` de la competencia.
- **CCC:** comprador único para el período por promotor y KPI. **CCC 1890:** se filtra por los 942 clientes del padrón P1 + P4 antes de contar, igual que el tablero general.
- **TBD UNG:** par único `promotor, cliente, SKU`; los combos conocidos se expanden por SKU, sin sumar bultos. Las composiciones sin SKU confirmado permanecen pendientes; por lo tanto, el TBD puede ser parcial.
- **Totales:** la fila suma los resultados por promotor; si un cliente compró con más de un vendedor en el período, la suma de CCC por promotores puede ser mayor que la cobertura única general. No hay objetivos individuales por promotor; el ranking es por valor absoluto, no por cumplimiento porcentual.
- **Combos fotografiados en BEES:** aparecen varias ofertas presentes en el catálogo, incluidos Pepsi SUR, Mirinda SUR, Latas PAT SUR, GTD 750CC y Saborizadas. La fotografía no permite leer inequívocamente todos los códigos de artículo; por seguridad **no** se agregaron composiciones nuevas sin verificación de SKU en ERP/BEES.

### Pruebas realizadas

Nueve pruebas unitarias ejecutadas correctamente, incluidas la deduplicación del TBD y la exclusión de clientes ajenos al padrón 1890. Además se procesó el TXT de ventas disponible del corte 1–14/10/2026 y se comprobó que el resultado general 1890 de 524 compradores coincide con la suma por promotores en ese corte. La interfaz completa sigue necesitando una prueba de inicio en el Windows del usuario.


## Composiciones incorporadas (CHESS, capturas 15/10/2026)

- **900098, Gin Cortá la Sed**: 7476 Paso de los Toros Tónica x6 1,5 L (UNG) y 76363 Bosque Gin x4 500 cc (fuera de UNG). Suma 1 SKU al TBD UNG por cliente comprador.
- **900376, Gatorade K+T SEP**: 1418, 1422 y 11522 (tres SKU UNG por cliente).
- **900377, Gatorade AS SEP**: 1413, 1418, 1422 y 11522 (cuatro SKU UNG por cliente).

Las composiciones se registran en `combo_componentes.csv` y en la regla `COMBO_UNG_SKUS` de `motor.py`. La cantidad de bultos no multiplica el TBD. Si el cliente ya compró el SKU suelto o por otro combo, se deduplica.

**Atención:** 900098 y **900355 (Gin Cortá la Sed - Área Sur)** son códigos diferentes. Sólo se verificó el 900098 con estas capturas; no se supone la composición del 900355. Permanecen pendientes de verificar otros combos con desglose SKU incompleto.


## Ajuste visual — 15/10/2026

- **Texto negro** en las tres solapas, incluyendo títulos, tablas, filtros y avisos. Tema claro fijado en `.streamlit/config.toml`.
- **CCC y TBD por promotor**: cabeceras con los mismos diez PNG utilizados en Indicadores generales, conservando las barras de progreso y descarga CSV. La tabla tiene desplazamiento horizontal para que se lean bien las diez columnas.
- **Ranking**: se conserva el selector de los diez indicadores, la tabla ordenada con posiciones y la descarga. Se quita el gráfico independiente de barras y las métricas superiores; queda solo la tabla de resultados.
- Sin modificaciones al motor comercial, a los componentes de combos ni a las fuentes Drive.

## Actualización CHESS — 15/10/2026: ocho combos UNG verificados

Se integraron las composiciones de ocho combos, aportadas en capturas de la pestaña **Composición** de CHESS:

| Combo | Artículos que suman a TBD UNG |
| --- | --- |
| 900355 — Gin Cortá la Sed Área Sur | 7476 (tónica); **77979 gin no suma** |
| 900391 — Mirinda SUR | 591, 627, 22619 |
| 900392 — Gatorade 750 cc | 14624, 14625, 14638 |
| 900397 — Latas PAT SUR | 30481, 30648, 30793, 31074 (venta del combo expresada en unidades) |
| 900404 — Saborizadas | 29814, 29816 (ambos H2OH!; también aporta a CCC H2OH!) |
| 900408 — Pepsi SUR | 30644, 30645 |
| 900409 — 7UP PAT | 30972, 47489 |
| 900410 — 1500 cc PAT | 7475, 30644, 30972 |

Las composiciones detalladas están en `combo_componentes.csv` y el mapeo operativo del TBD está en `motor.py`. Las cantidades de bultos o unidades de cada artículo dentro del combo **no multiplican** el TBD; cada par cliente–SKU positivo suma una sola vez. Se mantienen las composiciones verificadas de 900098, 900376 y 900377.

**Validación sobre el archivo de ventas disponible del 01/10 al 15/10/2026:** TBD UNG antes 6.043; tras completar las ocho composiciones 6.276; 0 combos vendidos pendientes de desglose para este corte. Pueden incorporarse nuevos códigos de combos a Drive posteriormente; si carecen de composición, el dashboard volverá a marcar el resultado como parcial.

Para actualizar automáticamente las ventas, el tablero sigue descargando `ventadiaria.txt` y `ventadiaria bultos.txt` de Google Drive al abrir, tras vencer la caché o al pulsar **Actualizar desde Drive**. El **catálogo de composiciones** es local: requiere cargar una composición confirmada cada vez que aparezca un combo nuevo, y no se obtiene automáticamente de CHESS.

### Actualización — 1890 P1/P4 con nombre de fantasía y promotor

En Indicadores generales se agregó un filtro por promotor y por estado de compra para los clientes del padrón P1/P4. La app consulta `REPORTE DE CLIENTES.xlsx` desde la misma carpeta Google Drive de las ventas; cruza por **Cliente**, incorpora **Nombre de fantasia**, **Descripción personal comercial** y **Ruta de venta**, y permite descargar la lista filtrada o solamente clientes sin compra 1890. La ausencia de datos comerciales en el reporte se marca **Sin asignar** y no modifica el Real de ventas.

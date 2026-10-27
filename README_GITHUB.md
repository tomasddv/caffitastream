# DDV — versión con 3 solapas y catálogo de combos extensible

- **Solapas:** Indicadores generales · CCC/TBD por promotor · Ranking. Se eliminó la solapa de conciliación.
- **Conciliación técnica sin ajustes ficticios:** ver `AUDITORIA_CRITERIOS_Y_PENDIENTES.md`.
- **Composiciones nuevas:** añadir filas verificadas por CHESS a `combo_componentes.csv`. El motor las utiliza en CCC y TBD UNG, sin cambiar Python. Las contradicciones se rechazan.
- **Fuentes automáticas:** los 2 TXT de Drive y el reporte de clientes actualizado del 26/10.
- **Seguridad:** conservar el repositorio como privado por el padrón P1/P4.

---

# Control del informe 19/10/2026 y nuevos combos (26/10/2026)

- La solapa visual de conciliación fue eliminada. Los informes del 19/10 y 26/10 se guardan solo como controles de regresión fuera de la interfaz; los valores de las capturas no sustituyen los cálculos reales.
- Se reconoce **900465 COMBO SABORIZADAS - PATAGONIA** para **CCC H2OH!**. Su composición CHESS confirmada contiene SKU 29815 y 29816; se suma 1 comprador a H2OH y ambos SKU distintos al TBD UNG.
- Se reconoce **900470 COMBO BRAHMA FT** para **CCC Innovaciones Core** y Cervezas. Se computa 1 CCC por cliente con compra neta, sin adjudicar SKU de limón/pomelo no confirmados. El desglose de Innovaciones sigue mostrando solo SKUs confirmados.
- Composiciones CHESS confirmadas el 27/10: 900457 (3 SKU), 900465 (2 SKU), 900467 (3 SKU), 900469 (4 SKU). TBD UNG incorpora los SKU únicos por cliente, sin duplicados ni devoluciones netas.
- Con el padrón actual (940 clientes) y el desglose CHESS actualizado, el TBD UNG al 19/10 es **7.379**, igual al informe. Permanecen diferencias de Cervezas +1, 1890 −14 por padrón, Latones +1 y Core −1. **No** se ajustan cifras a mano.
- Se adjunta `CONCILIACION_19_10_2026.md` con hipótesis, causas comprobadas y limitaciones.
- El archivo original `19.10 avance de coberturas.xlsx` y el Excel completo de clientes **no** están incluidos en el repositorio por tamaño y confidencialidad. Solo se guarda una referencia de 10 totales en `control_referencia_19_10_2026.csv`.

---

# Actualización P1 + P4 — 26/10/2026

El padrón vigente contiene **940 clientes únicos** y reemplaza el archivo de 942 clientes que traía la versión anterior. Se incorporaron los dos Excel recibidos el 26/10/2026:

- `export (7).xlsx`: 52 clientes.
- `export (8).xlsx`: 888 clientes.
- Duplicados entre ambos: 0.
- Nuevos códigos: 0.
- Bajas respecto del padrón anterior: **3913** (FERNANDEZ RICARDO) y **5430** (CUMINAO TAMARA JUDITH).
- Cambio de razón social para el código **5299**: de DIAZ ROMINA VANESA a IGLESIAS NORBERTO MARTIN. Revisar comercialmente si corresponde actualizar también la ficha de cliente en CHESS.

`clientes_p1_p4.csv` fue reemplazado; `padron.py` sigue deduplicando y cruzando por código. Tanto el CCC 1890 general como su tabla filtrable por promotor y el ranking 1890 usan automáticamente el padrón actualizado cuando se despliega este proyecto. No cambia el objetivo **941** de 1890, ni las reglas de CLIE PEOPLE, combos o TBD. El porcentaje *Cobertura* divide compradores únicos entre el universo elegible actual, no entre el objetivo.

La actualización es un **padrón fijo** creado a partir de estos Excel; las ventas y `REPORTE DE CLIENTES` continúan consultándose de Drive automáticamente. Para incorporar nuevos cambios de universo P1/P4 deberá actualizarse `clientes_p1_p4.csv`.

---

## Combo Michelob 710 cc: nueva regla CCC (26/10/2026)

- **900472 — COMBO MICHELOB 3CAL - PATAGONIA - KT**: cada compra neta positiva de un cliente aporta a **CCC Michelob**, **CCC Latones** (710 cc) y **CCC Cervezas**, salvo que ese cliente ya esté contabilizado por otra compra dentro de cada indicador. La matriz por promotor y el ranking reutilizan exactamente las mismas reglas.
- **49827 — MICHELOB ULTRA CAN 4X4 710CC**: la venta individual también aporta a los mismos tres CCC. La vinculación del SKU 49827 al combo surge de la indicación comercial del usuario y del nombre y calibre observados en la fuente de ventas.
- En `combo_componentes.csv` se registra sólo el componente 49827 **como desglose parcial**. Todavía hace falta verificar en la pestaña *Composición* de CHESS qué otros SKU y cantidades integran los tres calibres del combo 900472. No se inventaron componentes ni hectolitros.
- Se conservan la exclusión `CLIE PEOPLE`, el padrón P1/P4, la actualización automática de Drive y las demás reglas. No se alteraron los objetivos.
- Verificación sobre la fuente disponible el 26/10/2026 (sin incluir las ventas fechadas el 27/10): **CCC Michelob 285 → 299**, **CCC Latones 787 → 790**, con 17 compradores elegibles del combo, excluyendo `CLIE PEOPLE`. Las cifras son sólo de ese corte y se actualizan con Drive.

## Exclusión automática CLIE PEOPLE (19/10/2026)

- La aplicación descarga también `REPORTE DE CLIENTES.xlsx` desde la carpeta de Drive existente.
- En **Descripcion subcanal** identifica exactamente `CLIE PEOPLE` (ignorando diferencias de mayúsculas y espacios). **No** utiliza la categoría impositiva.
- Se eliminan esos códigos de cliente **antes** de calcular cualquier KPI: los 10 indicadores generales, los pares cliente-SKU del TBD UNG (ventas individuales y combos), la vista por promotor, el ranking y las exportaciones.
- En Cobertura 1890 P1/P4 también se excluyen del padrón elegible si estuvieran presentes. Los objetivos comerciales originales se mantienen sin modificar.
- La app indica cuántos clientes CLIE PEOPLE detectó y cuántos correspondían al padrón. Se actualiza con las fuentes de Drive (caché de 5 minutos y botón Actualizar).
- **Seguridad de datos:** si REPORTE DE CLIENTES no puede descargarse o carece de la columna de subcanal, no se muestran números de KPI sin filtrar. Los clientes ausentes del reporte no se consideran CLIE PEOPLE por suposición.
- La app no guarda el Excel del reporte dentro del repositorio. El padrón `clientes_p1_p4.csv` sí se incluye: si contiene datos personales, utilizá repositorios y apps con controles de acceso adecuados.

# DDV — Indicadores comerciales (GitHub / Streamlit)

Este proyecto incluye los **10 indicadores DDV**, el seguimiento **CCC y TBD por promotor**, el **ranking**, imágenes de productos y los componentes de combos confirmados. Las ventas se leen desde los dos archivos TXT de Google Drive referenciados en `motor.py`.

## Publicar en GitHub

1. Extraé el ZIP **antes de subirlo**: GitHub no descomprime automáticamente un archivo ZIP que subís al repositorio.
2. Creá un repositorio **privado** (recomendado: `clientes_p1_p4.csv` contiene códigos y nombres de clientes).
3. Subí **todos los archivos y carpetas extraídos** en la raíz del repositorio; verificá que `app.py`, `motor.py` y `requirements.txt` queden al primer nivel, no dentro de una carpeta adicional.
4. Si lo desplegás en [Streamlit Community Cloud](https://share.streamlit.io/), elegí el repositorio y configurá **Main file path** como `app.py`. Recordá que el servidor donde se publique la aplicación necesita acceso HTTP a los archivos de Drive.
5. Si necesitás que la aplicación no sea pública, revisá las opciones de privacidad y autorización del despliegue antes de compartir su URL. **Un repositorio privado no implica automáticamente que la aplicación desplegada sea privada.**

## Ejecutar en Windows

Extraé el ZIP en una carpeta nueva y ejecutá `ABRIR_TABLERO.bat`. También podés ejecutar `python -m pip install -r requirements.txt` y `python -m streamlit run app.py`.

## Fuente de datos y confidencialidad

- Archivos remotos: `ventadiaria.txt` y `ventadiaria bultos.txt` (IDs en `motor.py`).
- El archivo `clientes_p1_p4.csv` contiene datos de clientes. No lo publiques en un repositorio público sin autorización.
- Los cálculos que dependan de desglose de combos deben mantener actualizado `combo_componentes.csv` y las reglas correspondientes en `motor.py`.
- La lectura remota requiere permisos válidos de Drive y acceso a Internet; el proyecto no almacena automáticamente copias de los TXT.

Consultá también el `README.md` para reglas de negocio, limitaciones y pruebas históricas.

## Gestión 1890 P1 + P4 por promotor (nuevo)

- La sección **Indicadores generales → 1890 · P1 y P4 | Gestión por promotor** cruza el padrón vigente de 940 clientes con el archivo **REPORTE DE CLIENTES.xlsx**, descargado directamente de Drive (ID definido en `reporte_clientes.py`).
- Se usa `Cliente` como clave de cruce, `Nombre de fantasia` como nombre comercial y `Fuerza de venta 1 Descripcion personal comercial` como promotor asignado. La ruta proviene de `Fuerza de venta 1 Ruta de venta`.
- Los filtros permiten escoger **promotor** y **Compró / No compró / Todos**. Dos descargas CSV: listado filtrado y solo clientes que no compraron 1890. El resumen por promotor muestra compraron, no compraron y cobertura.
- Las compras siguen calculándose únicamente a partir de las ventas del período seleccionado; los datos de asignación no cambian el Real de 1890. El reporte es una fotografía comercial y puede estar desactualizado frente a reasignaciones recientes.
- Si el reporte falla al descargarse o leerlo, la aplicación mantiene los otros indicadores, advierte el problema y no atribuye promotores sin evidencia.
- El Excel completo del reporte **no está incluido** en el ZIP ni se sube a GitHub. Los datos se descargan de Drive cuando se usa la aplicación (caché de 5 minutos y botón de actualizar).
- Validación del 15/10/2026: 941 de 942 códigos P1+P4 figuran en el reporte. El código 3840 no figura y tres clientes del reporte no tienen promotor asignado. Se muestran como **Sin asignar**, sin excluirlos.


## Actualización del 26/10/2026 y conciliación

- La fuente de cliente/razón social/subcanal/promotor ahora es **reporte de clientes.xlsx**, archivo nuevo de Google Drive ID `1VrxE5Tu1T_ruYkKf4eW3uiGoKlJcpCA6`, creado/actualizado el 26/10/2026. El reporte anterior, ID `1wMDck39W-Of-4HESCy6WXDWtnW02Swdz`, estaba actualizado por última vez el 22/09/2026 y no incluye las altas nuevas.
- El reporte nuevo contiene 2.152 códigos de cliente únicos, de los cuales 142 están clasificados como subcanal **CLIE PEOPLE**. El padrón P1/P4 de los dos export del 26/10 contiene **940** clientes y todos encuentran coincidencia en el reporte actualizado.
- Las referencias comerciales del **19/10** y **26/10** permanecen solo para pruebas y auditoría fuera de la aplicación; ya no hay pestaña de conciliación. El archivo `control_referencia_26_10_2026.csv` es una instantánea explícita de las diez metas y resultados leídos de las capturas, no una fuente que se actualice sola.
- El informe comercial muestra 957 clientes P1/P4, **17 más que los 940 del padrón vigente**; sus resultados no tienen por qué coincidir. Con los 957 clientes que figuraban en el informe del 19/10, el cálculo del 26/10 dio 684, mientras la captura oficial reporta 683.
- **No se falsean resultados** de Pure Gold, Cerveza, Sin Alcohol, Latones, Core o TBD para coincidir con el informe. Persisten diferencias por auditar; en TBD UNG ya se incorporaron las composiciones CHESS del 900457, 900465, 900467 y 900469. Las diferencias restantes requieren un análisis del informe por SKU y cliente. El combo 900473 de Brahma/Quilmes 269 se señala como pendiente de criterio de Core.
- El resto de las funcionalidades, filtros por promotor, ranking y descarga 1890 se conservan.

**Complemento comercial 26/10:** los combos 900466 (latones), 900471 (0.0% + Pure Gold) y 900473 (269 cc Core) se reconocen en los CCC por su composición familiar explícita. 900473 aporta 6 nuevos clientes a Core y el dashboard queda en 219, ante 217 de la referencia. No se estiman SKU individuales desconocidos.

## Actualización CHESS del 27/10/2026 · cuatro combos verificados

- `900457`: **16371**, **22256**, **32710** Red Bull. Nombre «4 SKUS» pero captura CHESS con **3 artículos** (8, 4 y 4 unidades; cero bultos).
- `900465`: **29815**, **29816**, dos H2OH! (1 bulto cada uno).
- `900467`: **1418**, **1422**, **11522**, tres Gatorade (1 bulto cada uno).
- `900469`: **25645**, **30663**, **30791**, **30974** (1 bulto cada uno).

Los cuatro se incluyen en TBD UNG por pares únicos **cliente+SKU** con compra neta positiva, deduplicados frente a compras directas y otros combos. Se conserva CCC H2OH! y CCC Red Bull; los objetivos permanecen iguales.

**Recálculo con `ventadiaria bultos.txt` exportado el 26/10 y reporte de clientes subido el 26/10** (corte por fecha de venta):

| Fecha | Informe oficial TBD UNG | Dashboard anterior | Dashboard con cuatro combos | Diferencia final |
|---|---:|---:|---:|---:|
| 19/10 | 7.379 | 7.341 | **7.379** | **0** |
| 26/10 | 8.932 | 8.798 | **8.938** | **+6** |

**La diferencia +6 del 26/10 sigue pendiente de conciliación por cliente y SKU.** No se fuerza el resultado a 8.932. El archivo `CATALOGO_CHESS_27_10.md` conserva el registro del desglose por unidades/bultos.

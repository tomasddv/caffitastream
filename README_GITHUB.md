# Control del informe 19/10/2026 y nuevos combos (26/10/2026)

- Nueva cuarta solapa **Control Excel 19/10**: confronta los 10 KPI del libro histórico del 19/10 con los TXT actuales filtrados del 1 al 19/10, usando las reglas vigentes y excluyendo CLIE PEOPLE. Descarga CSV del control.
- Se reconoce **900465 COMBO SABORIZADAS - PATAGONIA** para **CCC H2OH!**. Tiene componentes UNG pendientes de identificación (no se inventan SKU).
- Se reconoce **900470 COMBO BRAHMA FT** para **CCC Innovaciones Core** y Cervezas. Se computa 1 CCC por cliente con compra neta, sin adjudicar SKU de limón/pomelo no confirmados. El desglose de Innovaciones sigue mostrando solo SKUs confirmados.
- Se señalan como **pendientes para TBD UNG** los combos 900457, 900465, 900467 y 900469 al 19/10. El TBD no aumenta artificialmente por estos combos sin desglose de CHESS.
- Con el padrón actual (940 clientes), al 19/10 coinciden 5 KPI con el Excel comercial; quedan diferencias de Cervezas +1, 1890 -14 por padrón, Latones +1, Core -1 y TBD UNG -38 por conciliación pendiente de productos y distinta granularidad. **No** se ajustan las cifras a mano.
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
- La cuarta pestaña permite elegir las referencias comerciales del **19/10** (Excel) y **26/10** (capturas) y calcular de nuevo las ventas del día correspondiente. El archivo `control_referencia_26_10_2026.csv` es una instantánea explícita de las diez metas y resultados leídos de las capturas, no una fuente que se actualice sola.
- El informe comercial muestra 957 clientes P1/P4, **17 más que los 940 del padrón vigente**; sus resultados no tienen por qué coincidir. Con los 957 clientes que figuraban en el informe del 19/10, el cálculo del 26/10 dio 684, mientras la captura oficial reporta 683.
- **No se falsean resultados** de Pure Gold, Cerveza, Sin Alcohol, Latones, Core o TBD para coincidir con el informe. Persisten diferencias por auditar; en TBD UNG faltan las composiciones validadas de los combos 900457, 900465, 900467 y 900469. El combo 900473 de Brahma/Quilmes 269 se señala como pendiente de criterio de Core.
- El resto de las funcionalidades, filtros por promotor, ranking y descarga 1890 se conservan.

**Complemento comercial 26/10:** los combos 900466 (latones), 900471 (0.0% + Pure Gold) y 900473 (269 cc Core) se reconocen en los CCC por su composición familiar explícita. 900473 aporta 6 nuevos clientes a Core y el dashboard queda en 219, ante 217 de la referencia. No se estiman SKU individuales desconocidos.

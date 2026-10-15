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

- La sección **Indicadores generales → 1890 · P1 y P4 | Gestión por promotor** cruza el padrón de 942 clientes con el archivo **REPORTE DE CLIENTES.xlsx**, descargado directamente de Drive (ID definido en `reporte_clientes.py`).
- Se usa `Cliente` como clave de cruce, `Nombre de fantasia` como nombre comercial y `Fuerza de venta 1 Descripcion personal comercial` como promotor asignado. La ruta proviene de `Fuerza de venta 1 Ruta de venta`.
- Los filtros permiten escoger **promotor** y **Compró / No compró / Todos**. Dos descargas CSV: listado filtrado y solo clientes que no compraron 1890. El resumen por promotor muestra compraron, no compraron y cobertura.
- Las compras siguen calculándose únicamente a partir de las ventas del período seleccionado; los datos de asignación no cambian el Real de 1890. El reporte es una fotografía comercial y puede estar desactualizado frente a reasignaciones recientes.
- Si el reporte falla al descargarse o leerlo, la aplicación mantiene los otros indicadores, advierte el problema y no atribuye promotores sin evidencia.
- El Excel completo del reporte **no está incluido** en el ZIP ni se sube a GitHub. Los datos se descargan de Drive cuando se usa la aplicación (caché de 5 minutos y botón de actualizar).
- Validación del 15/10/2026: 941 de 942 códigos P1+P4 figuran en el reporte. El código 3840 no figura y tres clientes del reporte no tienen promotor asignado. Se muestran como **Sin asignar**, sin excluirlos.

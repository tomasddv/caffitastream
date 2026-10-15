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

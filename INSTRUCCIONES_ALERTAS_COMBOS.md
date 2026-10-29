# DDV · Alertas automáticas y carga de combos nuevos

## Qué hace
- Lee `ventadiaria bultos.txt` de Google Drive en cada actualización; la caché de lectura vence cada 5 minutos.
- Detecta automáticamente los códigos de combo `900xxx` con **compras netas positivas** que no están ni en `motor.py` ni en `combo_componentes.csv`.
- Muestra una **alerta visible** sobre las mismas tres solapas y otra en la barra lateral. No agrega una solapa de conciliación.
- La alerta considera el TXT completo, incluidos compradores CLIE PEOPLE; **los indicadores continúan excluyendo CLIE PEOPLE**.
- Permite seleccionar un combo, ingresar SKU separados por coma o salto de línea, autocompletar descripción, marca, calibre, división y unidad desde los productos reales de `ventadiaria`, corregir esos campos en una tabla editable y descargar o guardar la composición.
- El motor reclasifica automáticamente el combo en los CCC por las marcas/productos confirmados (Pure Gold, Michelob, latones, cerveza, Red Bull, H2OH!, etc.). En TBD UNG cuenta los pares **cliente + SKU de UNG**, sin duplicar compras directas o por distintos combos.

## Ejemplo del 29/10/2026
**900474 — COPIA COMBO PURE GOLD:** SKU **49807** (Pure Gold lata 473 cc) y **47707** (Pure Gold botella 330 cc), registrados según la descripción del usuario y los SKU encontrados en `ventadiaria`. Ambos aportan a CCC Pure Gold y CCC Cervezas, sin multiplicar el número de compradores.

El catálogo suministrado incluye esa clasificación. Se puede revisar y editar desde la app si CHESS muestra otra composición.

## Persistencia — importante para Streamlit Cloud
Streamlit Cloud no garantiza conservar cambios escritos al disco después de un reinicio. Por eso no se usa un CSV temporal como almacenamiento definitivo. Existen dos vías:

**A. Guardado directo (recomendado)**
1. Crear un **fine-grained Personal Access Token** en GitHub, limitado a `tomasddv/caffitastream`, con permiso **Contents: Read and write**. No subir el token a GitHub ni compartirlo por chat.
2. En la administración de la app de Streamlit Cloud, abrir **Settings → Secrets** y agregar el siguiente contenido, con valores privados propios:

   ```toml
   GITHUB_TOKEN = "PEGAR_EL_TOKEN_EN_STREAMLIT_SECRETS"
   COMBO_EDITOR_PIN = "ELEGIR_UN_PIN_LARGO_Y_PRIVADO"
   GITHUB_REPO = "tomasddv/caffitastream"
   GITHUB_BRANCH = "main"
   ```

3. Guardar secretos y reiniciar la app. En la sección `Registrar composición de combos`, completar los componentes, introducir el PIN y pulsar **Guardar composición permanentemente en GitHub**.
4. La app realiza un commit del archivo `combo_componentes.csv` al repositorio. Streamlit Cloud redepliega los cambios. Antes del guardado se verifica el SHA del catálogo de GitHub: si otra persona lo editó desde que se inició la app, se rechaza para prevenir pérdidas de datos.

**B. Sin token**
- Usar **Descargar combo_componentes.csv actualizado**.
- En GitHub reemplazar `combo_componentes.csv` **en la raíz** del repositorio, confirmar con **Commit changes** y recargar Streamlit.
- No alcanza con copiar el CSV al sistema temporal de Streamlit; hay que actualizar el repositorio.

## Validaciones
- El código del combo debe empezar por 900 y tener seis cifras.
- No se aceptan SKU repetidos ni códigos no numéricos.
- Si un SKU todavía no figura individualmente en `ventadiaria`, hay que completar sus campos comerciales en la tabla editable. No se inventan marcas o unidades de negocio.
- Los desgloses UNG que ya fueron verificados en CHESS y codificados en el motor no se pueden reemplazar con otros contradictorios por accidente.
- Se contabiliza una compra solo cuando el neto de bultos del combo por cliente es positivo.
- Las alertas se disparan para combos que tengan compra neta positiva; combos presentes solo como devoluciones sin compra neta se excluyen.

**Seguridad:** protegé el PIN y el token. No pongas claves en el repositorio público ni en capturas. La aplicación de acceso público solo permite guardar cambios a quien conozca el PIN configurado en el servidor.

# Corrección `motor` sin `set_copy_aliases` — DDV

Este parche contiene solamente `app.py`, `motor.py` y `gestion_combos.py`.

## Qué corrige

- Antes de calcular indicadores, `app.py` comprueba que el motor exponga las funciones requeridas, incluidas `set_runtime_profile` y `set_copy_aliases`.
- Si Streamlit conserva en memoria un motor anterior, intenta recargar el módulo local.
- Si después de recargar faltan funciones, muestra un error de versión claro y no entrega cifras inconsistentes.
- La función `set_copy_aliases` incluida en `motor.py` aplica la regla comercial de copiar componentes desde un combo original inequívoco.

## Actualización en GitHub

1. Abrir el repositorio `tomasddv/caffitastream` (rama `main`).
2. Subir los tres archivos extraídos en la raíz, reemplazando los existentes.
3. Hacer un único commit.
4. En Streamlit Community Cloud, abrir **Manage app → Reboot app**.

**No reemplazar** `combo_componentes.csv`, archivos `clientes_p1_p4*`, `indicadores.csv`, imágenes ni los secretos de Streamlit: este parche no los necesita ni los incluye.

## Verificación

En `motor.py` deben existir `def set_copy_aliases(` y `def set_runtime_profile(`. Al elegir noviembre, los indicadores deben cargarse y el panel de combos debe indicar copias reconocidas y pendientes. Si Streamlit vuelve a mostrar `AttributeError`, revisar en **Manage app → Logs** el nombre y ruta del módulo que se está importando; confirmar que el despliegue apunta al repositorio y rama correctos.

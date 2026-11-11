# Copias automáticas de combos — DDV

## Regla validada por el usuario (noviembre 2026)

Cuando un combo nuevo de CHESS comienza con `COPIA`, es una copia del combo del
mes anterior cuyo nombre es el mismo, sin el prefijo `COPIA`. Se admiten
prefijos repetidos (`COPIA COPIA`) y variaciones de signos y acentos.
Si la única diferencia es un sufijo regional `SUR`, se identifica el origen
solo si existe un único candidato.

La aplicación consulta el archivo archivado `ventadiaria <mes anterior>.txt`
en Drive, compara el nombre y hereda **sin volver a pedir SKU** las familias
comerciales y los SKU ya documentados del combo original. El proceso se repite
en cada actualización, sin depender de archivos temporales ni un commit nuevo.

**Controles:**
- Si el nombre no coincide, el original no existe o hay dos candidatos, no se
  hacen suposiciones; el combo sigue en alertas para carga manual.
- Si el origen solo tiene clasificación comercial y no tiene composición
  detallada, la copia hereda solamente esa clasificación; no se crean SKU.
- Los combos con desglose propio en GitHub tienen prioridad sobre la regla de copia.
- No se duplican clientes ni pares cliente–SKU; el motor agrega ventas netas.
- Sigue vigente la exclusión de clientes del subcanal CLIE PEOPLE.
- El cierre histórico conserva sus reglas, sin incorporar combos nuevos
  del mes corriente.

## Verificación con ventas del 1 al 11 de noviembre de 2026

- 14 combos COPIA reconocidos mediante octubre 2026.
- 7 combos vendidos pendientes de registrar o revisar porque no son copias
  identificables.
- TBD UNG: de 3.996 a 4.204 pares cliente–SKU (+208).
- CCC Black: 136 a 150 clientes. Los combos de Pepsi común NO suman Black.

## Para subir a GitHub

Usá preferentemente el ZIP de actualización de tres archivos. Reemplazá
`app.py`, `motor.py` y `gestion_combos.py` en la raíz de
`tomasddv/caffitastream`, hacé commit y reiniciá Streamlit Cloud.
**No reemplaces `combo_componentes.csv`** con un archivo antiguo: este
archivo es actualizado en GitHub desde la app y debe conservar los últimos
cambios manuales.

Los secretos `GITHUB_TOKEN` y `COMBO_EDITOR_PIN` no se modifican.

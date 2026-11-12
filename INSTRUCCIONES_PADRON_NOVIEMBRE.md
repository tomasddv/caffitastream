# Padrón P1 + P4 oficial — noviembre 2026

**Fuente exclusiva para determinar la pertenencia P1/P4 de noviembre:** `p1 y p4.xlsx`, entregado el 12/11/2026. Sustituye por completo los listados de noviembre suministrados previamente.

- Fuente: 958 filas de clientes con encabezados `COD B2B` y `DISTRI`.
- Clientes únicos oficiales: **957**. El código **2674** aparece dos veces en el Excel original, una como texto con cero inicial y otra como número sin él; se consolida una sola vez.
- Se convierten los códigos B2B de 14 dígitos (`07054900` + seis dígitos de cliente) a códigos ERP normalizados de 4 o 6 cifras. Ejemplo: `07054900100572` → `100572`.
- El nuevo padrón de noviembre comparte 946 códigos con la versión anterior de 1.665; entran 11 y salen 719. La versión anterior queda desestimada.
- El padrón **cerrado de octubre (940 clientes)** queda intacto en `clientes_p1_p4_2026_10.csv`.
- Se reemplazan `clientes_p1_p4_2026_11.csv` (noviembre) y `clientes_p1_p4.csv` (base predeterminada de meses futuros).
- Nombres comerciales y promotores siguen viniendo del **REPORTE DE CLIENTES de Google Drive**, mediante el cruce por código; la fuente oficial adjunta solo aporta IDs y distribuidora. Se dejan sin razón social local seis códigos que no se identificaron de forma verificable en las fuentes complementarias; no se descartan del padrón.
- Se mantiene la exclusión de CLIE PEOPLE a través del reporte de clientes. El objetivo de cobertura 1890 de noviembre sigue siendo el **80 % del universo elegible**, no una cantidad fija de clientes.

## Archivos de este parche

- `clientes_p1_p4_2026_11.csv`
- `clientes_p1_p4.csv`
- `padron.py` (corrige la interpretación de B2B completos de clientes de 4 y 6 cifras)
- `tests/test_padron_noviembre26.py` (pruebas de padrón y mapeo)
- `INSTRUCCIONES_PADRON_NOVIEMBRE.md`

**No reemplazar** `clientes_p1_p4_2026_10.csv`, `combo_componentes.csv`, `app.py`, `motor.py` ni `gestion_combos.py`. Esto evita sobrescribir el cierre de octubre o las composiciones de combos guardadas desde la app.

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


# DDV — VS mes anterior a la misma fecha

Este parche modifica `app.py` y agrega `comparacion_mtd.py` (no modifica ni `motor.py`, ni los padrones históricos, ni `combo_componentes.csv`).

## Instalación en GitHub
1. Descomprimir el ZIP.
2. Subir **app.py** y **comparacion_mtd.py** a la raíz de `tomasddv/caffitastream` y hacer **Commit changes**.
3. Opcionalmente agregar `tests/test_comparacion_mtd.py` para conservar las pruebas.
4. En Streamlit Community Cloud, `Manage app → Reboot app`.

No reemplazar `combo_componentes.csv`; las composiciones guardadas automáticamente quedan intactas. No cambiar `GITHUB_TOKEN` ni el PIN de administrador.

## Definiciones
- El VS toma el acumulado **del día 1 hasta el día de corte** de cada mes, independientemente de que el filtro visual empiece en un día posterior.
- Por ejemplo, 12/11 contra 12/10. Si el mes anterior tiene menos días (31/03 contra febrero), el corte se limita al último día calendario de ese mes.
- Diferencia absoluta = MTD actual − MTD anterior.
- Variación relativa = diferencia ÷ MTD anterior. Si el mes anterior es cero, se marca `sin base %`.
- Cada KPI utiliza **la misma definición comercial del mes seleccionado** en ambos períodos: en noviembre se compara Pepsi Black con Pepsi Black (no Red Bull); CCC 269 con CCC 269 (no con Innovaciones Core completo).
- Se excluyen CLIE PEOPLE en ambos meses mediante el reporte de clientes actualizado.
- CCC 1890 utiliza el **padrón histórico del mes que corresponde**: octubre usa `clientes_p1_p4_2026_10.csv` y noviembre `clientes_p1_p4_2026_11.csv`. Es una comparación de poblaciones no idénticas; no deben confundirse las diferencias con productividad pura.
- El Real principal y los objetivos de los diez KPI no cambian; la referencia MTD es un complemento debajo de cada tarjeta y en la tabla descargable.

## Calidad del comparativo de octubre
En la carpeta Drive se halló `ventadiaria octubre.txt`, pero NO `ventadiaria bultos octubre.txt`. El sistema puede usar el volumen del archivo cerrado como sustituto **provisorio**, por lo que el VS mostrará una advertencia y la marca `PROVISORIO` en cada KPI. Para un comparativo **validado**, guardar también `ventadiaria bultos octubre.txt` en la misma carpeta. En caso de no hallar archivo histórico, muestra `SIN DATOS`; nunca inventa cero.

## Resiliencia
Los errores de la fuente comparativa no interrumpen el cálculo de noviembre. El VS no agrega una cuarta solapa, ni modifica los datos comerciales, ni altera los indicadores por promotor, ranking o carga automática de combos.

# Padrón P1/P4 y combos · noviembre 2026

- `clientes_p1_p4_2026_10.csv`: fotografía de octubre, 940 clientes.
- `clientes_p1_p4_2026_11.csv`: padrón corregido de noviembre, 1.665 clientes únicos, a partir de los archivos `export (2)(1).xlsx` y `export (3)(1).xlsx`.
- `clientes_p1_p4.csv`: padrón operativo por defecto (actualizado a noviembre).
- El selector de período elige el padrón correspondiente antes de ejecutar CCC 1890 y de calcular el 80 % de cobertura comercial.
- El objetivo 80 % se aplica al universo elegible tras excluir CLIE PEOPLE según el reporte actualizado de clientes.
- **Atención a `combo_componentes.csv`:** las composiciones guardadas desde Streamlit se confirman en el repositorio de GitHub. Antes de sustituir este CSV por el de un ZIP, revisá que el repositorio no tenga cargas posteriores; si las tiene, conservá la versión más reciente de GitHub. Esta entrega suma el combo 900468 que ya constaba allí.
- El catálogo permite registrar nuevas composiciones con `GITHUB_TOKEN` y `COMBO_EDITOR_PIN` configurados en Streamlit Secrets. No subas las credenciales al repositorio.
- Octubre no debe recalcularse usando el padrón de noviembre.

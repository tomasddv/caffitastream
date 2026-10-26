# Solución al error de importación en Streamlit Cloud · 26/10/2026

La captura muestra `ImportError` al cargar `from motor import (...)` en `app.py`, línea 18. El mensaje detallado está oculto por Streamlit Cloud, por lo que la captura sola no permite saber qué nombre produjo el error.

Este paquete verifica el origen del módulo `motor.py`, comprueba todas las funciones antes de iniciar y muestra un aviso de despliegue si encuentra archivos de distintas versiones. Incluye `deploy_check.py` y conserva las reglas comerciales del 26/10, los 10 KPI, padrón P1/P4 de 940, los combos y el reporte de clientes actualizado.

**Pasos:**
1. Descomprimí el ZIP.
2. En GitHub (`tomasddv/caffitastream`, rama `main`), subí **todos** los archivos del paquete, incluidas las carpetas `assets`, `tests` y `.streamlit`.
3. Asegurate de que `app.py`, `motor.py`, `padron.py`, `reporte_clientes.py` y `requirements.txt` estén juntos en la raíz, no dentro de una carpeta nueva.
4. Confirmá los cambios en un único `Commit changes`.
5. En Streamlit Cloud: `Manage app` → `Reboot app` para reiniciar el servidor.
6. Si persiste: `Manage app` → `Logs` y copiá el mensaje completo `cannot import name ...` o equivalente para encontrar la dependencia exacta.

**Verificación local** (si tenés Python): `python deploy_check.py`. No depende de que Streamlit esté instalado, pero necesita las bibliotecas del `requirements.txt` para importar el motor.

El ZIP no incluye el reporte completo de clientes descargado desde Drive. Contiene el padrón comercial `clientes_p1_p4.csv`: evitá publicarlo en un repositorio sin control de acceso.

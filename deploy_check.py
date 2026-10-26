"""Diagnóstico de compatibilidad: python deploy_check.py"""
from pathlib import Path
import sys
import ast

ROOT = Path(__file__).resolve().parent
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))
sys.path.insert(0, str(ROOT))
import motor, padron, reporte_clientes

REQUIRED = (
    'DIA_ID', 'BULTOS_ID', 'NOMBRES', 'OBJETIVOS', 'leer_tsv', 'prepare',
    'compute_sales', 'detalle_tbd_ung', 'detalle_innovaciones',
    'compradores_innovaciones_core', 'validate_reconciliation',
    'promotor_breakdown', 'PROMOTOR_LABELS',
)
def main():
    for name in ('app.py', 'motor.py', 'padron.py', 'reporte_clientes.py'):
        ast.parse((ROOT / name).read_text(encoding='utf8'), filename=name)
    assert Path(motor.__file__).resolve() == (ROOT/'motor.py').resolve(), 'El motor no corresponde a este repositorio'
    missing = [name for name in REQUIRED if not hasattr(motor, name)]
    assert not missing, 'Faltan funciones: ' + ', '.join(missing)
    assert reporte_clientes.REPORTE_CLIENTES_ID == '1VrxE5Tu1T_ruYkKf4eW3uiGoKlJcpCA6'
    for name in ('clientes_p1_p4.csv', 'combo_componentes.csv',
                 'control_referencia_19_10_2026.csv', 'control_referencia_26_10_2026.csv',
                 'requirements.txt'):
        assert (ROOT/name).is_file(), 'Falta el archivo '+name
    print('OK: imports del motor, padron, reporte de clientes y archivos indispensables')
if __name__ == '__main__': main()

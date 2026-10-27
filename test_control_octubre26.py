"""Protección de fuentes y controles de cobertura del corte del 26/10."""
import csv
from pathlib import Path
import unittest
from reporte_clientes import REPORTE_CLIENTES_ID, clientes_clie_people

ROOT=Path(__file__).resolve().parents[1]
class CutoffOct26Tests(unittest.TestCase):
    def test_reporte_clientes_vigente(self):
        self.assertEqual(REPORTE_CLIENTES_ID,'1VrxE5Tu1T_ruYkKf4eW3uiGoKlJcpCA6')
    def test_referencia_26(self):
        with (ROOT/'control_referencia_26_10_2026.csv').open(encoding='utf-8-sig') as f:
            data={r['id']:int(r['real_informe']) for r in csv.DictReader(f)}
        self.assertEqual(len(data),10)
        self.assertEqual(data['cervezas'],1149)
        self.assertEqual(data['1890'],683)
        self.assertEqual(data['ung'],8932)
        self.assertEqual(data['core'],217)
        self.assertEqual(data['mi'],299)
    def test_fuente_reporte_tiene_people(self):
        from reporte_clientes import leer_reporte_clientes_xlsx
        data=ROOT/'tests'/'fixtures_reporte_clientes_26.xlsx'
        if data.exists():
            self.assertEqual(len(clientes_clie_people(leer_reporte_clientes_xlsx(data.read_bytes()))),142)
    def test_control_fechas_en_app(self):
        text=(ROOT/'app.py').read_text(encoding='utf-8')
        self.assertNotIn('with tab_control:',text)
        self.assertNotIn('🔎 Control oficial',text)
        self.assertIn('tab_general, tab_promotor, tab_ranking = st.tabs(',text)

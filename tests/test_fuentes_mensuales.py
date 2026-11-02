import unittest
from datetime import date
from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import fuentes_mensuales as fm
from motor import leer_tsv,prepare,validate_reconciliation

class TestMeses(unittest.TestCase):
    def test_filenames_accept_both_orders(self):
        self.assertEqual(fm.filename_info('ventadiaria octubre.txt'),('volumen',10))
        self.assertEqual(fm.filename_info('ventadiaria bultos octubre.txt'),('bultos',10))
        self.assertEqual(fm.filename_info('ventadiaria octubre bultos.txt'),('bultos',10))
        self.assertEqual(fm.filename_info('ventadiaria.txt'),('volumen',None))
        self.assertEqual(fm.filename_info('ventadiaria bultos.txt'),('bultos',None))
        self.assertEqual(fm.filename_info('ventadaria.txt'),('volumen',None))
        self.assertIsNone(fm.filename_info('venta_reporte_octubre.xlsx'))
        self.assertIsNone(fm.filename_info('ventadiaria diciembre 2025.txt'))
    def test_just_two_periods_year_rollover(self):
        self.assertEqual(fm.mes_anterior(date(2027,1,1)),(2026,12))
        d={'ventadiaria.txt':'nov','ventadiaria bultos.txt':'nov-b',
           'ventadiaria octubre.txt':'oct','ventadiaria bultos octubre.txt':'oct-b',
           'ventadiaria septiembre.txt':'sep'}
        x=fm.fuentes_por_periodo(d,date(2026,11,2))
        self.assertEqual(set(x),{(2026,11),(2026,10)})
        self.assertEqual(x[(2026,10)],{'volumen':'oct','bultos':'oct-b'})
        self.assertEqual(x[(2026,11)],{'volumen':'nov','bultos':'nov-b'})
    def test_error_for_duplicate_filenames_same_month(self):
        with self.assertRaisesRegex(ValueError,'duplicadas'):
            fm.fuentes_por_periodo({'ventadiaria bultos octubre.txt':'a',
                                    'ventadiaria octubre bultos.txt':'b'},date(2026,11,2))
    def test_validate_real_nov_pair(self):
        path=Path('/mnt/data')
        if not (path/'ventadiaria.txt').exists():self.skipTest('Datos de prueba Drive no montados')
        vol=leer_tsv((path/'ventadiaria.txt').read_bytes())
        bul=leer_tsv((path/'ventadiaria bultos.txt').read_bytes())
        self.assertEqual(validate_reconciliation(vol,bul)[0],True)
        self.assertEqual(len(fm.filtrar_y_validar_mes(vol,(2026,11))),739)
        with self.assertRaisesRegex(ValueError,'no contiene ventas'):
            fm.filtrar_y_validar_mes(vol,(2026,10))
    def test_october_does_not_accept_nov(self):
        df=pd.DataFrame({'Descripción Período':['2-nov-26','31-oct-26']})
        # Evitar creer que dos meses son uno, incluso si archivo comparte nombre.
        from motor import prepare
        fake=leer_tsv(Path('/mnt/data/ventadiaria.txt').read_bytes()).head(2).copy()
        fake.loc[fake.index[0],'Descripción Período']='31-oct-26'
        with self.assertRaisesRegex(ValueError,'fuera de Octubre'):
            fm.filtrar_y_validar_mes(fake,(2026,10))
    def test_october_volume_fallback_sign_not_false_bultos(self):
        raw=leer_tsv(Path('/mnt/data/ventadiaria octubre.txt').read_bytes())
        self.assertEqual(len(fm.filtrar_y_validar_mes(raw,(2026,10))),36790)
        tmp=fm.volumen_para_conteo(raw)
        combo=tmp['Código'].str.fullmatch(r'900\d{3}')
        self.assertGreater(combo.sum(),100)
        self.assertTrue((tmp.loc[combo,'Cantidades Totales'] != '0').any())

if __name__=='__main__':unittest.main()

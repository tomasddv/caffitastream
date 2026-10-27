"""Pruebas de regresión: el catálogo CHESS puede ampliarse sin tocar motor.py."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import motor

HEAD='codigo,articulo_componente,descripcion,unidad_negocio,marca,calibre,division,hl_por_combo\n'

class CatalogoTests(unittest.TestCase):
    def test_combo_ung_nuevo_csv_aporta_sku_y_no_duplica(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'combo_componentes.csv').write_text(HEAD+
                '900999,591,MIRINDA MANZANA 2.25L,UNG,MIRINDA,2250 CC PET,GASEOSAS,\n'
                '900999,627,MIRINDA NARANJA 2.25L,UNG,MIRINDA,2250 CC PET,GASEOSAS,\n', encoding='utf-8-sig')
            ventas=pd.DataFrame([
                ('5','900999','',1),('5','591','UNG',1),('5','900999','',1),
                ('6','900999','',1),('7','900999','',1),('7','900999','',-1),
            ],columns=['cliente','sku','unidad','bultos'])
            with patch.object(motor,'RAIZ',Path(td)):
                pairs,pend=motor.detalle_tbd_ung(ventas)
                self.assertEqual(len(pairs),4)
                self.assertTrue(pend.empty)
                self.assertSetEqual(set(pairs.loc[pairs.cliente.eq('5'),'sku']), {'591','627'})
                self.assertSetEqual(set(pairs.loc[pairs.cliente.eq('6'),'sku']), {'591','627'})
                self.assertEqual(len(pairs.loc[pairs.cliente.eq('7')]),0)

    def test_combo_nuevo_1890_solo_si_componente_confirmado(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'combo_componentes.csv').write_text(HEAD+
                '900999,51290,QUILMES 1890 CAN 4X4 710CC,CZA,QUILMES 1890,710 CC LATAS,CERVEZAS,\n',encoding='utf-8-sig')
            ventas=pd.DataFrame([('8','900999','',1)],columns=['cliente','sku','unidad','bultos'])
            for col in ('marca','descripcion','calibre','division'):
                ventas[col]=''
            with patch.object(motor,'RAIZ',Path(td)):
                flags,_=motor.mask_por_indicador(ventas)
            self.assertTrue(flags['1890'].iloc[0])
            self.assertTrue(flags['latones'].iloc[0])
            self.assertTrue(flags['cervezas'].iloc[0])

    def test_composicion_contradictoria_falla_antes_de_contar(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'combo_componentes.csv').write_text(HEAD+
                '900409,30972,7UP 1500,UNG,7 UP,1500 CC PET,GASEOSAS,\n'
                '900409,99999,SKU INCORRECTO,UNG,7 UP,2000 CC PET,GASEOSAS,\n',encoding='utf-8-sig')
            with patch.object(motor,'RAIZ',Path(td)):
                with self.assertRaisesRegex(ValueError,'contradictoria'):
                    motor.obtener_componentes_ung()

    def test_promotores_total_global_unico(self):
        # Mismo cliente compra con dos promotores: total general = 1, no 2.
        ventas=pd.DataFrame([
            ('8','29743','QUILMES 1890','QUILMES 1890','473 CC LATAS','CERVEZAS','CERVEZAS',1,'Lucas'),
            ('8','29743','QUILMES 1890','QUILMES 1890','473 CC LATAS','CERVEZAS','CERVEZAS',1,'Mati'),
        ],columns=['cliente','sku','descripcion','marca','calibre','division','unidad','bultos','promotor'])
        with tempfile.TemporaryDirectory() as td:
            Path(td,'combo_componentes.csv').write_text(HEAD,encoding='utf-8-sig')
            with patch.object(motor,'RAIZ',Path(td)):
                prom=motor.promotor_breakdown(ventas,['cervezas'])
        self.assertEqual(int(prom.iloc[-1,1]),1)
        self.assertEqual(int(prom.iloc[:-1,1].sum()),2)

    def test_tres_solapas_sin_conciliacion(self):
        app=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf8')
        self.assertEqual(app.count(' = st.tabs('),1)
        self.assertIn('tab_general, tab_promotor, tab_ranking = st.tabs(',app)
        self.assertNotIn('with tab_control:',app)

if __name__=='__main__':unittest.main()

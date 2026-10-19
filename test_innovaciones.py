"""Tests de CCC Innovaciones Core."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from motor import detalle_innovaciones,clasificar_innovacion

class TestInnovaciones(unittest.TestCase):
    def test_identificar_brahma_y_quilmes_269_y_ft(self):
        self.assertEqual(clasificar_innovacion('15624'),'Brahma 269 cc')
        self.assertEqual(clasificar_innovacion('63068'),'Quilmes Clásica 269 cc')
        self.assertEqual(clasificar_innovacion('80001','BRAHMA FT 4X6','BRAHMA','','CERVEZAS','LIMON'),'Brahma FT Limón')
        self.assertEqual(clasificar_innovacion('80002','BRAHMA FT POMELO','BRAHMA','','CERVEZAS'),'Brahma FT Pomelo')
        self.assertEqual(clasificar_innovacion('31074','PDT POMELO CAN X24 269','PASO DE LOS TOROS','269 CC LATA','GASEOSAS'),'')
        self.assertEqual(clasificar_innovacion('2218','QUILMES 473','QUILMES','473 CC LATAS','CERVEZAS'),'')

    def test_cliente_unico_y_saldo_neto(self):
        records=[
            ('A','15624','BRAHMA 269','BRAHMA','269 CC LATA','CERVEZAS','',4),
            ('A','15624','BRAHMA 269','BRAHMA','269 CC LATA','CERVEZAS','',3),
            ('A','63068','QUILMES CLASICA 269','QUILMES CLASICA','269 CC LATA','CERVEZAS','',1),
            ('B','80001','BRAHMA FT','BRAHMA','','CERVEZAS','LIMON',1),
            ('B','80002','BRAHMA FT','BRAHMA','','CERVEZAS','POMELO',3),
            ('B','80002','BRAHMA FT','BRAHMA','','CERVEZAS','POMELO',-1),
            ('C','63068','QUILMES CLASICA 269','QUILMES CLASICA','269 CC LATA','CERVEZAS','',1),
            ('C','63068','QUILMES CLASICA 269','QUILMES CLASICA','269 CC LATA','CERVEZAS','',-1),
            ('D','31074','PDT POMELO 269','PASO DE LOS TOROS','269 CC LATA','GASEOSAS','POMELO',1),
        ]
        df=pd.DataFrame(records,columns=['cliente','sku','descripcion','marca','calibre','division','sabor','bultos'])
        pares,resumen,pending=detalle_innovaciones(df)
        self.assertEqual(pares.cliente.nunique(),2)
        self.assertEqual(len(pares),4)
        self.assertEqual(set(pares.sku),{'15624','63068','80001','80002'})
        self.assertTrue(pending.empty)

    def test_combo_documentado_deduplica_sku(self):
        records=[
            ('A','15624','BRAHMA 269','BRAHMA','269 CC LATA','CERVEZAS','',1),
            ('A','900777','COMBO INNOVACION','', '', '', '',2),
            ('B','900777','COMBO INNOVACION','', '', '', '',1),
        ]
        df=pd.DataFrame(records,columns=['cliente','sku','descripcion','marca','calibre','division','sabor','bultos'])
        with patch('motor.obtener_componentes_innovaciones',return_value={'900777': {'15624':'Brahma 269 cc','63068':'Quilmes Clásica 269 cc'}}):
            pares,_,pending=detalle_innovaciones(df)
        self.assertEqual(len(pares),4)
        self.assertEqual(pares.cliente.nunique(),2)
        self.assertIn('Venta directa',pares.loc[(pares.cliente=='A')&(pares.sku=='15624'),'origen'].item())
        self.assertIn('Combo 900777',pares.loc[(pares.cliente=='A')&(pares.sku=='15624'),'origen'].item())
        self.assertTrue(pending.empty)

if __name__ == '__main__': unittest.main()

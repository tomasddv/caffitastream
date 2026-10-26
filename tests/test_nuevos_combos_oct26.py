"""Nuevos combos reconocibles a nivel familia, no componente SKU."""
from datetime import date
import unittest
import pandas as pd
from motor import COMBOS,COMBO_UNG_SKUS,compute_sales


def v(cliente,sku,cant=1):
    return {'Cod. Cliente':str(cliente),'Código':str(sku),
            'Descripción.2':{'900466':'COMBO LATONES - BRAHMA Y QUILMES - PATAGONIA BDV',
                             '900471':'COMBO PORRONES 0.0 + PURE GOLD',
                             '900473':'COMBO BRAH&QUIL 269 CC SUR'}.get(str(sku),'OTRO'),
            'Descripción.3':'','Descripción.4':'','Descripción.5':'','Descripción.8':'',
            'Cantidades Totales':str(cant),'Descripción Período':'26-oct-26',
            'Vendedor':'1','Descripción Vendedor':'NICASTRO LUCAS'}
class TestOct26NewCombos(unittest.TestCase):
    def test_mapping_and_no_fake_components(self):
        self.assertIn('core',COMBOS['900473'])
        self.assertIn('latones',COMBOS['900466'])
        self.assertIn('pure_gold',COMBOS['900471'])
        self.assertIn('cero',COMBOS['900471'])
        for sku in ['900466','900471','900473']:
            self.assertNotIn(sku,COMBO_UNG_SKUS)
    def test_each_combo_once_for_ccc(self):
        p=pd.DataFrame({'cliente_codigo':['1','2','3']})
        out,_,_,_=compute_sales(pd.DataFrame([v(1,900473),v(1,900473),v(2,900466),v(3,900471)]),p,date(2026,10,1),date(2026,10,26))
        d={q['id']:q['real'] for q in out}
        self.assertEqual(d['core'],1)
        self.assertEqual(d['cervezas'],3)
        self.assertEqual(d['latones'],1)
        self.assertEqual(d['pure_gold'],1)
        self.assertEqual(d['cero'],1)
if __name__=='__main__':unittest.main()

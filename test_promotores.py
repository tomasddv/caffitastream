"""Pruebas de reparto de 10 KPI por promotor y filtro del padrón 1890."""
from pathlib import Path
import sys
import unittest
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from motor import promotor_breakdown, PROMOTOR_LABELS


def ventas_ejemplo():
    def linea(prom,cli,sku,desc='',marca='',cal='',div='',unidad='',bultos=1):
        return dict(promotor=prom,cliente=cli,sku=sku,descripcion=desc,marca=marca,calibre=cal,
                    division=div,unidad=unidad,bultos=bultos,sabor='')
    return pd.DataFrame([
        linea('Fede','A','30645','PEPSI 2L','PEPSI',unidad='UNG',bultos=10),
        linea('Fede','A','30645','PEPSI 2L','PEPSI',unidad='UNG',bultos=1),
        linea('Fede','A','900444','COMBO AGUAS + UNG',bultos=2),
        linea('Fede','A','29740','QUILMES 1890','QUILMES 1890',div='CERVEZAS',unidad='CERVEZAS'),
        linea('Fede','X','29740','QUILMES 1890','QUILMES 1890',div='CERVEZAS',unidad='CERVEZAS'),
        linea('Mati','B','63068','QUILMES 269','QUILMES CLASICA','269 CC LATA','CERVEZAS','CERVEZAS'),
        linea('Mati','B','63068','QUILMES 269','QUILMES CLASICA','269 CC LATA','CERVEZAS','CERVEZAS'),
        linea('Mati','B','16371','RED BULL','RED BULL',unidad='UNG',bultos=4),
        linea('Sin promotor','C','30645','PEPSI 2L','PEPSI',unidad='UNG'),
    ])

class TestPromotorMatrix(unittest.TestCase):
    def test_ten_indicators_and_tbd_customer_sku(self):
        x=ventas_ejemplo()
        padron=pd.DataFrame({'cliente_codigo':['A','B']})
        keys=['h2oh','redbull','pure_gold','mi','cero','core','1890','latones','cervezas','ung']
        df=promotor_breakdown(x,keys,padron)
        self.assertEqual(len(df.columns),11)
        self.assertEqual(list(df.columns[1:]),[PROMOTOR_LABELS[k] for k in keys])
        fede=df.set_index('Promotores').loc['Fede']
        self.assertEqual(fede['Tbd Ung'],2) # Pepsi directo + Pepsi del combo se cuenta una vez, 7UP suma otra
        self.assertEqual(fede['Ccc 1890 P1/P4'],1) # excluye X no perteneciente a P1+P4
        mati=df.set_index('Promotores').loc['Mati']
        self.assertEqual(mati['Ccc Innovaciones Core'],1)
        self.assertEqual(mati['Ccc Red bull'],1)
        self.assertEqual(mati['Tbd Ung'],1)
        self.assertEqual(df.set_index('Promotores').loc['Sin promotor','Tbd Ung'],1)
        self.assertEqual(df.iloc[-1]['Tbd Ung'],4)
        self.assertEqual(df.iloc[-1]['Promotores'],'Totales')

    def test_p1p4_without_padron_errors_instead_of_overcounting(self):
        with self.assertRaisesRegex(ValueError,'padrón'):
            promotor_breakdown(ventas_ejemplo(),['1890'])

if __name__=='__main__':
    unittest.main()

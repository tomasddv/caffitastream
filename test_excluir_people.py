"""La exclusión CLIE PEOPLE debe afectar todos los KPI, combos, promotores y ranking."""
from datetime import date
import unittest
import pandas as pd
from motor import compute_sales,promotor_breakdown,OBJETIVOS, detalle_tbd_ung
from reporte_clientes import clientes_clie_people,filtrar_padron_people


class ExcluirPeopleTest(unittest.TestCase):
    @staticmethod
    def ventas_prueba():
        items=[]
        for client,vendedor,sku,nom,marca,unidad,calibre,cant in [
            ('5','NICASTRO LUCAS','30481','7UP LATA','7 UP','UNG','354 CC',1),
            ('840','NICASTRO LUCAS','30481','7UP LATA','7 UP','UNG','354 CC',1),
            ('840','NICASTRO LUCAS','30972','7UP PET','7 UP','UNG','1500 CC',7),
            ('840','NICASTRO LUCAS','900409','COMBO 7UP PAT','','','','1'),
            ('5','NICASTRO LUCAS','29740','QUILMES 1890','QUILMES 1890','CZA','1 L',2),
            ('840','NICASTRO LUCAS','29740','QUILMES 1890','QUILMES 1890','CZA','1 L',1),
        ]:
            items.append({'Cod. Cliente':client,'Código':sku,'Descripción.2':nom,
                 'Descripción.3':marca,'Descripción.4':calibre,'Descripción.5':'CERVEZAS' if sku=='29740' else 'GASEOSAS',
                 'Descripción.8':unidad,'Descripción Período':'1-oct-26',
                 'Cantidades Totales':str(cant),'Descripción Vendedor':vendedor,'Vendedor':'71'})
        return pd.DataFrame(items)

    def test_exclusion_permea_a_todo(self):
        reporte=pd.DataFrame({'cliente_codigo':['5','840'], 'subcanal':['ALMACEN','clie   people']})
        excluidos=clientes_clie_people(reporte)
        self.assertEqual(excluidos,{'840'})
        padr=pd.DataFrame({'cliente_codigo':['5','840'], 'razon_social':['A','B']})
        filtrado=filtrar_padron_people(padr,excluidos)
        rows,detail,combos,x=compute_sales(self.ventas_prueba(),filtrado,date(2026,10,1),date(2026,10,31),excluir_clientes=excluidos)
        data={row['id']:row for row in rows}
        self.assertEqual(data['1890']['real'],1)
        self.assertEqual(data['1890']['cobertura'],1.0)
        self.assertEqual(data['ung']['real'],1)
        self.assertEqual(data['1890']['objetivo'],OBJETIVOS['1890'])
        self.assertEqual(detail['cliente_codigo'].tolist(),['5'])
        self.assertTrue(x['cliente'].eq('5').all())
        self.assertEqual(detalle_tbd_ung(x)[0]['cliente'].unique().tolist(),['5'])
        prom=promotor_breakdown(x,['ung','1890'],filtrado)
        self.assertEqual(prom.iloc[-1]['Tbd Ung'],1)
        self.assertEqual(prom.iloc[-1]['Ccc 1890 P1/P4'],1)

    def test_sin_catalogo_de_subcanal_no_adivinar(self):
        with self.assertRaises(ValueError):
            clientes_clie_people(pd.DataFrame({'cliente_codigo':['840']}))


if __name__=='__main__':
    unittest.main()

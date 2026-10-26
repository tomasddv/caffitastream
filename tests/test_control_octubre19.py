"""Reglas de conciliación 19/10: combos con familia confirmada, sin inventar SKU."""
from datetime import date
import unittest
import pandas as pd
from motor import COMBOS, COMBO_UNG_SKUS, compute_sales, promotor_breakdown, detalle_tbd_ung


def venta(cliente,sku,cantidad,fecha='19-oct-26',promotor='FEDERICO BISS'):
    desc={'900465':'COMBO SABORIZADAS - PATAGONIA','900470':'COMBO BRAHMA FT',
          '900467':'COMBO GATORADE K+T - OCT','15624':'BRAHMA FT LIMON'}
    combo=str(sku).startswith('900')
    return {'Cod. Cliente':str(cliente),'Código':str(sku),
            'Descripción.2':desc.get(str(sku),''),
            'Descripción.3':'' if combo else 'BRAHMA',
            'Descripción.4':'' if combo else '269 CC LATAS',
            'Descripción.5':'' if combo else 'CERVEZAS',
            'Descripción.8':'' if combo else 'CERVEZAS CMQ',
            'Cantidades Totales':str(cantidad),'Descripción Período':fecha,
            'Vendedor':'12','Descripción Vendedor':promotor}


class ControlOctubre19Test(unittest.TestCase):
    def correr(self,*ventas,excluir=None):
        pad=pd.DataFrame({'cliente_codigo':['101','102','103']})
        rows,_,_,x=compute_sales(pd.DataFrame(ventas),pad,date(2026,10,1),date(2026,10,19),excluir_clientes=excluir)
        return {v['id']:v['real'] for v in rows}, x, pad

    def test_combo_saborizadas_suma_h2oh_sin_adjudicar_sku_falso(self):
        self.assertIn('h2oh',COMBOS['900465'])
        self.assertNotIn('900465',COMBO_UNG_SKUS)
        valores,x,pad=self.correr(venta('101','900465',1))
        self.assertEqual(valores['h2oh'],1)
        self.assertEqual(valores['ung'],0)
        _,pendientes=detalle_tbd_ung(x)
        self.assertEqual(pendientes.sku.tolist(),['900465'])
        self.assertEqual(int(promotor_breakdown(x,['h2oh'],pad).iloc[-1]['Ccc H2oh']),1)

    def test_brahma_ft_comprador_con_composicion_parcial(self):
        self.assertIn('core',COMBOS['900470'])
        valores,x,pad=self.correr(venta('101','900470',1),venta('101','15624',1),venta('102','900470',1))
        self.assertEqual(valores['core'],2)
        self.assertEqual(valores['cervezas'],2)
        self.assertEqual(int(promotor_breakdown(x,['core'],pad).iloc[-1]['Ccc Innovaciones Core']),2)

    def test_returns_people_y_fecha_respetados(self):
        valores,_,_=self.correr(venta('101','900470',1),venta('101','900470',-1),venta('102','900470',1),
                              venta('103','900470',1,fecha='20-oct-26'),excluir={'102'})
        self.assertEqual(valores['core'],0)

    def test_nuevo_combo_gatorade_se_senala_pendiente(self):
        self.assertIn('ung',COMBOS['900467'])
        vals,x,_=self.correr(venta('101','900467',1))
        self.assertEqual(vals['ung'],0)
        self.assertEqual(detalle_tbd_ung(x)[1].sku.tolist(),['900467'])

if __name__=='__main__':unittest.main()

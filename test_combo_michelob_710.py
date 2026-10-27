"""Regresión comercial: combo 900472 impacta tres CCC sin duplicar clientes.

El combo 900472 incluye Michelob Ultra 710 cc según la indicación comercial del
26/10/2026. La composición restante debe verificarse en CHESS antes de añadir
sus códigos al catálogo de componentes.
"""
import unittest
from datetime import date
import pandas as pd
from motor import compute_sales, promotor_breakdown, COMBOS


def venta(cliente, sku, cantidad, promotor='FEDERICO BISS', fecha='23-oct-26'):
    es_combo=str(sku).startswith('900')
    return {
        'Cod. Cliente':str(cliente), 'Código':str(sku),
        'Descripción.2':'COMBO MICHELOB 3CAL - PATAGONIA - KT' if str(sku)=='900472'
            else ('COMBO MICHELOB - PATAGONIA - KT' if str(sku)=='900407' else 'MICHELOB ULTRA CAN 4X4 710CC'),
        'Descripción.3':'' if es_combo else 'MICHELOB ULTRA',
        'Descripción.4':'' if es_combo else '710 CC LATAS',
        'Descripción.5':'' if es_combo else 'CERVEZAS',
        'Descripción.8':'' if es_combo else 'CERVEZAS',
        'Descripción Período':fecha, 'Cantidades Totales':str(cantidad),
        'Descripción Vendedor':promotor, 'Vendedor':'12',
    }


class Michelob710Test(unittest.TestCase):
    def evaluar(self, items, *, excluir=None):
        raw=pd.DataFrame(items)
        padron=pd.DataFrame({'cliente_codigo':['101','102','103','104','105'], 'razon_social':['X']*5})
        rows, _detail, _combos, xf=compute_sales(raw,padron,date(2026,10,1),date(2026,10,26),excluir_clientes=excluir)
        return {r['id']:r for r in rows}, xf, padron

    def test_dos_indicadores_y_cerveza_por_un_combo(self):
        self.assertEqual(set(COMBOS['900472']),{'mi','latones','cervezas'})
        rows,xf,pad=self.evaluar([venta('101','900472',1)])
        self.assertEqual((rows['mi']['real'],rows['latones']['real'],rows['cervezas']['real']), (1,1,1))
        prom=promotor_breakdown(xf,['mi','latones','cervezas'],pad)
        self.assertEqual(prom.iloc[-1][['Ccc Michelob','Ccc Latones','Ccc Cervezas']].tolist(), [1,1,1])

    def test_combo_directo_y_repeticion_no_duplican_cliente(self):
        rows,_,_=self.evaluar([venta('101','900472',1),venta('101','49827',2),venta('101','900472',1)])
        self.assertEqual(rows['mi']['real'],1)
        self.assertEqual(rows['latones']['real'],1)

    def test_otros_combos_michelob_no_crean_laton(self):
        rows,_,_=self.evaluar([venta('101','900407',1)])
        self.assertEqual(rows['mi']['real'],1)
        self.assertEqual(rows['latones']['real'],0)

    def test_clientes_excluidos_y_neto_cero(self):
        rows,_,_=self.evaluar([venta('101','900472',1),venta('101','900472',-1),venta('102','900472',1),venta('103','900472',1)], excluir={'103'})
        self.assertEqual(rows['mi']['real'],1)
        self.assertEqual(rows['latones']['real'],1)

    def test_fechas_futuras_no_computan(self):
        rows,_,_=self.evaluar([venta('101','900472',1,fecha='27-oct-26')])
        self.assertEqual(rows['mi']['real'],0)
        self.assertEqual(rows['latones']['real'],0)


if __name__=='__main__': unittest.main()

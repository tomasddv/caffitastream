"""Regresión de cuatro capturas CHESS del 27/10/2026."""
import unittest
import pandas as pd
from motor import COMBO_UNG_SKUS,obtener_componentes_ung,detalle_tbd_ung,compute_sales
from datetime import date

COMP={
 '900457':('16371','22256','32710'),
 '900465':('29815','29816'),
 '900467':('1418','1422','11522'),
 '900469':('25645','30663','30791','30974')
}

def venta(cliente,sku,n,fecha='26-oct-26'):
 return {'Cod. Cliente':str(cliente),'Código':sku,'Descripción.2':'COMBO' if sku.startswith('900') else 'UN SKU',
         'Descripción.3':'','Descripción.4':'','Descripción.5':'','Descripción.8':'UNG' if not sku.startswith('900') else '',
         'Cantidades Totales':str(n),'Descripción Período':fecha, 'Vendedor':'', 'Descripción Vendedor':'NICASTRO LUCAS'}

class CuatroCombosCHESS(unittest.TestCase):
 def test_componentes_motor_catalogo_coinciden(self):
  cats=obtener_componentes_ung()
  for codigo,componentes in COMP.items():
   with self.subTest(codigo=codigo):
    self.assertEqual(COMBO_UNG_SKUS[codigo],componentes)
    self.assertEqual(cats[codigo],componentes)

 def test_combo_redbull_tres_articulos_aunque_nombre_diga_cuatro(self):
  p=pd.DataFrame({'cliente_codigo':['5']})
  out,_,diag,_=compute_sales(pd.DataFrame([venta('5','900457',1)]),p,date(2026,10,1),date(2026,10,26))
  self.assertEqual({r['id']:r['real'] for r in out}['ung'],3)
  self.assertEqual({r['id']:r['real'] for r in out}['redbull'],1)
  self.assertFalse(bool(diag.loc[diag.sku.eq('900457'),'pendiente_desglose_ung'].any()))

 def test_combos_deduplicados_y_devoluciones_netas(self):
  ventas=pd.DataFrame([
   venta('5','900467',2),venta('5','900467',-1), # neto +1: 3 SKU
   venta('5','1418',1), # ya está en el combo, no duplica
   venta('5','900469',1), # 4 SKU nuevos
   venta('6','900465',1),venta('6','900465',-1), # cancelación neta
   venta('7','900465',1),
  ])
  p=pd.DataFrame({'cliente_codigo':['5','6','7']})
  out,_,_,x=compute_sales(ventas,p,date(2026,10,1),date(2026,10,26))
  self.assertEqual({q['id']:q['real'] for q in out}['ung'],9) # 7 de cliente 5 + 2 de 7
  self.assertEqual({q['id']:q['real'] for q in out}['h2oh'],1)
  pares,pend=detalle_tbd_ung(x)
  self.assertTrue(pend.empty)
  self.assertEqual(len(pares.loc[pares.cliente.eq('5')]),7)
  self.assertFalse(pares.cliente.eq('6').any())

 def test_periodo_y_exclusion_people(self):
  rows=[venta('5','900469',1),venta('6','900469',1),venta('7','900469',1,'27-oct-26')]
  p=pd.DataFrame({'cliente_codigo':['5','6','7']})
  out,_,_,_=compute_sales(pd.DataFrame(rows),p,date(2026,10,1),date(2026,10,26),excluir_clientes={'6'})
  self.assertEqual({q['id']:q['real'] for q in out}['ung'],4)

if __name__=='__main__':unittest.main()

"""Pruebas de distribucion numerica total (TBD) por cliente/SKU UNG.
Ejecutar desde la carpeta de la aplicación: python -m unittest discover -s tests
"""
import sys
from pathlib import Path
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from motor import detalle_tbd_ung, COMBO_UNG_SKUS


class TestTBD(unittest.TestCase):
    def test_tres_clientes_dos_tres_tres_igual_ocho(self):
        # A: dos SKUs a pesar de comprar varias veces uno.
        # B: combo Red Bull de 3 SKU; 16371 también comprado suelto.
        # C: un SKU suelto + combo Black de otros dos SKU.
        ventas=pd.DataFrame([
            ('A','30645','UNG',5),('A','30645','UNG',2),('A','47489','UNG',1),
            ('B','16371','UNG',4),('B','900441','',2),
            ('C','30791','UNG',2),('C','900438','',3),
            # Una venta y devolución completa: no hubo compra neta.
            ('D','30645','UNG',1),('D','30645','UNG',-1),
        ],columns=['cliente','sku','unidad','bultos'])
        pares,pending=detalle_tbd_ung(ventas)
        assert len(pares)==8,pares.to_string(index=False)
        assert pares.groupby('cliente').size().to_dict()=={'A':2,'B':3,'C':3}
        assert pending.empty

    def test_combo_mixto_solo_ung_y_sin_repeticiones(self):
        x=pd.DataFrame([
            ('A','900444','',2),  # contiene ECO + Pepsi y 7Up
            ('A','30645','UNG',1), # Pepsi ya contada por combo
            ('B','900444','',1),  # cuenta 2 SKU a este otro cliente
        ],columns=['cliente','sku','unidad','bultos'])
        pairs,pending=detalle_tbd_ung(x)
        assert len(pairs)==4, pairs
        assert '2439' not in pairs['sku'].values
        assert pending.empty

    def test_no_suponemos_composiciones_desconocidas(self):
        x=pd.DataFrame([('A','900411','',1)],columns=['cliente','sku','unidad','bultos'])
        pairs,pending=detalle_tbd_ung(x)
        assert len(pairs)==0
        assert pending['sku'].tolist()==['900411']

    def test_conteo_combo_no_cantidad(self):
        x=pd.DataFrame([('A','900456','',100)],columns=['cliente','sku','unidad','bultos'])
        pairs,pending=detalle_tbd_ung(x)
        assert len(pairs)==len(COMBO_UNG_SKUS['900456'])==6
        assert pending.empty


if __name__=='__main__':
    unittest.main()

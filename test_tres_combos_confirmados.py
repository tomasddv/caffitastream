"""Composiciones verificadas por capturas CHESS del 15/10/2026."""
import sys, unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from motor import COMBO_UNG_SKUS, detalle_tbd_ung, promotor_breakdown, PROMOTOR_LABELS, RAIZ

class TestTresCombos(unittest.TestCase):
    def test_composiciones_exactas(self):
        self.assertEqual(COMBO_UNG_SKUS['900098'],('7476',))
        self.assertEqual(COMBO_UNG_SKUS['900376'],('1418','1422','11522'))
        self.assertEqual(COMBO_UNG_SKUS['900377'],('1413','1418','1422','11522'))
        self.assertEqual(COMBO_UNG_SKUS['900355'],('7476',))  # Variante gin 77979, no UNG

    def test_componentes_archivo(self):
        df=pd.read_csv(RAIZ/'combo_componentes.csv',dtype=str)
        for code,n in [('900098',2),('900376',3),('900377',4)]:
            self.assertEqual(len(df[df.codigo.eq(code)]),n)
        self.assertEqual(df.loc[df.articulo_componente.eq('76363'),'unidad_negocio'].item(),'NO UNG')

    def test_deduplica_combos_y_sueltos_y_excluye_gin(self):
        # A compra ambos Gatorade (3 + 4) y Gatorade 1418 suelto: 4 SKU únicos.
        # B compra Gin Cortá la Sed y Paso Tónica suelto: 1 SKU UNG (7476).
        # C compra combo Gin Área Sur (900355): sólo tónica 7476, gin excluido.
        rows=[('A','Fede','900376','',1),('A','Fede','900377','',1),
              ('A','Fede','1418','UNG',8),('B','Mati','900098','',2),
              ('B','Mati','7476','UNG',1),('C','Mati','900355','',1)]
        data=pd.DataFrame(rows,columns=['cliente','promotor','sku','unidad','bultos'])
        for col in ['descripcion','marca','calibre','division','sabor']:
            data[col]=''
        pairs,pending=detalle_tbd_ung(data)
        self.assertEqual(pairs.groupby('cliente').size().to_dict(),{'A':4,'B':1,'C':1})
        self.assertNotIn('76363',pairs.sku.tolist())
        self.assertTrue(pending.empty)
        table=promotor_breakdown(data,['ung'])
        self.assertEqual(int(table.loc[table.Promotores.eq('Fede'), PROMOTOR_LABELS['ung']].item()),4)
        self.assertEqual(int(table.loc[table.Promotores.eq('Mati'), PROMOTOR_LABELS['ung']].item()),2)

if __name__=='__main__':unittest.main()

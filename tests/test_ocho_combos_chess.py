"""Composiciones verificadas mediante capturas de CHESS del 15/10/2026.

Se valida la pertenencia por SKU para TBD UNG, la deduplicación del
SKU compartido entre combos y el CCC H2OH de COMBO SABORIZADAS.
"""
import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from motor import COMBO_UNG_SKUS, RAIZ, detalle_tbd_ung, mask_por_indicador, promotor_breakdown

CONFIRMADOS = {
    '900355': ('7476',),
    '900391': ('591', '627', '22619'),
    '900392': ('14624', '14625', '14638'),
    '900397': ('30481', '30648', '30793', '31074'),
    '900404': ('29814', '29816'),
    '900408': ('30644', '30645'),
    '900409': ('30972', '47489'),
    '900410': ('7475', '30644', '30972'),
}


def ejemplo(filas):
    df=pd.DataFrame(filas,columns=['cliente','promotor','sku','unidad','bultos'])
    for col in ('descripcion','marca','calibre','division','sabor'):
        df[col]=''
    return df


class TestOchoCombos(unittest.TestCase):
    def test_mapeo_skus_chess(self):
        for codigo,skus in CONFIRMADOS.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(COMBO_UNG_SKUS[codigo],skus)

    def test_catalogo_refleja_todas_las_capturas(self):
        cat=pd.read_csv(RAIZ/'combo_componentes.csv',dtype=str).fillna('')
        for codigo,skus in CONFIRMADOS.items():
            with self.subTest(codigo=codigo):
                catalog_skus=tuple(cat.loc[(cat.codigo.eq(codigo)) & (cat.unidad_negocio.eq('UNG')),'articulo_componente'])
                self.assertEqual(catalog_skus,skus)
        gin=cat[(cat.codigo.eq('900355')) & (cat.articulo_componente.eq('77979'))]
        self.assertEqual(gin.unidad_negocio.item(),'NO UNG')

    def test_7up_mas_1500cc_desduplica_30972_y_directos(self):
        df=ejemplo([
            ('A','Fede','900409','',2),
            ('A','Fede','900410','',1),
            ('A','Fede','30972','UNG',10),
            ('B','Mati','900409','',5),
        ])
        pares,pendientes=detalle_tbd_ung(df)
        self.assertTrue(pendientes.empty)
        self.assertEqual(pares.groupby('cliente').size().to_dict(),{'A':4,'B':2})
        self.assertEqual(set(pares.loc[pares.cliente.eq('A'),'sku']),{'30972','47489','7475','30644'})
        matrix=promotor_breakdown(df,['ung']).set_index('Promotores')
        self.assertEqual(matrix.loc['Fede','Tbd Ung'],4)
        self.assertEqual(matrix.loc['Mati','Tbd Ung'],2)

    def test_gin_no_ung_y_tonica_si(self):
        pares,pendientes=detalle_tbd_ung(ejemplo([('A','Fede','900355','',1)]))
        self.assertEqual(pares.sku.tolist(),['7476'])
        self.assertTrue(pendientes.empty)

    def test_combo_900404_tambien_cuenta_como_ccc_h2oh(self):
        df=ejemplo([('A','Fede','900404','',2)])
        flags,_=mask_por_indicador(df)
        self.assertTrue(bool(flags['h2oh'].iloc[0]))
        pares,pendientes=detalle_tbd_ung(df)
        self.assertEqual(set(pares.sku),{'29814','29816'})
        self.assertTrue(pendientes.empty)
        matrix=promotor_breakdown(df,['h2oh','ung']).set_index('Promotores')
        self.assertEqual(matrix.loc['Fede','Ccc H2oh'],1)
        self.assertEqual(matrix.loc['Fede','Tbd Ung'],2)

if __name__=='__main__':
    unittest.main()

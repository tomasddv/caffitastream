import unittest
from padron import cargar_padron
from motor import OBJETIVOS

class TestPadronVigente(unittest.TestCase):
    def test_padron_unico_940(self):
        p = cargar_padron()
        self.assertEqual(len(p), 940)
        self.assertEqual(p['cliente_codigo'].nunique(), 940)
        self.assertNotIn('3913', set(p['cliente_codigo']))
        self.assertNotIn('5430', set(p['cliente_codigo']))
        self.assertEqual(p.set_index('cliente_codigo').loc['5299','razon_social'], 'IGLESIAS NORBERTO MARTIN')
    def test_objetivo_no_depende_de_universo(self):
        self.assertEqual(OBJETIVOS['1890'], 941)

if __name__ == '__main__':
    unittest.main()

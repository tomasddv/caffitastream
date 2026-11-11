import unittest
from pathlib import Path
from padron import cargar_padron
import motor
ROOT=Path(__file__).resolve().parents[1]

class TestPadronNoviembre(unittest.TestCase):
    def test_dos_padrones_separados(self):
        old=cargar_padron(ROOT/'clientes_p1_p4_2026_10.csv')
        nov=cargar_padron(ROOT/'clientes_p1_p4_2026_11.csv')
        self.assertEqual(len(old),940)
        self.assertEqual(len(nov),1665)
        self.assertEqual(len(set(nov.cliente_codigo)),1665)
        self.assertIn('5306',set(nov.cliente_codigo))
    def test_perfiles_de_indicadores(self):
        motor.set_runtime_profile((2026,11))
        self.assertEqual(motor.OBJETIVOS['ung'],10324)
        self.assertEqual(motor.NOMBRES['redbull'],'CCC BLACK')
        motor.set_runtime_profile((2026,10))
        self.assertEqual(motor.NOMBRES['redbull'],'CCC RED BULL')
        self.assertEqual(motor.OBJETIVOS['ung'],10113)

if __name__=='__main__':unittest.main()

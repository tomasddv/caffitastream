import unittest
from pathlib import Path
from padron import cargar_padron, codigo_cliente
import motor

ROOT=Path(__file__).resolve().parents[1]

class TestPadronOficialNoviembre(unittest.TestCase):
    def test_padrones_historicos_y_oficial(self):
        octubre=cargar_padron(ROOT/'clientes_p1_p4_2026_10.csv')
        noviembre=cargar_padron(ROOT/'clientes_p1_p4_2026_11.csv')
        predeterminado=cargar_padron(ROOT/'clientes_p1_p4.csv')
        self.assertEqual(len(octubre), 940)
        self.assertEqual(len(noviembre), 957)
        self.assertEqual(noviembre.cliente_codigo.nunique(), 957)
        self.assertEqual(set(noviembre.cliente_codigo), set(predeterminado.cliente_codigo))
        self.assertIn('2674', set(noviembre.cliente_codigo))
        self.assertIn('100572', set(noviembre.cliente_codigo))
        self.assertNotIn('07054900100572',set(noviembre.cliente_codigo))

    def test_codigos_b2b_4_y_6_digitos(self):
        self.assertEqual(codigo_cliente('07054900002674'), '2674')
        self.assertEqual(codigo_cliente('07054900100572'), '100572')
        self.assertEqual(codigo_cliente(7054900002674), '2674')
        self.assertEqual(codigo_cliente('100572'), '100572')

    def test_perfiles_de_indicadores_independientes(self):
        try:
            motor.set_runtime_profile((2026,11))
            self.assertEqual(motor.OBJETIVOS['ung'], 10324)
            self.assertEqual(motor.NOMBRES['redbull'], 'CCC BLACK')
            motor.set_runtime_profile((2026,10))
            self.assertEqual(motor.NOMBRES['redbull'], 'CCC RED BULL')
            self.assertEqual(motor.OBJETIVOS['ung'], 10113)
        finally:
            motor.set_runtime_profile((2026,10))

if __name__ == '__main__': unittest.main()

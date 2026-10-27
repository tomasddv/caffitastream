import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from deploy_check import main

class TestDeployImports(unittest.TestCase):
    def test_compatibilidad_y_archivos(self):
        main()

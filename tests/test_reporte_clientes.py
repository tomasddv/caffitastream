import io
import unittest
import zipfile
import pandas as pd
from reporte_clientes import leer_reporte_clientes_xlsx, enriquecer_padron_1890

_NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'

def sample_xlsx():
    headers=['Cliente','Nombre de fantasia','Razon social',
             'Fuerza de venta 1 Descripcion personal comercial','Fuerza de venta 1 Ruta de venta']
    names=['Cliente', 'Nombre de fantasia', 'Razon social',
           'Fuerza de venta 1 Descripcion personal comercial','Fuerza de venta 1 Ruta de venta',
           'GALINA','PRUEBA','NICASTRO LUCAS']
    shared=''.join('<si><t>'+n+'</t></si>' for n in names)
    cells=''.join(f'<c r="{chr(65+i)}1" t="s"><v>{i}</v></c>' for i in range(len(headers)))
    row2='<c r="A2"><v>5</v></c><c r="B2" t="s"><v>5</v></c><c r="C2" t="s"><v>6</v></c><c r="D2" t="s"><v>7</v></c><c r="E2"><v>713</v></c>'
    xml=f'<worksheet xmlns="{_NS}"><sheetData><row r="1">{cells}</row><row r="2">{row2}</row></sheetData></worksheet>'
    with io.BytesIO() as b:
        with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('xl/sharedStrings.xml',f'<sst xmlns="{_NS}">{shared}</sst>')
            z.writestr('xl/worksheets/sheet1.xml',xml)
        return b.getvalue()


class TestReporteClientes(unittest.TestCase):
    def test_xlsx_parsing_y_promotor_automatico(self):
        reporte=leer_reporte_clientes_xlsx(sample_xlsx())
        self.assertEqual(len(reporte),1)
        r=reporte.iloc[0]
        self.assertEqual(r['cliente_codigo'],'5')
        self.assertEqual(r['nombre_fantasia'],'GALINA')
        self.assertEqual(r['promotor'],'Lucas')
        self.assertEqual(r['ruta_venta'],'713')

    def test_sin_cruce_no_elimina_ni_cambia_compra(self):
        padron=pd.DataFrame({'cliente_codigo':['5','3840'],'razon_social':['Prueba','Otro'],
                             'estado_1890':['Compró','No compró'],'bultos_neto_1890':[3,0]})
        r=leer_reporte_clientes_xlsx(sample_xlsx())
        out=enriquecer_padron_1890(padron,r)
        self.assertEqual(len(out),2)
        self.assertEqual(out['estado_1890'].tolist(),['Compró','No compró'])
        self.assertEqual(out['promotor'].tolist(),['Lucas','Sin asignar'])
        self.assertEqual(out['estado_cruce'].tolist(),['Coincide con reporte','No figura en reporte'])

    def test_codigos_p1p4_repetidos_rechazados(self):
        padron=pd.DataFrame({'cliente_codigo':['5','5'],'estado_1890':['Compró','Compró']})
        with self.assertRaises(ValueError):
            enriquecer_padron_1890(padron,leer_reporte_clientes_xlsx(sample_xlsx()))

if __name__ == '__main__':unittest.main()

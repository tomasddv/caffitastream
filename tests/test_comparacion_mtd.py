from datetime import date
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import comparacion_mtd as cm
import motor


def test_misma_fecha_noviembre_octubre():
    assert cm.rango_referencia((2026,11),date(2026,11,12))==(date(2026,10,1),date(2026,10,12))


def test_enero_diciembre_anterior():
    assert cm.rango_referencia((2027,1),date(2027,1,31))==(date(2026,12,1),date(2026,12,31))


def test_febrero_clips_day_31():
    assert cm.rango_referencia((2026,3),date(2026,3,31))==(date(2026,2,1),date(2026,2,28))


def test_bisiesto_29():
    assert cm.rango_referencia((2024,3),date(2024,3,31))==(date(2024,2,1),date(2024,2,29))


def test_no_cruzar_fecha_de_periodo_distinto():
    import pytest
    with pytest.raises(ValueError):
        cm.rango_referencia((2026,11),date(2026,10,11))


def test_positivo_negativo_cero_y_sin_base():
    actual=[{'id':'mi','real':50},{'id':'cero','real':30},{'id':'ung','real':4},{'id':'redbull','real':0}]
    anterior=[{'id':'mi','real':40},{'id':'cero','real':60},{'id':'ung','real':0},{'id':'redbull','real':0}]
    m=cm.variaciones(actual,anterior,provisional=True)
    assert m['mi']['delta']==10 and m['mi']['delta_pct']==.25
    assert m['cero']['delta']==-30 and m['cero']['delta_pct']==-.5
    assert m['ung']['delta']==4 and m['ung']['delta_pct'] is None
    assert m['redbull']['delta']==0 and m['redbull']['delta_pct'] is None
    assert all(x['provisional'] for x in m.values())


def test_mes_anterior_sin_datos_no_finge_cero():
    m=cm.variaciones([{'id':'mi','real':22}],[{'id':'core','real':12}])
    assert m['mi']['anterior'] is None
    assert m['mi']['delta'] is None


def test_misma_familia_pepsi_black_vs_ambos_meses():
    # Perfil noviembre aplicado a ambos. Aun si octubre tenía objetivo Red Bull,
    # aquí la referencia anterior se calcula con máscara BLACK, nunca Red Bull.
    motor.set_runtime_profile((2026,11))
    import pandas as pd
    x=pd.DataFrame({
        'sku':['30793','16371','30791'],
        'marca':['PEPSI BLACK','RED BULL','PEPSI BLACK'],
        'descripcion':['PEPSI BLACK 354CC','RED BULL 250CC','PEPSI BLACK 500CC'],
        'calibre':['354 CC CAN','250 CC LATA','500 CC PET'],
        'division':['GASEOSAS','BEBIDAS ENERGIZANTES','GASEOSAS'],
        'unidad':['UNG','UNG','UNG'],
    })
    flags,_=motor.mask_por_indicador(x)
    assert flags['redbull'].tolist()==[True,False,True]
    motor.set_runtime_profile((2026,10))


def test_html_muestra_vs_en_tarjeta_sin_cambiar_objetivos():
    import ast, html
    from datetime import date
    app_file=Path(__file__).resolve().parents[1] / 'app.py'
    tree=ast.parse(app_file.read_text(encoding='utf-8'))
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('fnum','vs_mes_html','cards_html')]
    namespace={'date':date,'html':html,'picture':lambda k:'',}
    exec(compile(ast.Module(body=funcs,type_ignores=[]),str(app_file),'exec'),namespace)
    d={'id':'ung','nombre':'TBD UNG','objetivo':10324,'real':40,'alcance':40/10324,'faltan':10284,'cobertura':None,'estado':'CALCULADO'}
    dif={'ung':{'actual':40,'anterior':32,'delta':8,'delta_pct':.25,'provisional':True}}
    html_card=namespace['cards_html']([d],dif,date(2026,10,12))
    assert 'Objetivo' in html_card and '10.324' in html_card
    assert 'VS 12/10/2026' in html_card and 'Anterior 32' in html_card
    assert 'Δ +8 (+25,0%)' in html_card and 'PROVISORIO' in html_card
    assert 'MTD 40' in html_card

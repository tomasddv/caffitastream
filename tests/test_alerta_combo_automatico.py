"""Pruebas del circuito de nuevos combos: detección, carga, impacto y persistencia."""
import sys
from pathlib import Path
import datetime as dt
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import motor
import gestion_combos as gc


def ventas_simuladas():
    return pd.DataFrame([
        {'cliente':'5','sku':'900999','descripcion':'COMBO PURE GOLD NUEVO','fecha':pd.Timestamp('2026-10-29'),'bultos':2,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'5','sku':'900999','descripcion':'COMBO PURE GOLD NUEVO','fecha':pd.Timestamp('2026-10-29'),'bultos':-1,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'6','sku':'900999','descripcion':'COMBO PURE GOLD NUEVO','fecha':pd.Timestamp('2026-10-29'),'bultos':1,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'7','sku':'900998','descripcion':'COMBO SIN VENTA NETA','fecha':pd.Timestamp('2026-10-29'),'bultos':1,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'7','sku':'900998','descripcion':'COMBO SIN VENTA NETA','fecha':pd.Timestamp('2026-10-29'),'bultos':-1,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'8','sku':'900474','descripcion':'COMBO CATALOGADO','fecha':pd.Timestamp('2026-10-29'),'bultos':1,'unidad':'','marca':'','calibre':'','division':''},
        {'cliente':'10','sku':'49807','descripcion':'STELLA PURE GOLD CAN','fecha':pd.Timestamp('2026-10-29'),'bultos':1,'unidad':'CERVEZAS CMQ','marca':'STELLA ARTOIS PURE GOLD','calibre':'473 CC LATAS','division':'CERVEZAS'},
    ])


def test_aviso_detecta_solo_nuevos_con_compra_neta():
    x=ventas_simuladas()
    d=gc.combos_sin_catalogar(x,{'900474'})
    assert d['Código combo'].tolist()==['900999']
    assert d.iloc[0]['Clientes compradores']==2
    assert d.iloc[0]['Bultos netos']==2


def test_componentes_manuales_autocompletan_metadata():
    ref=gc.referencia_articulos(ventas_simuladas())
    filas=gc.construir_filas('900999','49807',ref)
    assert filas.iloc[0].loc['marca']=='STELLA ARTOIS PURE GOLD'
    assert filas.iloc[0].loc['unidad_negocio']=='CERVEZAS CMQ'
    assert filas.iloc[0].loc['articulo_componente']=='49807'


def test_no_se_inventan_datos_si_sku_desconocido():
    ref=gc.referencia_articulos(ventas_simuladas())
    with pytest.raises(ValueError,match='Completá'):
        gc.construir_filas('900999','777777',ref)
    borrador=gc.borrador_filas('900999','777777',ref)
    borrador.loc[0,['descripcion','unidad_negocio','marca','calibre','division']]=['PURE GOLD LATA','CERVEZAS CMQ','STELLA ARTOIS PURE GOLD','473 CC LATAS','CERVEZAS']
    guardado=gc.construir_filas('900999','777777',ref,borrador)
    assert guardado.iloc[0]['marca']=='STELLA ARTOIS PURE GOLD'


def test_no_permite_codigos_repetidos_ni_reemplazos_no_solicitados():
    ref=gc.referencia_articulos(ventas_simuladas())
    with pytest.raises(ValueError,match='repetir'):
        gc.construir_filas('900999','49807,49807',ref)
    filas=gc.construir_filas('900999','49807',ref)
    with pytest.raises(ValueError,match='ya tiene composición'):
        gc.fusionar_catalogo(filas,filas)


def test_se_recupera_900474_y_cuenta_en_ambos_ccc():
    cat=gc.leer_catalogo(ROOT/'combo_componentes.csv')
    d=cat.loc[cat['codigo'].eq('900474')]
    assert set(d['articulo_componente'])=={'49807','47707'}
    assert {'pure_gold','cervezas'}.issubset(motor.familias_por_componentes()['900474'])
    assert {'pure_gold','cervezas'}.issubset(set(motor.COMBOS['900474']))
    assert '900474' not in gc.combos_sin_catalogar(ventas_simuladas(),set(motor.COMBOS)|set(cat.codigo))['Código combo'].tolist()


def test_guardado_github_utiliza_sha_y_nunca_sobre_escribe_si_cambio(monkeypatch):
    import hashlib
    class Resp:
        def __init__(self,status,body):self.status_code=status;self.body=body
        def json(self):return self.body
    original=b'codigo\n'
    sha=hashlib.sha1(f'blob {len(original)}\0'.encode()+original).hexdigest()
    calls=[]
    monkeypatch.setattr(gc.requests,'get',lambda url,**kwargs:Resp(200,{'sha':sha}))
    monkeypatch.setattr(gc.requests,'put',lambda url,**kwargs:(calls.append(kwargs['json']),Resp(200,{'commit':{'html_url':'https://github.com/tomasddv/caffitastream/commit/abc'}}))[1])
    url=gc.guardar_csv_github(b'new bytes','secret',original=original)
    assert url.endswith('/abc') and calls[0]['sha']==sha
    with pytest.raises(ValueError,match='cambió en GitHub'):
        gc.guardar_csv_github(b'new bytes','secret',original=b'otra version')
    assert len(calls)==1


def test_edicion_requiere_token_y_pin(monkeypatch):
    assert gc.permisos_edicion({'GITHUB_TOKEN':'abc','COMBO_EDITOR_PIN':'1234'},'1234')==(True,True)
    assert gc.permisos_edicion({'GITHUB_TOKEN':'abc','COMBO_EDITOR_PIN':'1234'},'0000')==(False,True)
    assert gc.permisos_edicion({'GITHUB_TOKEN':'abc'},'1234')==(False,False)


def test_una_composicion_nueva_actualiza_familias_y_flags_sin_editar_codigo(monkeypatch,tmp_path):
    # Simula exactamente el CSV que un usuario cargaría desde la interfaz.
    base=gc.leer_catalogo(ROOT/'combo_componentes.csv')
    ref=gc.referencia_articulos(ventas_simuladas())
    nuevo=gc.construir_filas('900999','49807',ref)
    fusion=gc.fusionar_catalogo(base,nuevo)
    (tmp_path/'combo_componentes.csv').write_bytes(gc.csv_catalogo(fusion))
    monkeypatch.setattr(motor,'RAIZ',tmp_path)
    assert 'pure_gold' in motor.familias_por_componentes()['900999']
    assert 'cervezas' in motor.familias_por_componentes()['900999']
    flags,_=motor.mask_por_indicador(ventas_simuladas())
    assert flags['pure_gold'].loc[0] and flags['cervezas'].loc[0]
    assert not flags['mi'].loc[0]

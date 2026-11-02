"""Selección automática y verificable de fuentes mensuales de CHESS en Drive.

Solamente se ofrecen el mes corriente y el anterior. La enumeración pública
por nombre usa gdown (carpeta compartida). Los ID conocidos son contingencia,
no se inventan IDs ni se mezclan períodos si el inventario falla.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import unicodedata
import pandas as pd

FOLDER_ID = '1cukgXLUaPsEDK_yD7tSwgaBFZAbiDUot'
MES_NOMBRES = ('enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre')
# IDs comprobados al 2/11/2026. Se usan sólo si la enumeración pública falla.
FALLBACK = {
    'ventadiaria.txt':'1I-vewZKeotS02twpDgSnmAbYjKT4mlXG',
    'ventadiaria bultos.txt':'169T6XFTCJpPManqx3dUR_-0nR1rJ4TZT',
    'ventadiaria octubre.txt':'190CTcpwpXnb3r8jBMnwDYJVWsED8hVI2',
}


def slug(name:str)->str:
    s=unicodedata.normalize('NFKD',str(name)).encode('ascii','ignore').decode('ascii').lower().strip()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()


def filename_info(name:str):
    """(clase, mes) o None; acepta las dos posiciones de 'bultos' en el nombre."""
    p=Path(str(name)).name
    if not p.lower().endswith('.txt'):
        return None
    words=slug(p[:-4]).split()
    if not words or words[0] not in ('ventadiaria','ventadaria') and words[:2]!=['venta','diaria']:
        return None
    words=words[1:] if words[0] in ('ventadiaria','ventadaria') else words[2:]
    kind='bultos' if 'bultos' in words else 'volumen'
    words=[w for w in words if w not in ('bultos','mes','cerrado')]
    if not words: return kind,None
    # Evitar reconocer otros archivos por coincidencia parcial.
    if len(words)!=1 or words[0] not in MES_NOMBRES:
        return None
    return kind,MES_NOMBRES.index(words[0])+1


def mes_anterior(hoy:date)->tuple[int,int]:
    return (hoy.year-1,12) if hoy.month==1 else (hoy.year,hoy.month-1)


def periodo_nombre(ym:tuple[int,int]):
    return f'{MES_NOMBRES[ym[1]-1].capitalize()} {ym[0]}'


def periodo_bounds(ym:tuple[int,int]):
    from calendar import monthrange
    y,m=ym
    return date(y,m,1),date(y,m,monthrange(y,m)[1])


def inventario_publico():
    """La API pública de gdown devuelve id/path sin descargar archivos.

    Si falla el listado (cambios de Google o permisos), el llamador usa los
    ID conocidos de contingencia y avisa en pantalla.
    """
    import gdown
    items=gdown.download_folder(id=FOLDER_ID,skip_download=True,remaining_ok=True,
                                quiet=True,use_cookies=False)
    if items is None:
        raise RuntimeError('Drive no permitió enumerar los archivos de la carpeta pública')
    out={}
    for item in items:
        name=Path(str(item.path)).name
        if filename_info(name) is not None and getattr(item,'id',None):
            out[name]=str(item.id)
    if not out:
        raise ValueError('Drive no devolvió TXT de ventas reconocibles en la carpeta')
    return out


def fuentes_por_periodo(files:dict[str,str], hoy:date):
    """Solo los dos períodos válidos. Asignaciones nunca cruzan meses."""
    current=(hoy.year,hoy.month); previous=mes_anterior(hoy)
    out={current:{'volumen':None,'bultos':None},previous:{'volumen':None,'bultos':None}}
    seen={}
    for name,id in files.items():
        info=filename_info(name)
        if not info: continue
        kind,m=info
        for ym in out:
            # sin sufijo = fuente viva y sólo puede ser del mes corriente
            if (m is None and ym==current) or (m==ym[1] and ym==previous):
                key=(ym,kind)
                if key in seen and seen[key]!=id:
                    raise ValueError(f'Hay fuentes duplicadas para {periodo_nombre(ym)} / {kind}.')
                seen[key]=id
                out[ym][kind]=id
    return out


def filtrar_y_validar_mes(df:pd.DataFrame, ym:tuple[int,int]):
    from motor import prepare
    dates=prepare(df)['fecha']
    if dates.isna().any():
        raise ValueError('Se encontraron fechas no reconocidas en el TXT.')
    selected=dates.dt.year.eq(ym[0]) & dates.dt.month.eq(ym[1])
    if not selected.any():
        raise ValueError(f'El archivo no contiene ventas de {periodo_nombre(ym)}.')
    if not selected.all():
        different=int((~selected).sum())
        raise ValueError(f'El TXT contiene {different} filas fuera de {periodo_nombre(ym)}; revisá el archivo antes de usarlo.')
    return df


def volumen_para_conteo(raw:pd.DataFrame)->pd.DataFrame:
    """Contingencia si el archivo de bultos cerrado se extravió.

    No reconstruye bultos y no permite validar íntegramente el cierre. Para
    combos con volumen cero usa sólo signo de importe como aproximación.
    """
    from motor import decimal
    out=raw.copy()
    codigo=out['Código'].astype(str).str.strip()
    is_combo=codigo.str.fullmatch(r'900\d{3}')
    vol=decimal(out['Cantidades Totales'])
    importe=decimal(out['Importes Netos'])
    replacement=pd.Series(0.0,index=out.index)
    replacement.loc[is_combo & vol.eq(0) & importe.gt(0)]=1.
    replacement.loc[is_combo & vol.eq(0) & importe.lt(0)]=-1.
    # El motor usa la columna para decidir compra neta positiva. Es hectolitros,
    # no bultos, en este modo; la UI debe comunicarlo claramente.
    out.loc[is_combo & vol.eq(0),'Cantidades Totales']=replacement.loc[is_combo & vol.eq(0)].map(
        lambda x:str(int(x)))
    return out

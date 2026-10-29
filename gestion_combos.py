"""Detección y mantenimiento del catálogo de combos de DDV.

No requiere servicios externos para analizar ventas o preparar CSV. El guardado
persistente en GitHub es explícito y requiere credenciales en Streamlit Secrets.
"""
from __future__ import annotations

import hmac
import hashlib
import re
from pathlib import Path
import pandas as pd
import requests

COLUMNAS = ['codigo', 'articulo_componente', 'descripcion', 'unidad_negocio', 'marca', 'calibre', 'division', 'hl_por_combo']
PATRON_COMBO = re.compile(r'^900\d{3}$')


def cod(valor: object) -> str:
    s = str(valor).strip()
    if re.fullmatch(r'\d+\.0+', s):
        s = s.split('.')[0]
    return s.lstrip('0') if s.isdigit() else ''


def leer_catalogo(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=COLUMNAS)
    d = pd.read_csv(path, dtype=str, encoding='utf-8-sig', keep_default_na=False)
    if not set(COLUMNAS).issubset(d.columns):
        raise ValueError('combo_componentes.csv no tiene todas las columnas requeridas')
    return d[COLUMNAS].copy()


def combos_sin_catalogar(x: pd.DataFrame, codigos_conocidos: set[str]) -> pd.DataFrame:
    """Combos con compra neta positiva, no cubiertos por motor ni catálogo.

    x debe contener ventas ya filtradas por período y CLIE PEOPLE. Se suma por
    cliente/combo para neutralizar devoluciones antes de contar compradores.
    """
    combo = x.loc[x['sku'].astype(str).str.fullmatch(r'900\d{3}')].copy()
    combo['sku'] = combo['sku'].map(cod)
    combo = combo.loc[~combo['sku'].isin(codigos_conocidos) & combo['cliente'].ne('')]
    if combo.empty:
        return pd.DataFrame(columns=['Código combo','Descripción','Clientes compradores','Bultos netos','Última compra'])
    positivos = combo.groupby(['sku','cliente'], as_index=False)['bultos'].sum()
    positivos = positivos[positivos['bultos'] > 0]
    if positivos.empty:
        return pd.DataFrame(columns=['Código combo','Descripción','Clientes compradores','Bultos netos','Última compra'])
    combos = combo.merge(positivos[['sku','cliente']], on=['sku','cliente'])
    info = combos.sort_values('fecha').groupby('sku',as_index=False).agg(
        descripcion=('descripcion','last'), ultima=('fecha','max'))
    sums = positivos.groupby('sku',as_index=False).agg(clientes=('cliente','nunique'),netos=('bultos','sum'))
    out = sums.merge(info,on='sku').sort_values(['ultima','clientes'],ascending=[False,False])
    out.columns = ['Código combo','Clientes compradores','Bultos netos','Descripción','Última compra']
    return out[['Código combo','Descripción','Clientes compradores','Bultos netos','Última compra']].reset_index(drop=True)


def referencia_articulos(x:pd.DataFrame) -> pd.DataFrame:
    """Catálogo sugerido desde SKU reales individuales, sin inventar componentes."""
    y = x.loc[~x['sku'].astype(str).str.fullmatch(r'900\d{3}')].copy()
    y = y.loc[y['sku'].astype(str).ne('')].sort_values('fecha')
    y = y.drop_duplicates('sku',keep='last')
    return y.set_index('sku')[['descripcion','unidad','marca','calibre','division']]



def borrador_filas(codigo_combo: str, codigos: str, referencia:pd.DataFrame, catalogo:pd.DataFrame|None=None) -> pd.DataFrame:
    """Precompleta metadatos desde ventas; deja editables los SKU sin referencia."""
    combo=cod(codigo_combo)
    if not PATRON_COMBO.fullmatch(combo):
        raise ValueError('Código de combo inválido.')
    entradas=[cod(v) for v in re.split(r'[,;\s]+',codigos.strip()) if v.strip()]
    if not entradas or any(not s for s in entradas) or len(entradas)!=len(set(entradas)):
        raise ValueError('Ingresá SKU numéricos sin duplicados, separados por coma o salto de línea.')
    rows=[]
    for sku in entradas:
        matching=None
        if catalogo is not None and not catalogo.empty:
            subset=catalogo.loc[catalogo['articulo_componente'].map(cod).eq(sku)]
            if not subset.empty: matching=subset.iloc[0].to_dict()
        reference=referencia.loc[sku].to_dict() if sku in referencia.index else {}
        if isinstance(reference,pd.DataFrame):reference=reference.iloc[0].to_dict()
        fields={'codigo':combo,'articulo_componente':sku,
                'descripcion':reference.get('descripcion',''),'unidad_negocio':reference.get('unidad',''),
                'marca':reference.get('marca',''),'calibre':reference.get('calibre',''),
                'division':reference.get('division',''),'hl_por_combo':''}
        if matching:fields.update({k:v for k,v in matching.items() if k in COLUMNAS})
        fields['codigo']=combo
        rows.append(fields)
    return pd.DataFrame(rows,columns=COLUMNAS).fillna('')

def construir_filas(codigo_combo: str, codigos: str, referencia:pd.DataFrame, detalles:pd.DataFrame|None=None) -> pd.DataFrame:
    combo=cod(codigo_combo)
    if not PATRON_COMBO.fullmatch(combo):
        raise ValueError('El código del combo debe tener seis cifras y comenzar con 900.')
    entradas=[cod(v) for v in re.split(r'[,;\s]+',codigos.strip()) if v.strip()]
    if not entradas or any(not s for s in entradas) or len(entradas)!=len(set(entradas)):
        raise ValueError('Ingresá uno o más SKU numéricos, sin repetir códigos.')
    overrides={}
    if detalles is not None:
        for r in detalles.to_dict('records'):
            s=cod(r.get('articulo_componente',''))
            if s: overrides[s]=r
    rows=[]
    for sku in entradas:
        original=referencia.loc[sku] if sku in referencia.index else None
        if isinstance(original,pd.DataFrame): original=original.iloc[0]
        extra=overrides.get(sku,{})
        def val(field, source):
            manual=str(extra.get(field,'')).strip()
            return manual if manual else (str(original.get(source,'')).strip() if original is not None else '')
        d={'codigo':combo,'articulo_componente':sku,
           'descripcion':val('descripcion','descripcion'),
           'unidad_negocio':val('unidad_negocio','unidad'),
           'marca':val('marca','marca'),'calibre':val('calibre','calibre'),
           'division':val('division','division'),'hl_por_combo':str(extra.get('hl_por_combo','')).strip()}
        if not all(d[k] for k in ['descripcion','unidad_negocio','marca','calibre','division']):
            raise ValueError(f'SKU {sku}: no está completo en la venta diaria. Completá descripción, unidad, marca, calibre y división para clasificar sus CCC.')
        rows.append(d)
    return pd.DataFrame(rows,columns=COLUMNAS)


def fusionar_catalogo(catalogo:pd.DataFrame, nuevas:pd.DataFrame, reemplazar:bool=False) -> pd.DataFrame:
    if nuevas.empty: raise ValueError('No se agregaron componentes.')
    codigo_set=set(nuevas['codigo'].map(cod))
    if len(codigo_set)!=1:raise ValueError('Solo se puede editar un combo por operación.')
    codigo=next(iter(codigo_set))
    anteriores=catalogo.loc[catalogo['codigo'].map(cod).eq(codigo)]
    if not anteriores.empty and not reemplazar:
        raise ValueError(f'El combo {codigo} ya tiene composición en el catálogo. Seleccioná editar para reemplazarla.')
    resultado=pd.concat([catalogo.loc[~catalogo['codigo'].map(cod).eq(codigo)],nuevas],ignore_index=True)
    return resultado[COLUMNAS].copy()


def csv_catalogo(catalogo:pd.DataFrame) -> bytes:
    return catalogo[COLUMNAS].to_csv(index=False).encode('utf-8-sig')


def permisos_edicion(secrets, pin:str):
    """El PIN es obligatorio para no permitir edición a visitantes de la app."""
    try:
        configurado = str(secrets.get('COMBO_EDITOR_PIN',''))
        token = str(secrets.get('GITHUB_TOKEN',''))
    except Exception:
        return False,False
    return bool(configurado and token and hmac.compare_digest(pin, configurado)), bool(configurado and token)


def guardar_csv_github(content:bytes,token:str,repo:str='tomasddv/caffitastream',branch:str='main', *, original:bytes|None=None) -> str:
    """Commit atómico del catálogo a GitHub. No almacena tokens en archivos."""
    import base64
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):
        raise ValueError('GITHUB_REPO debe tener el formato usuario/repositorio.')
    if not re.fullmatch(r'[A-Za-z0-9_./-]+',branch):
        raise ValueError('La rama de GitHub no es válida.')
    url=f'https://api.github.com/repos/{repo}/contents/combo_componentes.csv'
    headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    response=requests.get(url,headers=headers,params={'ref':branch},timeout=25)
    if response.status_code != 200:
        raise ValueError(f'No pude leer el catálogo de GitHub (HTTP {response.status_code}). Revisá repositorio y permisos del token.')
    sha=response.json().get('sha')
    if not sha:raise ValueError('GitHub no devolvió el SHA necesario para evitar sobrescribir una versión diferente.')
    if original is not None:
        orig_sha=hashlib.sha1(f'blob {len(original)}\0'.encode()+original).hexdigest()
        if sha != orig_sha:
            raise ValueError('El catálogo cambió en GitHub desde que se abrió esta app. Recargá Streamlit antes de guardar para no borrar otro cambio.')
    payload={'message':'Actualizar composición de combos DDV desde Streamlit',
             'content':base64.b64encode(content).decode('ascii'),
             'sha':sha,'branch':branch}
    save=requests.put(url,headers=headers,json=payload,timeout=30)
    if save.status_code not in (200,201):
        msg='Otro usuario actualizó el catálogo. Recargá los datos antes de guardar.' if save.status_code==409 else 'Revisá permisos Contents: Read and write o la protección de la rama.'
        raise ValueError(f'GitHub no guardó los cambios (HTTP {save.status_code}). {msg}')
    commit=save.json().get('commit',{})
    return str(commit.get('html_url',f'https://github.com/{repo}/commits/{branch}'))

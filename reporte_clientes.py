"""Lectura del reporte de clientes de CHESS directamente desde Google Drive.

Este módulo utiliza únicamente bibliotecas estándar para extraer las columnas
necesarias del XLSX, sin leer archivos locales ni incluir el reporte en GitHub.
"""
from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from padron import codigo_cliente
from motor import normalizar_promotor

# Fuente vigente: reporte de clientes.xlsx, carga del 26/10/2026; Drive ID nuevo.
REPORTE_CLIENTES_ID = '1VrxE5Tu1T_ruYkKf4eW3uiGoKlJcpCA6'
_NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
_REQUIRED = (
    'Cliente', 'Nombre de fantasia', 'Razon social',
    'Fuerza de venta 1 Descripcion personal comercial',
    'Fuerza de venta 1 Ruta de venta',
    'Descripcion subcanal',
)


def _col_idx(address: str) -> int:
    letters = re.match(r'^[A-Z]+', address)
    if not letters:
        raise ValueError(f'Referencia XLSX inválida: {address}')
    value = 0
    for ch in letters.group():
        value = value * 26 + ord(ch) - ord('A') + 1
    return value - 1


def _text(cell, shared: list[str]) -> str:
    kind = cell.attrib.get('t', '')
    v = cell.find(_NS + 'v')
    if kind == 'inlineStr':
        return ''.join(t.text or '' for t in cell.iter(_NS + 't')).strip()
    if v is None or v.text is None:
        return ''
    if kind == 's':
        idx = int(v.text)
        return shared[idx].strip() if 0 <= idx < len(shared) else ''
    return v.text.strip()


def leer_reporte_clientes_xlsx(raw: bytes) -> pd.DataFrame:
    """Devuelve un registro único por código de cliente desde Hoja1.

    No interpreta ventas: las compras se determinan exclusivamente en ventadiaria.
    """
    if not raw[:2] == b'PK':
        raise ValueError('El reporte de clientes descargado no es un archivo Excel XLSX.')
    with zipfile.ZipFile(io.BytesIO(raw)) as book:
        if 'xl/sharedStrings.xml' in book.namelist():
            with book.open('xl/sharedStrings.xml') as f:
                root = ET.parse(f).getroot()
            shared = [''.join(node.text or '' for node in si.iter(_NS + 't')) for si in root.findall(_NS + 'si')]
        else:
            shared = []
        if 'xl/worksheets/sheet1.xml' not in book.namelist():
            raise ValueError('El reporte no incluye la Hoja1 esperada.')
        headers = {}
        records = []
        with book.open('xl/worksheets/sheet1.xml') as f:
            for _, row in ET.iterparse(f, events=('end',)):
                if row.tag != _NS + 'row':
                    continue
                rownum = int(row.attrib.get('r', '0'))
                if rownum == 1:
                    for cell in row.findall(_NS+'c'):
                        headers[_text(cell, shared)] = _col_idx(cell.attrib.get('r',''))
                    missing = set(_REQUIRED) - headers.keys()
                    if missing:
                        raise ValueError('El reporte cambió de estructura; faltan columnas: '+', '.join(sorted(missing)))
                    wanted = {headers[col]: col for col in _REQUIRED}
                elif rownum >= 2:
                    chosen = {}
                    for cell in row.findall(_NS+'c'):
                        idx = _col_idx(cell.attrib.get('r', ''))
                        if idx in wanted:
                            chosen[wanted[idx]] = _text(cell, shared)
                    if chosen.get('Cliente', ''):
                        records.append(chosen)
                row.clear()
    result=pd.DataFrame.from_records(records, columns=list(_REQUIRED)).fillna('')
    if result.empty:
        raise ValueError('REPORTE DE CLIENTES no tiene filas para cruzar con el padrón.')
    result['cliente_codigo'] = result['Cliente'].map(codigo_cliente)
    if result['cliente_codigo'].eq('').any():
        raise ValueError('El reporte contiene códigos de cliente inválidos.')
    if result['cliente_codigo'].duplicated().any():
        raise ValueError('El reporte contiene códigos de cliente repetidos: requiere revisar el origen.')
    result['promotor']=result['Fuerza de venta 1 Descripcion personal comercial'].map(
        lambda name: normalizar_promotor(name) if str(name).strip() else 'Sin asignar')
    result['promotor']=result['promotor'].replace('Sin promotor','Sin asignar')
    return result.rename(columns={
        'Nombre de fantasia':'nombre_fantasia',
        'Razon social':'razon_social_reporte',
        'Fuerza de venta 1 Ruta de venta':'ruta_venta',
        'Descripcion subcanal':'subcanal',
    })[['cliente_codigo','nombre_fantasia','razon_social_reporte','promotor','ruta_venta','subcanal']]


def clientes_clie_people(reporte: pd.DataFrame) -> set[str]:
    """Códigos clasificados exactamente como CLIE PEOPLE en el subcanal de CHESS.

    No confundir con 'Categoria' ni 'Categoría' impositiva del XLSX.
    """
    if not {'cliente_codigo', 'subcanal'}.issubset(reporte.columns):
        raise ValueError('Faltan código o subcanal en REPORTE DE CLIENTES; no se puede aplicar la exclusión CLIE PEOPLE.')
    categoria = reporte['subcanal'].fillna('').astype(str).str.upper().str.replace(r'\s+', ' ', regex=True).str.strip()
    return set(reporte.loc[categoria.eq('CLIE PEOPLE'), 'cliente_codigo'])


def filtrar_padron_people(padron: pd.DataFrame, excluidos: set[str]) -> pd.DataFrame:
    """Elimina CLIE PEOPLE también del universo de cobertura de 1890 P1+P4."""
    return padron.loc[~padron['cliente_codigo'].isin(excluidos)].copy()

def enriquecer_padron_1890(detalle: pd.DataFrame, reporte: pd.DataFrame) -> pd.DataFrame:
    """Cruza por código normalizado, conservando todos los P1+P4 sin inventar datos."""
    if detalle['cliente_codigo'].duplicated().any():
        raise ValueError('El padrón P1+P4 tiene códigos de cliente duplicados.')
    base = detalle.merge(reporte, on='cliente_codigo', how='left', validate='one_to_one', indicator=True)
    base['estado_cruce'] = base['_merge'].map({'both':'Coincide con reporte','left_only':'No figura en reporte'}).astype(str)
    base.drop(columns=['_merge'], inplace=True)
    base['nombre_fantasia'] = base['nombre_fantasia'].fillna('').str.strip()
    base['nombre_fantasia'] = base['nombre_fantasia'].mask(base['nombre_fantasia'].eq(''), 'Sin nombre de fantasía')
    base['promotor'] = base['promotor'].fillna('').str.strip()
    base['promotor'] = base['promotor'].mask(base['promotor'].eq(''), 'Sin asignar')
    base['ruta_venta'] = base['ruta_venta'].fillna('').str.strip()
    return base

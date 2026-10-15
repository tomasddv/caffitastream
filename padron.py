"""Padrón P1+P4 de DDV: consolidación y cruce por código de cliente.

El padrón contiene dos archivos de origen. No se presupone cuál representa
P1 o P4 de manera individual: los archivos se tratan como un único universo.
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

PADRON_PATH = Path(__file__).resolve().parent / 'clientes_p1_p4.csv'
PREFIJO_BEES = '0705490000'


def codigo_cliente(valor: object) -> str:
    """Normaliza códigos sencillos o IDs BEES completos, sin mezclar nombres."""
    if pd.isna(valor):
        return ''
    cadena = str(valor).strip()
    if re.fullmatch(r'\d+\.0+', cadena):
        cadena = cadena.split('.')[0]
    if not cadena.isdigit():
        return ''
    if cadena.startswith(PREFIJO_BEES) and len(cadena) > len(PREFIJO_BEES):
        cadena = cadena[len(PREFIJO_BEES):]
    return str(int(cadena)) if cadena else ''


def normalizar_serie(serie: pd.Series) -> pd.Series:
    return serie.map(codigo_cliente)


def cargar_padron(path: str | Path = PADRON_PATH) -> pd.DataFrame:
    padron = pd.read_csv(path, encoding='utf-8-sig', dtype=str, keep_default_na=False)
    requeridas = {'cliente_codigo', 'razon_social', 'sucursal', 'origen'}
    if not requeridas.issubset(padron.columns):
        raise ValueError('El padrón P1+P4 no contiene las columnas esperadas.')
    padron['cliente_codigo'] = normalizar_serie(padron['cliente_codigo'])
    if padron['cliente_codigo'].eq('').any():
        raise ValueError('El padrón tiene códigos de cliente vacíos o inválidos.')
    if padron['cliente_codigo'].duplicated().any():
        raise ValueError('El padrón P1+P4 tiene códigos duplicados.')
    return padron


def sugerir_columna_cliente(ventas: pd.DataFrame, padron: pd.DataFrame, excluir: set[str] | None = None) -> tuple[str | None, int]:
    """Sugiere la columna con más coincidencias comprobables con el padrón.
    Nunca permite que el SKU o la descripción actúen como cliente.
    """
    ignorar = excluir or set()
    universo = set(padron['cliente_codigo'])
    mejor_columna, mejor_puntaje = None, 0
    muestra = ventas.head(6000)
    for col in ventas.columns:
        if col in ignorar:
            continue
        valores = normalizar_serie(muestra[col])
        matches = valores[valores.isin(universo) & valores.ne('')]
        cantidad = len(matches)
        if cantidad > mejor_puntaje:
            mejor_columna, mejor_puntaje = col, cantidad
    return mejor_columna, mejor_puntaje


def detalle_compradores(padron: pd.DataFrame, clientes: pd.Series, mascara_producto: pd.Series,
                       cantidades: pd.Series | None, calculable: bool) -> pd.DataFrame:
    """Devuelve todos los clientes del padrón, con compra neta positiva si hay cantidades.
    Si no se puede evaluar la regla del producto, NO se marca como 'No compró'.
    """
    detalle = padron.copy()
    if not calculable:
        detalle['estado_1890'] = 'Sin cálculo'
        detalle['cantidad_neta_1890'] = pd.NA
        return detalle
    elegibles = mascara_producto & clientes.isin(set(padron['cliente_codigo']))
    if cantidades is None:
        compradores = set(clientes[elegibles & clientes.ne('')])
        detalle['estado_1890'] = detalle['cliente_codigo'].map(lambda c: 'Compró' if c in compradores else 'No compró')
        detalle['cantidad_neta_1890'] = pd.NA
    else:
        sales = pd.DataFrame({'codigo': clientes[elegibles], 'cantidad': cantidades[elegibles]})
        totales = sales.groupby('codigo')['cantidad'].sum() if len(sales) else pd.Series(dtype=float)
        detalle['cantidad_neta_1890'] = detalle['cliente_codigo'].map(totales).fillna(0)
        detalle['estado_1890'] = detalle['cantidad_neta_1890'].map(lambda v: 'Compró' if v > 0 else 'No compró')
    return detalle

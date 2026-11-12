"""Comparación de acumulados MTD del tablero DDV, sin dependencia de Streamlit.

Se compara un mismo indicador con la MISMA definición comercial en ambos meses;
el padrón P1/P4 de cada mes puede ser diferente. Los KPI no se fuerzan.
"""
from __future__ import annotations
from calendar import monthrange
from datetime import date


def mes_previo(ym:tuple[int,int])->tuple[int,int]:
    y,m=ym
    return (y-1,12) if m==1 else (y,m-1)


def rango_referencia(ym:tuple[int,int], fecha_corte:date)->tuple[date,date]:
    """Desde día 1 al mismo número de día del mes previo (o su último día)."""
    if (fecha_corte.year,fecha_corte.month)!=ym:
        raise ValueError('La fecha de corte no pertenece al mes seleccionado.')
    y,m=mes_previo(ym)
    return date(y,m,1),date(y,m,min(fecha_corte.day,monthrange(y,m)[1]))


def variaciones(rows_actual:list[dict],rows_anterior:list[dict],*,provisional:bool=False)->dict[str,dict]:
    """Devuelve comparables por ID de KPI, con diferencia absoluta y relativa.

    Si el mes anterior es 0, la variación porcentual no tiene denominador y se deja None.
    """
    prior={r['id']:r.get('real') for r in rows_anterior}
    result={}
    for row in rows_actual:
        k=row['id'];actual=row.get('real');anterior=prior.get(k)
        if actual is None or anterior is None:
            result[k]={'actual':actual,'anterior':anterior,'delta':None,'delta_pct':None,'provisional':provisional}
        else:
            diff=int(actual)-int(anterior)
            result[k]={'actual':int(actual),'anterior':int(anterior),'delta':diff,
                       'delta_pct':diff/int(anterior) if int(anterior)!=0 else None,
                       'provisional':provisional}
    return result

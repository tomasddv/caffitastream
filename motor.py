"""Motor de indicadores DDV: columnas fijas del export real de CHESS (sin mapeo manual).

Los KPI no definidos comercialmente se muestran como no validados, nunca como cero.
Los combos aportan a varios KPI cuando la composición conocida confirma producto.
"""
from __future__ import annotations
from pathlib import Path
import re
import unicodedata
import io
import pandas as pd

RAIZ=Path(__file__).resolve().parent
DIA_ID='190CTcpwpXnb3r8jBMnwDYJVWsED8hVI2'
BULTOS_ID='169T6XFTCJpPManqx3dUR_-0nR1rJ4TZT'
EXPECTED={"Cod. Cliente","Código","Descripción.2","Descripción.3","Descripción.4","Descripción.5","Descripción.8","Cantidades Totales","Descripción Período"}
OBJETIVOS={"pure_gold":259,"mi":340,"cero":526,"cervezas":1179,"1890":941,"latones":832,"core":376,"ung":10113,"h2oh":326,"redbull":270}
NOMBRES={"pure_gold":"CCC SA PURE GOLD","mi":"CCC MI","cero":"CCC 0.0%","cervezas":"CERVEZAS","1890":"Cobertura 1890 P1 & P4","latones":"CCC LATONES","core":"CCC INNOVACIONES CORE","ung":"TBD UNG","h2oh":"CCC H2OH!","redbull":"CCC RED BULL"}
PROMOTOR_LABELS={
    'h2oh':'Ccc H2oh','redbull':'Ccc Red bull','pure_gold':'Ccc Stella Pure Gold',
    'mi':'Ccc Michelob','cero':'Ccc 0.0','core':'Ccc Innovaciones Core',
    '1890':'Ccc 1890 P1/P4','latones':'Ccc Latones','cervezas':'Ccc Cervezas','ung':'Tbd Ung'
}
PROMOTOR_ALIASES={
    'FEDERICO BISS':'Fede','MATIAS GARCIA':'Mati','SIRI MARTIN':'Martin','NICOLAS POCHETINO':'Nico',
    'VILLAGRA ENZO':'Enzo','NICASTRO LUCAS':'Lucas','GASTON FABRE':'Gaston','MENDEZ CARLOS':'Carlos',
    'PABLO ALVAREZ':'Pablo','JUAN MANUEL GIMENEZ':'Juanma','MARIANO HERRERA':'Mariano',
    'ALEXANDER ROJAS':'Alex','FERNANDO FIELG':'Fer','':'Sin promotor'
}
PROMOTOR_ORDER=['Fede','Mati','Martin','Nico','Enzo','Lucas','Gaston','Carlos','Pablo','Juanma','Mariano','Alex','Fer','Sin promotor']

# Estas asignaciones son una fotografía conservadora de combos del catálogo del repositorio.
# Solamente se incluye en el KPI cuando el nombre o desglose ERP disponible permite concluir su pertenencia.
# Los combos de composición incompleta se muestran en Diagnóstico, no se inventan productos ocultos.
COMBOS={
 '900098':('ung',),'900226':(),
 '900299':('cervezas','latones'),'900311':('cervezas','latones'),
 '900329':('cervezas',),'900355':('ung',),
 '900376':('ung',),'900377':('ung',),
 '900381':('cervezas','pure_gold'),'900385':('ung',),
 '900391':('ung',),'900392':('ung',),'900393':('cervezas','pure_gold'),
 '900397':('ung',),'900398':('ung',),'900399':('cervezas','cero'),
 '900404':('ung','h2oh'),'900405':('ung',),'900406':('ung',),
 '900407':('cervezas','mi'),'900408':('ung',),'900409':('ung',),'900410':('ung',),
 '900411':('ung',),'900421':(),'900422':(),
 '900423':('ung','redbull'),'900424':('ung','redbull'),'900425':(), '900427':(),
 '900428':('cervezas','latones'), '900429':('cervezas','pure_gold'),
 '900430':('cervezas','pure_gold'), '900433':('ung',),
 '900435':('ung',),'900436':('ung',),'900438':('ung',),
 '900439':('ung','redbull'),'900440':('ung',),'900441':('ung','redbull'),
 '900444':('ung',), # mixto ECO + 2 UNG; sí aporta a distribución UNG
 '900445':('cervezas',),'900455':('ung','redbull'),
 '900456':('ung','redbull'),'900459':('ung',),'900460':('cervezas',),
 '900461':('cervezas','cero'),'900463':('cervezas','pure_gold'),
 '900464':('cervezas',),
}
# Desglose por *código exacto* según notas ERP del catálogo de combos de DDV.
# Confirmados en capturas de CHESS, 15/10/2026.
# El 900098 aporta sólo el SKU 7476 de Paso de los Toros Tónica a UNG;
# el gin 76363 no es un SKU UNG. El 900355 tiene otra variante de gin, igualmente no UNG.
COMBO_UNG_SKUS = {
    '900098': ('7476',),                              # gin + tónica, sólo tónica es UNG
    '900355': ('7476',),                              # gin AREA SUR + tónica; gin 77979 no es UNG
    '900376': ('1418','1422','11522'),                # Gatorade K+T SEP
    '900377': ('1413','1418','1422','11522'),         # Gatorade AS SEP
    '900391': ('591','627','22619'),                 # Mirinda SUR
    '900392': ('14624','14625','14638'),             # Gatorade 750cc
    '900397': ('30481','30648','30793','31074'),    # Latas PAT SUR
    '900404': ('29814','29816'),                     # H2OH! saborizadas
    '900408': ('30644','30645'),                     # Pepsi SUR
    '900409': ('30972','47489'),                     # 7UP PAT
    '900410': ('7475','30644','30972'),             # 1500cc PAT
    '900398': ('25645','30663','30791','30974'),
    '900438': ('30789','30790'),
    '900439': ('11522','16371'),
    '900440': ('1416','1418','11522','30647','30970'),
    '900441': ('16371','26422','29799'),
    '900444': ('30645','47489'),
    '900455': ('16371','22256'),
    '900456': ('16371','16372','26422','29799','32710','58089'),
    '900459': ('30791','30793'),
}

# Innovaciones Core confirmadas por el usuario (15/10/2026).
INNOVACIONES_269 = {'63068': 'Quilmes Clásica 269 cc', '15624': 'Brahma 269 cc'}
INNOVACIONES_FAMILIAS = (
    'Quilmes Clásica 269 cc', 'Brahma 269 cc',
    'Brahma FT Limón', 'Brahma FT Pomelo',
)
# SKUs precisos deducidos del texto y marcas de ventadiaria (no por coincidencias difusas).
SKU_1890={'29740','29743','51290'}


def canon(val):
    return re.sub(r'[^A-Z0-9]+', ' ',unicodedata.normalize('NFKD',str(val or '')).encode('ascii','ignore').decode('ascii').upper()).strip()


def normalizar_promotor(nombre:str):
    limpio=canon(nombre)
    return PROMOTOR_ALIASES.get(limpio, limpio.title() if limpio else 'Sin promotor')


def leer_tsv(raw:bytes):
    for cod in ('utf-8-sig','cp1252','latin1'):
        try:
            df=pd.read_csv(io.BytesIO(raw),sep='\t',encoding=cod,dtype=str,low_memory=False).fillna('')
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError('No se pudo detectar la codificación del archivo Drive')
    falta=EXPECTED-set(df.columns)
    if falta:
        raise ValueError('La fuente de ventas cambió: faltan columnas '+', '.join(sorted(falta)))
    return df


def decimal(s):
    return pd.to_numeric(s.astype(str).str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce').fillna(0)


def prepare(df):
    from padron import normalizar_serie
    x=pd.DataFrame(index=df.index)
    x['cliente']=normalizar_serie(df['Cod. Cliente'])
    x['sku']=df['Código'].astype(str).str.strip().str.lstrip('0').replace('', '0')
    x['descripcion']=df['Descripción.2'].astype(str).str.upper().str.strip()
    x['marca']=df['Descripción.3'].astype(str).str.upper().str.strip()
    x['calibre']=df['Descripción.4'].astype(str).str.upper().str.strip()
    x['division']=df['Descripción.5'].astype(str).str.upper().str.strip()
    x['sabor']=df['Descripción.7'].astype(str).str.upper().str.strip() if 'Descripción.7' in df.columns else ''
    x['unidad']=df['Descripción.8'].astype(str).str.upper().str.strip()
    x['bultos']=decimal(df['Cantidades Totales'])
    x['vendedor']=df['Vendedor'].astype(str).str.strip() if 'Vendedor' in df.columns else ''
    x['vendedor_descripcion']=df['Descripción Vendedor'].astype(str).str.upper().str.strip() if 'Descripción Vendedor' in df.columns else ''
    x['promotor']=x['vendedor_descripcion'].map(normalizar_promotor)
    months={'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12,
            'JAN':1,'APR':4,'AUG':8,'DEC':12}
    parts=df['Descripción Período'].str.strip().str.upper().str.extract(r'^(\d{1,2})[-/ ]([A-Z]{3})[-/ ](\d{2,4})$')
    y=pd.to_numeric(parts[2],errors='coerce');y=y.where(y>=100,2000+y)
    x['fecha']=pd.to_datetime(pd.DataFrame({'year':y,'month':parts[1].map(months),'day':pd.to_numeric(parts[0],errors='coerce')}),errors='coerce')
    if x['fecha'].isna().all():
        raise ValueError('No se reconocieron fechas en "Descripción Período"')
    return x


def clasificar_innovacion(sku, descripcion='', marca='', calibre='', division='', sabor=''):
    sku = str(sku).strip().lstrip('0')
    if sku in INNOVACIONES_269:
        return INNOVACIONES_269[sku]
    d, b, c, div, sabor_norm = (canon(x) for x in (descripcion, marca, calibre, division, sabor))
    is_brahma = b == 'BRAHMA' or bool(re.search(r'\bBRAHMA\b', d))
    is_quilmes_clasica = b in ('QUILMES', 'QUILMES CLASICA') or bool(re.search(r'\bQUILMES\s+CLASICA\b',d))
    is_269 = bool(re.search(r'\b269\b',c)) or bool(re.search(r'\b269\b',d))
    if is_269 and (div == 'CERVEZAS' or b in ('BRAHMA','QUILMES','QUILMES CLASICA')):
        if is_brahma: return 'Brahma 269 cc'
        if is_quilmes_clasica: return 'Quilmes Clásica 269 cc'
    marca_ft = bool(re.search(r'\bFT\b|\bFRESH\s+TWIST\b|\bFRUIT\s+TWIST\b',d+' '+b))
    if is_brahma and marca_ft:
        texto_sabor=d+' '+sabor_norm
        if re.search(r'\bLIMON\b',texto_sabor): return 'Brahma FT Limón'
        if re.search(r'\bPOMELO\b',texto_sabor): return 'Brahma FT Pomelo'
    return ''


def obtener_componentes_innovaciones():
    path=RAIZ/'combo_componentes.csv'
    if not path.exists():
        return {}
    cat=pd.read_csv(path,dtype=str,encoding='utf-8-sig').fillna('')
    columnas={'codigo','articulo_componente','descripcion','marca','calibre','division'}
    if not columnas.issubset(set(cat.columns)):
        raise ValueError('combo_componentes.csv no tiene las columnas necesarias: '+str(sorted(columnas-set(cat.columns))))
    result={}
    for r in cat.to_dict('records'):
        sku=str(r['articulo_componente']).strip().lstrip('0')
        grupo=clasificar_innovacion(sku,r['descripcion'],r['marca'],r['calibre'],r['division'])
        if grupo:
            codigo=str(r['codigo']).strip().lstrip('0')
            result.setdefault(codigo, {})[sku]=grupo
    return result


def detalle_tbd_ung(x: pd.DataFrame, por_promotor:bool=False):
    base=x.loc[x['cliente'].ne('')].copy()
    combo=base['sku'].isin(COMBOS) | base['sku'].str.match(r'^900\d{3}$')
    dims=['cliente','sku']
    if por_promotor:
        dims=['promotor']+dims
    ventas_directas=base.loc[~combo & base['unidad'].eq('UNG')].copy()
    totales_directos=ventas_directas.groupby(dims,as_index=False)['bultos'].sum()
    directos=totales_directos.loc[totales_directos['bultos'].gt(0),dims].copy()
    directos['origen']='SKU directo'

    combos=base.loc[combo].groupby((['promotor'] if por_promotor else [])+['cliente','sku'],as_index=False)['bultos'].sum()
    combos=combos[combos['bultos'].gt(0)]
    expansiones=[]
    for codigo,skus in COMBO_UNG_SKUS.items():
        clientes=combos.loc[combos['sku'].eq(codigo), (['promotor'] if por_promotor else [])+['cliente']]
        if clientes.empty:
            continue
        rep=clientes.loc[clientes.index.repeat(len(skus))].reset_index(drop=True)
        rep['sku']=list(skus)*len(clientes)
        rep['origen']=f'Combo {codigo}'
        expansiones.append(rep)
    from_combo=pd.concat(expansiones,ignore_index=True) if expansiones else pd.DataFrame(columns=dims+['origen'])
    pares=pd.concat([directos,from_combo],ignore_index=True)
    pares=pares.groupby(dims,as_index=False,sort=True).agg(origen=('origen', lambda v:', '.join(sorted(set(v)))))
    pendientes=combos.loc[combos['sku'].map(lambda code:'ung' in COMBOS.get(code,())) & ~combos['sku'].isin(COMBO_UNG_SKUS)]
    agg_dims=(['promotor'] if por_promotor else [])+['sku']
    pendientes=pendientes.groupby(agg_dims,as_index=False).agg(clientes=('cliente','nunique'),compras_netas=('bultos','sum')).sort_values(agg_dims).reset_index(drop=True)
    return pares,pendientes


def detalle_innovaciones(x:pd.DataFrame, por_promotor:bool=False):
    cols=['cliente','sku','descripcion','marca','calibre','division','bultos']
    if por_promotor:
        cols=['promotor']+cols
    base=x.loc[x['cliente'].ne(''),cols].copy()
    base['sabor']=x.loc[base.index,'sabor'] if 'sabor' in x.columns else ''
    combo=base['sku'].isin(COMBOS) | base['sku'].str.match(r'^900\d{3}$')
    directo=base.loc[~combo].copy()
    unique=directo[['sku','descripcion','marca','calibre','division','sabor']].drop_duplicates('sku').copy()
    unique['familia']=unique.apply(lambda r:clasificar_innovacion(r['sku'],r['descripcion'],r['marca'],r['calibre'],r['division'],r['sabor']),axis=1)
    directo=directo.merge(unique[['sku','familia']],on='sku',how='left')
    directo=directo[directo['familia'].fillna('').ne('')]
    dims=(['promotor'] if por_promotor else [])+['cliente','sku','familia']
    directos=directo.groupby(dims,as_index=False)['bultos'].sum()
    directos=directos.loc[directos['bultos'].gt(0),dims].copy()
    directos['origen']='Venta directa'

    composiciones=obtener_componentes_innovaciones()
    ventas_combo=base.loc[combo].groupby((['promotor'] if por_promotor else [])+['cliente','sku'],as_index=False)['bultos'].sum()
    ventas_combo=ventas_combo[ventas_combo['bultos'].gt(0)]
    expand=[]
    for codigo,componentes in composiciones.items():
        cliente_cols=(['promotor'] if por_promotor else [])+['cliente']
        clientes=ventas_combo.loc[ventas_combo['sku'].eq(codigo),cliente_cols].drop_duplicates().to_dict('records')
        for row in clientes:
            for sku,grupo in componentes.items():
                item=row.copy(); item.update({'sku':sku,'familia':grupo,'origen':'Combo '+codigo}); expand.append(item)
    de_combos=pd.DataFrame(expand,columns=(['promotor'] if por_promotor else [])+['cliente','sku','familia','origen'])
    pares=pd.concat([directos,de_combos],ignore_index=True)
    pares=pares.groupby(dims,as_index=False,sort=True).agg(origen=('origen',lambda vals:', '.join(sorted(set(vals)))))
    posible=ventas_combo.merge(base.loc[combo,['sku','descripcion']].drop_duplicates('sku'),on='sku',how='left')
    expresion=r'\b269\b|\bBRAHMA\b.*(?:\bFT\b|\bFRESH\s+TWIST\b|\bFRUIT\s+TWIST\b)'
    posible=posible.loc[posible['descripcion'].map(canon).str.contains(expresion,regex=True,na=False) & ~posible['sku'].isin(composiciones)]
    group_dims=(['promotor'] if por_promotor else [])+['sku','descripcion']
    sin_composicion=posible.groupby(group_dims,as_index=False).agg(clientes=('cliente','nunique'))
    resumen=pd.DataFrame({'familia':list(INNOVACIONES_FAMILIAS)})
    conteo=pares.groupby('familia',as_index=False).agg(clientes=('cliente','nunique'),skus=('sku','nunique')) if not pares.empty else pd.DataFrame(columns=['familia','clientes','skus'])
    resumen=resumen.merge(conteo,on='familia',how='left').fillna({'clientes':0,'skus':0})
    if not resumen.empty:
        resumen[['clientes','skus']]=resumen[['clientes','skus']].astype(int)
    return pares, resumen, sin_composicion


def mask_por_indicador(x):
    sku=x['sku'];marca=x['marca'];desc=x['descripcion'];cal=x['calibre'];division=x['division'];unidad=x['unidad'];is_combo=sku.isin(COMBOS.keys()) | sku.str.match(r'^900\d{3}$')
    ordinary=~is_combo
    flags={}
    flags['pure_gold']=ordinary & (marca.eq('STELLA ARTOIS PURE GOLD')|desc.str.contains('PURE GOLD',regex=False))
    flags['mi']=ordinary & (marca.eq('MICHELOB ULTRA')|desc.str.contains('MICHELOB',regex=False))
    flags['cero']=ordinary & (marca.isin(['STELLA ARTOIS 0.0%','QUILMES 0.0%','CORONA CERO']) | desc.str.contains(r'\b0[\.,]0\b',regex=True))
    flags['cervezas']=ordinary & (unidad.str.contains('CERVEZAS',regex=False)|division.eq('CERVEZAS'))
    flags['1890']=ordinary & (sku.isin(SKU_1890)|marca.eq('QUILMES 1890'))
    flags['latones']=ordinary & cal.str.contains(r'710\s*CC\s*LATAS',regex=True)
    flags['core']=ordinary & sku.isin(INNOVACIONES_269)
    flags['ung']=ordinary & unidad.eq('UNG')
    flags['h2oh']=ordinary & (marca.eq('H2OH')|desc.str.contains('H2OH',regex=False))
    flags['redbull']=ordinary & (marca.eq('RED BULL')|desc.str.contains('RED BULL|RB ZERO',regex=True))
    for k in flags:
        combo_skus={s for s,v in COMBOS.items() if k in v}
        if combo_skus:
            flags[k] = flags[k] | (is_combo & sku.isin(combo_skus))
    return flags,is_combo


def compute_sales(bultos:pd.DataFrame,padron:pd.DataFrame,desde=None,hasta=None, *, excluir_clientes:set[str]|None=None):
    """Calcula TODOS los KPI usando un único filtro de clientes excluidos.

    El DataFrame filtrado se reutiliza para detalle, promotores, ranking y TBD.
    """
    x=prepare(bultos)
    if excluir_clientes:
        x=x.loc[~x['cliente'].isin(excluir_clientes)].copy()
        padron=padron.loc[~padron['cliente_codigo'].isin(excluir_clientes)].copy()
    if desde is not None: x=x.loc[x['fecha'].dt.date>=desde].copy()
    if hasta is not None: x=x.loc[x['fecha'].dt.date<=hasta].copy()
    flags,is_combo=mask_por_indicador(x)
    padr=set(padron['cliente_codigo'])
    output=[];compradores_por_indicador={}
    pendientes_core=pd.DataFrame(); combos_pendientes_ung=pd.DataFrame()
    for k in OBJETIVOS:
        mask=flags[k] & x['cliente'].ne('')
        if k=='1890':mask=mask & x['cliente'].isin(padr)
        if k=='core':
            pares_core, _, pendientes_core=detalle_innovaciones(x)
            compradores=set(pares_core['cliente'])
            real=len(compradores)
        elif k=='ung':
            pares_ung, combos_pendientes_ung=detalle_tbd_ung(x)
            real=int(len(pares_ung))
            compradores=set(pares_ung['cliente'])
        else:
            venta=x.loc[mask,['cliente','bultos']]
            totales=venta.groupby('cliente',sort=False)['bultos'].sum()
            compradores=set(totales.index[totales.gt(0)])
            real=len(compradores)
        compradores_por_indicador[k]=compradores
        goal=OBJETIVOS[k]
        ratio=real/goal if real is not None else None
        coverage=real/len(padr) if k=='1890' and real is not None else None
        if k=='core':estado=('CALCULADO · Innovaciones 269 cc + Brahma FT (combos documentados)' if pendientes_core.empty else 'PARCIAL · revisar combos de innovaciones')
        elif k=='ung':estado=('PARCIAL · faltan SKU de '+str(len(combos_pendientes_ung))+' combos' if len(combos_pendientes_ung) else 'CALCULADO · cliente + SKU (incluye combos documentados)')
        elif k=='1890':estado='CALCULADO · combos 1890 sin composición confirmada'
        else:estado='CALCULADO · mapeo de combos conocidos'
        output.append({'id':k,'nombre':NOMBRES[k],'objetivo':goal,'real':real,'alcance':ratio,'faltan':max(0,goal-real) if real is not None else None,'cobertura':coverage,'estado':estado})
    detalle=padron.copy()
    detalle['estado_1890']=detalle['cliente_codigo'].map(lambda c:'Compró' if c in compradores_por_indicador['1890'] else 'No compró')
    known=x.loc[flags['1890'] & x['cliente'].isin(padr)].groupby('cliente')['bultos'].sum()
    detalle['bultos_neto_1890']=detalle['cliente_codigo'].map(known).fillna(0)
    combo_diagnostic=x.loc[is_combo & x['bultos'].ne(0),['sku','descripcion','cliente','bultos']].copy()
    combos_core=obtener_componentes_innovaciones()
    combo_diagnostic['familias_reconocidas']=combo_diagnostic['sku'].map(
        lambda v:', '.join(sorted(set(COMBOS.get(v,())) | ({'core'} if v in combos_core else set()))))
    combo_diagnostic['revisar']=combo_diagnostic['familias_reconocidas'].eq('')
    combo_group=combo_diagnostic.groupby(['sku','descripcion','familias_reconocidas','revisar'],dropna=False,as_index=False).agg(clientes=('cliente','nunique'),combos_vendidos=('bultos','sum'))
    return output,detalle,combo_group,x


def promotor_breakdown(x:pd.DataFrame, indicadores:list[str], padron:pd.DataFrame|None=None):
    flags,_=mask_por_indicador(x)
    if '1890' in indicadores and padron is None:
        raise ValueError('El indicador 1890 requiere el padrón P1/P4 para calcular por promotor.')
    padr=set(padron['cliente_codigo']) if padron is not None else set()
    base_promotores=[p for p in PROMOTOR_ORDER if p in set(x['promotor']) and p!='Sin promotor']
    extras=sorted(set(x['promotor'])-set(base_promotores)-{'Sin promotor'})
    promotores=base_promotores+extras
    if 'Sin promotor' in set(x['promotor']):
        promotores.append('Sin promotor')
    data=pd.DataFrame({'Promotores':promotores})
    for ind in indicadores:
        if ind=='ung':
            pares,_=detalle_tbd_ung(x,por_promotor=True)
            serie=pares.groupby('promotor').size()
        elif ind=='core':
            pares,_,_=detalle_innovaciones(x,por_promotor=True)
            serie=pares.groupby('promotor')['cliente'].nunique()
        else:
            mask=flags[ind] & x['cliente'].ne('')
            if ind=='1890':
                mask=mask & x['cliente'].isin(padr)
            venta=x.loc[mask,['promotor','cliente','bultos']].groupby(['promotor','cliente'],as_index=False)['bultos'].sum()
            serie=venta.loc[venta['bultos'].gt(0)].groupby('promotor')['cliente'].nunique()
        data[PROMOTOR_LABELS.get(ind,NOMBRES.get(ind,ind))]=data['Promotores'].map(serie).fillna(0).astype(int)
    total={col:(data[col].sum() if col!='Promotores' else 'Totales') for col in data.columns}
    data=pd.concat([data,pd.DataFrame([total])],ignore_index=True)
    return data


def validate_reconciliation(vol:pd.DataFrame,bul:pd.DataFrame):
    keys=['Descripción Período','Cod. Cliente','Código','Importes Netos']
    if len(vol)!=len(bul):return False,'Las fuentes tienen diferente cantidad de filas.'
    if not vol[keys].reset_index(drop=True).equals(bul[keys].reset_index(drop=True)):
        av=vol[keys].value_counts(dropna=False).sort_index()
        ab=bul[keys].value_counts(dropna=False).sort_index()
        if not av.equals(ab):return False,'Los TXT no corresponden al mismo conjunto de ventas.'
    return True,'Fuentes alineadas (fecha, cliente, producto e importe).'

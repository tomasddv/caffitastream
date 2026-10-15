"""DDV · Tablero conectado automáticamente a los dos TXT de Google Drive."""
from __future__ import annotations
import base64
import html
import tempfile
import os
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from padron import cargar_padron
from reporte_clientes import REPORTE_CLIENTES_ID, leer_reporte_clientes_xlsx, enriquecer_padron_1890
from motor import (
    DIA_ID,BULTOS_ID,NOMBRES,OBJETIVOS,leer_tsv,prepare,compute_sales,
    detalle_tbd_ung,detalle_innovaciones,validate_reconciliation,promotor_breakdown,
    PROMOTOR_LABELS
)

BASE=Path(__file__).resolve().parent
st.set_page_config(page_title='DDV | Indicadores automáticos',page_icon='📊',layout='wide')
st.markdown("""<style>
/* Paleta clara con todos los caracteres en negro, incluso en widgets y avisos. */
:root {color-scheme:light;}
html, body, .stApp, .stApp * {color:#000000 !important;}
.stApp, [data-testid="stAppViewContainer"] {background:#f7f9fc !important;}
[data-testid="stSidebar"] {background:#f1f4f8 !important;}
.block-container {padding-top:1rem;max-width:1650px;}
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"],
[data-testid="stDownloadButton"] button,
[data-testid="stFormSubmitButton"] button {
  background:#ffffff !important;border:1px solid #92a1b2 !important;
}
[data-testid="stTabs"] button, [data-testid="stTabs"] button * {
  color:#000000 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {background:#e8eef5 !important;}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"], [data-testid="stDataFrame"] * {
  color:#000000 !important;
}
[data-baseweb="select"] *, [data-baseweb="popover"] *,
[data-baseweb="tooltip"] *, [data-testid="stTooltipContent"] * {
  color:#000000 !important;
}
[data-baseweb="popover"], [data-baseweb="tooltip"],
[data-testid="stTooltipContent"] {background:#ffffff !important;}
</style>""",unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def drive_txt(file_id:str):
    urls=[('https://drive.google.com/uc',{'export':'download','id':file_id}),
          (f'https://drive.google.com/uc?export=download&id={file_id}',None)]
    failures=[]
    for url,params in urls:
        try:
            r=requests.get(url,params=params,timeout=90,allow_redirects=True)
            r.raise_for_status()
            data=r.content
            if len(data)<5000 or data[:1000].lower().find(b'<html')>=0:
                raise ValueError('Drive devolvió una página web, no el archivo TXT')
            return data
        except Exception as e:
            failures.append(str(e))
    try:
        import gdown
        with tempfile.TemporaryDirectory() as tmp:
            target=os.path.join(tmp,'venta.txt')
            downloaded=gdown.download(id=file_id,output=target,quiet=True,use_cookies=False)
            if not downloaded: raise ValueError('gdown no pudo acceder al archivo')
            data=Path(target).read_bytes()
            if len(data)<5000 or b'<html' in data[:1000].lower(): raise ValueError('Drive entregó HTML en vez de TXT')
            return data
    except Exception as e:
        failures.append(str(e))
    raise RuntimeError('No pude descargar el TXT desde Drive. '+ '; '.join(failures))

@st.cache_data(ttl=300,show_spinner=False)
def load_both():
    raw1=drive_txt(DIA_ID); raw2=drive_txt(BULTOS_ID)
    vol=leer_tsv(raw1); bul=leer_tsv(raw2)
    ok,exp=validate_reconciliation(vol,bul)
    if not ok:
        raise ValueError('Fuente desactualizada: '+exp+' El tablero no mostrará cifras inconsistentes.')
    return vol,bul


@st.cache_data(ttl=300, show_spinner=False)
def load_reporte_clientes():
    # Misma fuente de Drive, archivo XLSX. Nunca se guarda una copia de clientes en GitHub.
    return leer_reporte_clientes_xlsx(drive_txt(REPORTE_CLIENTES_ID))


def picture(k):
    path=BASE/'assets'/f'{k}.png'
    return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode('ascii') if path.exists() else ''


def fnum(v):
    if v is None:return '—'
    return f'{v:,.0f}'.replace(',','.')


def cards_html(results):
    out=[]
    for d in results:
        pct='—' if d['alcance'] is None else f'{d["alcance"]:.0%}'
        cov='—' if d['cobertura'] is None else f'{d["cobertura"]:.0%}'
        color='#b91c1c' if d['alcance'] is None or d['alcance']<0.8 else '#0f766e'
        progress=min(100,max(0,(d['alcance'] or 0)*100))
        cells=''.join(f'<div class="line"><span>{html.escape(label)}</span><strong class="{css}">{html.escape(str(value))}</strong></div>' for label,value,css in [
            ('Objetivo',fnum(d['objetivo']),''),('Real',fnum(d['real']),''),
            ('Alcance',pct,'attention'),('Faltan',fnum(d['faltan']),''),('Cobertura',cov,'')])
        out.append(f'''<article class="card"><div class="img"><img src="{picture(d['id'])}" alt="{html.escape(d['nombre'])}"/></div>
        <div class="heading">{html.escape(d['nombre'])}</div><div class="stats">{cells}
        <div class="bar"><div style="width:{progress:.1f}%;background:{color}"></div></div>
        <p>{html.escape(d['estado'])}</p></div></article>''')
    return ''.join(out)

STYLE='''<style>*{box-sizing:border-box;color:#000}body{font:14px Arial,sans-serif;color:#000;background:transparent;margin:0}
.group{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:12px;margin-bottom:18px}
.card{background:white;border:1px solid #dae1e9;border-radius:10px;overflow:hidden;min-width:0}
.img{height:95px;background:white;display:flex;align-items:center;justify-content:center;padding:7px}
.img img{height:auto;width:auto;max-height:82px;max-width:95%;object-fit:contain}
.heading{background:#e9eef4;color:#000;text-align:center;font-weight:700;font-size:13px;min-height:42px;display:flex;align-items:center;justify-content:center;padding:6px}
.stats{padding:8px 11px}.line{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #e6edf2;padding:6px 0;font-size:13px;gap:6px}
.line strong{font-size:14px;color:#000}.line strong.attention{color:#000}
.bar{height:5px;border-radius:6px;background:#e7edf3;margin:10px 0 8px;overflow:hidden}.bar div{height:100%}
p{margin:0;min-height:27px;font-size:10px;color:#000}
@media(max-width:1050px){.group{display:flex;overflow-x:auto}.card{min-width:185px;flex:1}}</style>'''


def promotor_table_html(df: pd.DataFrame):
    color_map={
        'Ccc H2oh':'#6eb6ff','Ccc Red bull':'#9db2ff','Ccc Stella Pure Gold':'#87d59d',
        'Ccc Michelob':'#2f8fef','Ccc 0.0':'#f0b4bd','Ccc Innovaciones Core':'#90d7a3',
        'Ccc 1890 P1/P4':'#f3c66d','Ccc Latones':'#ffd166','Ccc Cervezas':'#c7d2fe','Tbd Ung':'#b7a6ff'
    }
    cols=list(df.columns)
    metric_cols=cols[1:]
    # Cada encabezado usa exactamente el PNG de la primera solapa.
    by_label={nombre:codigo for codigo,nombre in PROMOTOR_LABELS.items()}
    max_by_col={c:max(1,int(df.iloc[:-1][c].max()) if len(df)>1 else 1) for c in metric_cols}
    header_cells=[]
    for c in cols:
        codigo=by_label.get(c)
        if codigo:
            img=picture(codigo)
            image_tag=f'<img src="{img}" alt="{html.escape(c)}" />' if img else ''
            header_cells.append(f'<th><div class="head-content">{image_tag}<span>{html.escape(c)}</span></div></th>')
        else:
            header_cells.append(f'<th class="th-name">{html.escape(c)}</th>')
    head=''.join(header_cells)
    body=[]
    for _,row in df.iterrows():
        is_total=str(row['Promotores']).lower()=='totales'
        tds=[f"<td class='name{' total' if is_total else ''}'>{html.escape(str(row['Promotores']))}</td>"]
        for c in metric_cols:
            v=int(row[c])
            w=(v/max_by_col[c])*100 if max_by_col[c] else 0
            bar=color_map.get(c,'#cbd5e1')
            cls='metric total' if is_total else 'metric'
            tds.append(f"<td class='{cls}'><div class='cellbar'><div class='fill' style='width:{w:.1f}%;background:{bar}'></div><span>{v}</span></div></td>")
        body.append('<tr>'+''.join(tds)+'</tr>')
    style='''<style>
    *{box-sizing:border-box;color:#000!important}
    body{margin:0;background:white;font-family:Arial,sans-serif}
    .prom-wrap{overflow-x:auto;max-width:100%;background:#fff;border:1px solid #cbd5e1}
    table.prom{border-collapse:collapse;min-width:1460px;width:100%;font-family:Arial,sans-serif;font-size:14px;background:white}
    table.prom th,table.prom td{border:1px solid #97a3b0;padding:0;color:#000!important}
    table.prom th{background:#edf1f6;color:#000!important;padding:5px 8px;text-align:center;font-weight:700;vertical-align:bottom}
    .head-content{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:3px;min-height:90px}
    .head-content img{width:110px;height:64px;object-fit:contain}
    .head-content span{display:block;min-height:30px;font-size:12px;line-height:1.2;color:#000!important}
    table.prom th.th-name{background:#dde4ec;vertical-align:bottom;padding-bottom:10px;min-width:108px}
    table.prom td.name{padding:6px 8px;background:#e9edf1;font-weight:600;white-space:nowrap;text-align:left}
    table.prom td.name.total{font-weight:700;background:#dce3ea}
    table.prom td.metric{min-width:115px;background:#f8fafc}
    table.prom td.metric.total{background:#efefef;font-weight:700}
    .cellbar{position:relative;height:28px;display:flex;align-items:center;justify-content:center;overflow:hidden}
    .cellbar .fill{position:absolute;left:2px;top:3px;bottom:3px;border-radius:0;opacity:.65}
    .cellbar span{position:relative;z-index:2;font-weight:700;color:#000!important}
    </style>'''
    html_table=style+"<div class='prom-wrap'><table class='prom'><thead><tr>"+head+"</tr></thead><tbody>"+''.join(body)+"</tbody></table></div>"
    return html_table

st.title('Distribuidora del Valle | Indicadores comerciales')
st.caption('Fuente exclusiva de ventas: Google Drive · Lectura automática de columnas · Incluye combos conocidos · Padrón P1 + P4')
padron=cargar_padron()

with st.sidebar:
    st.header('Actualización')
    st.caption('Fuentes: ventadiaria.txt, ventadiaria bultos.txt y REPORTE DE CLIENTES.xlsx · Google Drive')
    if st.button('🔄 Actualizar desde Drive',use_container_width=True):
        drive_txt.clear(); load_both.clear(); load_reporte_clientes.clear(); st.rerun()
    st.caption('Se lee al abrir y con Actualizar desde Drive. La caché vence cada 5 minutos.')
    st.metric('Padrón P1 + P4', f'{len(padron):,}'.replace(',','.'))

try:
    with st.spinner('Descargando ventas desde Google Drive y verificando los datos...'):
        vol,bultos=load_both()
    prep=prepare(bultos)
    fechas=prep['fecha'].dropna()
    if fechas.empty: raise ValueError('No se identificaron fechas de venta.')
    ultimo=fechas.max().date(); primero=fechas.min().date()
    hoy_ar=datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).date()
    corte_default=min(ultimo,hoy_ar)
    if corte_default < primero: raise ValueError('La fuente no contiene ventas correspondientes a fechas hasta hoy.')
    with st.sidebar:
        st.success(f'Drive conectado · {len(bultos):,} registros'.replace(',','.'))
        st.caption(f'Ventas cargadas: {primero:%d/%m/%Y} al {ultimo:%d/%m/%Y}')
        if ultimo>hoy_ar: st.warning('Drive contiene fechas futuras; por defecto se excluyen del indicador.')
        periodo=st.date_input('Período de análisis',value=(primero,corte_default),min_value=primero,max_value=ultimo)
    if isinstance(periodo,(tuple,list)) and len(periodo)==2:
        desde,hasta=periodo
    else:
        desde,hasta=primero,corte_default
    rows,detail,combos,xf=compute_sales(bultos,padron,desde,hasta)
    valid_ok=True
    reporte_error=''
    try:
        reporte_clientes=load_reporte_clientes()
        detail=enriquecer_padron_1890(detail,reporte_clientes)
        reporte_ok=True
    except Exception as err:
        # La lectura del padrón comercial no debe romper los restantes indicadores.
        reporte_ok=False
        reporte_error=str(err)
except Exception as e:
    st.error('No pude calcular los indicadores con la información actual de Drive: '+str(e))
    st.info('No se muestran ceros ficticios ni se solicita seleccionar columnas. Verificá la conexión a Internet y los permisos de los TXT.')
    rows=[{'id':k,'nombre':name,'objetivo':OBJETIVOS[k],'real':None,'alcance':None,'faltan':None,'cobertura':None,'estado':'SIN DATOS DE DRIVE'} for k,name in NOMBRES.items()]
    detail=None; combos=None; valid_ok=False; xf=None; ultimo=None; reporte_ok=False; reporte_error=""

tab_general, tab_promotor, tab_ranking = st.tabs(['📊 Indicadores generales','👥 CCC y TBD por promotor','🏆 Ranking'])

with tab_general:
    components.html(STYLE+'<div class="group" style="--n:3">'+cards_html(rows[:3])+'</div><div class="group" style="--n:7">'+cards_html(rows[3:])+'</div>',height=640,scrolling=True)
    if valid_ok:
        summary=pd.DataFrame(rows)
        st.caption(f'Corte de ventas: **{ultimo:%d/%m/%Y}** · Selección: **{desde:%d/%m/%Y} al {hasta:%d/%m/%Y}** · {len(xf):,} registros evaluados'.replace(',','.'))
        st.subheader('Seguimiento y detalle')
        resumen_vista=summary[['nombre','objetivo','real','alcance','faltan','cobertura','estado']].copy()
        for campo in ['alcance','cobertura']:
            resumen_vista[campo]=resumen_vista[campo].map(lambda v:f'{v:.1%}' if pd.notna(v) else '—')
        st.dataframe(resumen_vista,use_container_width=True,hide_index=True)
        st.download_button('Descargar indicadores CSV',summary.to_csv(index=False).encode('utf-8-sig'),file_name='ddv_indicadores.csv',mime='text/csv')

        st.subheader('Innovaciones Core · Brahma y Quilmes 269 cc + Brahma FT')
        st.caption('Real = clientes únicos con compra neta positiva de cualquier innovación. Un mismo cliente cuenta una sola vez, aunque compre varios SKU y bultos.')
        innov_pares, innov_resumen, innov_pendientes=detalle_innovaciones(xf)
        c1,c2,c3=st.columns(3)
        c1.metric('Clientes compradores de innovaciones',len(innov_pares['cliente'].unique()))
        c2.metric('Objetivo comercial',OBJETIVOS['core'])
        c3.metric('Alcance',f'{len(innov_pares["cliente"].unique()) / OBJETIVOS["core"]:.1%}')
        st.dataframe(innov_resumen.rename(columns={'familia':'Producto','clientes':'Clientes','skus':'SKU distintos vendidos'}),use_container_width=True,hide_index=True)
        with st.expander('Ver y descargar detalle de innovaciones por cliente y SKU'):
            st.dataframe(innov_pares,use_container_width=True,hide_index=True)
            st.download_button('Descargar clientes / SKU Innovaciones',innov_pares.to_csv(index=False).encode('utf-8-sig'),file_name='innovaciones_core_clientes_sku.csv',mime='text/csv')
            if not innov_pendientes.empty:
                st.warning('Hay combos relacionados con innovaciones cuyo desglose SKU no está confirmado. No se atribuyen productos sin evidencia.')
                st.dataframe(innov_pendientes,use_container_width=True,hide_index=True)
                st.download_button('Descargar combos de innovación por revisar',innov_pendientes.to_csv(index=False).encode('utf-8-sig'),file_name='innovaciones_core_combos_pendientes.csv',mime='text/csv')

        st.subheader('TBD UNG · SKU distintos por cliente')
        st.caption('Cada par cliente + código SKU de UNG suma 1 en el período, sin importar los bultos. Un SKU repetido, comprado directo o en combos documentados, se cuenta una sola vez.')
        tbd_pares, tbd_pendientes=detalle_tbd_ung(xf)
        k1,k2,k3=st.columns(3)
        k1.metric('TBD UNG calculado',f'{len(tbd_pares):,}'.replace(',','.'))
        k2.metric('Clientes compradores UNG',int(tbd_pares['cliente'].nunique()))
        k3.metric('Combos pendientes de desglose',int(len(tbd_pendientes)))
        with st.expander('Ver detalle cliente + SKU, y combos sin composición confirmada'):
            st.dataframe(tbd_pares,use_container_width=True,hide_index=True)
            st.download_button('Descargar cliente–SKU UNG',tbd_pares.to_csv(index=False).encode('utf-8-sig'),file_name='tbd_ung_cliente_sku.csv',mime='text/csv')
            if not tbd_pendientes.empty:
                st.warning('El Real de TBD UNG es parcial: estos combos contienen UNG pero todavía no tienen códigos componentes confirmados. No se los calcula como un SKU ficticio.')
                st.dataframe(tbd_pendientes,use_container_width=True,hide_index=True)
                st.download_button('Descargar combos UNG pendientes',tbd_pendientes.to_csv(index=False).encode('utf-8-sig'),file_name='tbd_ung_combos_pendientes.csv',mime='text/csv')

        st.subheader('1890 · P1 y P4 | Gestión por promotor')
        a,b,c=st.columns(3)
        a.metric('Clientes del padrón',len(padron))
        b.metric('Compraron 1890',int(detail['estado_1890'].eq('Compró').sum()))
        c.metric('No compraron 1890',int(detail['estado_1890'].eq('No compró').sum()))
        st.caption('Compras: TXT de ventas del período seleccionado. Nombre de fantasía y promotor asignado: REPORTE DE CLIENTES de Google Drive. La asignación comercial del reporte puede diferir del vendedor que realizó una venta.')
        if reporte_ok:
            sin_cruce=int(detail['estado_cruce'].eq('No figura en reporte').sum())
            sin_promotor=int(detail['promotor'].eq('Sin asignar').sum())
            if sin_cruce or sin_promotor:
                st.warning(f'Reporte de clientes: {len(detail)-sin_cruce} de {len(detail)} clientes vinculados. '
                           f'{sin_cruce} sin coincidencia y {sin_promotor} sin promotor asignado. '
                           'Estos clientes permanecen visibles para revisión.')
            # Filtros independientes del resultado comercial, sin modificar el Real general.
            promotores=['Todos']+sorted(detail['promotor'].dropna().unique().tolist(),
                                       key=lambda v:(v=='Sin asignar',v.casefold()))
            col_filtro1,col_filtro2=st.columns(2)
            with col_filtro1:
                promotor_1890=st.selectbox('Promotor asignado', promotores, key='p1p4_filtro_promotor')
            with col_filtro2:
                estado_1890=st.selectbox('Estado de compra 1890', ['Todos','No compró','Compró'],key='p1p4_filtro_compra')
            listado=detail.copy()
            if promotor_1890!='Todos':
                listado=listado[listado['promotor'].eq(promotor_1890)]
            if estado_1890!='Todos':
                listado=listado[listado['estado_1890'].eq(estado_1890)]
            ver=listado.rename(columns={
                'cliente_codigo':'Código de cliente', 'nombre_fantasia':'Nombre de fantasía',
                'razon_social':'Razón social', 'promotor':'Promotor', 'ruta_venta':'Ruta',
                'estado_1890':'Estado 1890', 'bultos_neto_1890':'Bultos netos 1890',
                'estado_cruce':'Coincidencia con reporte',
            })
            visible=[c for c in ['Código de cliente','Nombre de fantasía','Razón social',
                       'Promotor','Ruta','Estado 1890','Bultos netos 1890','Coincidencia con reporte'] if c in ver.columns]
            ver=ver[visible].sort_values(['Promotor','Estado 1890','Nombre de fantasía'],kind='stable')
            f1,f2,f3=st.columns(3)
            f1.metric('Clientes filtrados',len(ver))
            f2.metric('Compraron',int(listado['estado_1890'].eq('Compró').sum()))
            f3.metric('Pendientes de compra',int(listado['estado_1890'].eq('No compró').sum()))
            st.dataframe(ver,use_container_width=True,hide_index=True,height=400)
            nombre_seguro=re.sub(r'[^a-z0-9]+','_',promotor_1890.lower()).strip('_') if promotor_1890!='Todos' else 'todos'
            cdesc1,cdesc2=st.columns(2)
            with cdesc1:
                st.download_button('📥 Descargar listado filtrado',ver.to_csv(index=False).encode('utf-8-sig'),
                    file_name=f'1890_p1_p4_{nombre_seguro}.csv',mime='text/csv',key='1890_descargar_filtrado')
            pendientes=listado[listado['estado_1890'].eq('No compró')].copy().rename(columns={
                'cliente_codigo':'Código de cliente','nombre_fantasia':'Nombre de fantasía',
                'razon_social':'Razón social','promotor':'Promotor','ruta_venta':'Ruta',
                'estado_1890':'Estado 1890','estado_cruce':'Coincidencia con reporte',
            })
            cols_pend=[c for c in ['Código de cliente','Nombre de fantasía','Razón social','Promotor','Ruta',
                                   'Estado 1890','Coincidencia con reporte'] if c in pendientes.columns]
            with cdesc2:
                st.download_button('📥 Descargar solo los que NO compraron',pendientes[cols_pend].to_csv(index=False).encode('utf-8-sig'),
                    file_name=f'1890_p1_p4_pendientes_{nombre_seguro}.csv',mime='text/csv',key='1890_descargar_pendientes')
            with st.expander('Resumen de compra 1890 por promotor'):
                resumen_1890=(detail.groupby(['promotor','estado_1890']).size().unstack(fill_value=0)
                              .reindex(columns=['Compró','No compró'],fill_value=0).reset_index())
                resumen_1890['Total']=resumen_1890['Compró']+resumen_1890['No compró']
                resumen_1890['Cobertura']=resumen_1890['Compró'].div(resumen_1890['Total'].replace(0,pd.NA))
                st.dataframe(resumen_1890,use_container_width=True,hide_index=True)
                st.download_button('Descargar resumen por promotor',resumen_1890.to_csv(index=False).encode('utf-8-sig'),
                                   file_name='1890_resumen_por_promotor.csv',mime='text/csv',key='1890_descargar_resumen')
        else:
            st.error('No se pudo leer REPORTE DE CLIENTES desde Drive: '+reporte_error)
            st.info('La cobertura de 1890 sigue calculada desde las ventas, pero se suspende el filtro por promotor hasta poder verificar la asignación de clientes.')
            with st.expander('Ver listado sin asignación de promotores'):
                st.dataframe(detail,use_container_width=True,hide_index=True)
        with st.expander('Auditoría de combos incluidos y pendientes'):
            st.caption('Un cliente que compró dos combos con el mismo producto cuenta UNA vez por indicador. El producto de un combo puede aportar a múltiples indicadores. La composición incompleta no se supone.')
            st.dataframe(combos,use_container_width=True,hide_index=True)
            st.download_button('Descargar auditoría de combos',combos.to_csv(index=False).encode('utf-8-sig'),file_name='combos_ddv_revision.csv',mime='text/csv')
        if tbd_pendientes.empty:
            st.success('TBD UNG: todos los combos UNG vendidos y reconocidos durante el período seleccionado tienen sus SKU componentes documentados.')
        else:
            st.warning(f'TBD UNG parcial: faltan composiciones SKU de {len(tbd_pendientes)} combos vendidos durante el período seleccionado.')
        st.info('Validaciones comerciales todavía abiertas: Brahma FT se reconoce por nombre/sabor hasta confirmar sus códigos, y los combos de 1890 requieren composición específica si aparecen. La cobertura de otros indicadores no tiene universo oficial definido. Un combo nuevo que aparezca en Drive puede requerir validar su composición en CHESS.')
    else:
        st.caption('Los objetivos se muestran aun cuando Google Drive no esté disponible.')

INDICADORES_PROMOTORES=['h2oh','redbull','pure_gold','mi','cero','core','1890','latones','cervezas','ung']

with tab_promotor:
    st.subheader('CCC y TBD por promotor')
    st.caption('Los 10 KPI del tablero en una sola tabla · CCC = clientes únicos con compra · TBD UNG = pares cliente–SKU únicos. Datos del período elegido, desde Google Drive.')
    if valid_ok:
        matriz=promotor_breakdown(xf, INDICADORES_PROMOTORES, padron)
        altura=max(440,min(990,140+34*(len(matriz)+1)))
        components.html(promotor_table_html(matriz), height=altura, scrolling=True)
        with st.expander('Ver tabla accesible y descargar CSV'):
            st.dataframe(matriz,use_container_width=True,hide_index=True)
        st.download_button('Descargar los 10 KPI por promotor',matriz.to_csv(index=False).encode('utf-8-sig'),file_name='ddv_10_indicadores_por_promotor.csv',mime='text/csv',key='csv_10_promotores')
        st.caption('La fila Totales suma los resultados de los promotores. Puede diferir del Real general cuando un mismo cliente compra con más de un vendedor. Los combos sin composición SKU confirmada no se suman al TBD.')
    else:
        st.info('Sin datos de Drive no se puede construir la vista por promotor.')

with tab_ranking:
    st.subheader('Ranking de promotores')
    st.caption('Ordená a los promotores por cualquiera de los 10 indicadores. El ranking usa los mismos cálculos y período que la tabla por promotor.')
    if valid_ok:
        indicador_rank=st.selectbox('Indicador del ranking',INDICADORES_PROMOTORES,format_func=lambda k:PROMOTOR_LABELS.get(k,NOMBRES.get(k,k)),index=0,key='seleccion_ranking')
        col_indicador=PROMOTOR_LABELS.get(indicador_rank,NOMBRES.get(indicador_rank,indicador_rank))
        seleccion=matriz[['Promotores',col_indicador]].copy() if 'matriz' in locals() else promotor_breakdown(xf,[indicador_rank],padron)
        seleccion=seleccion.loc[~seleccion['Promotores'].isin(['Totales','Sin promotor'])].copy()
        seleccion=seleccion.sort_values([col_indicador,'Promotores'],ascending=[False,True],kind='stable').reset_index(drop=True)
        seleccion.insert(0,'Posición',seleccion[col_indicador].rank(method='min',ascending=False).astype(int))
        seleccion=seleccion.rename(columns={col_indicador:'Resultado'})
        if not seleccion.empty:
            st.dataframe(seleccion,use_container_width=True,hide_index=True,column_config={
                'Posición':st.column_config.NumberColumn('Puesto',format='%d'),
                'Promotores':st.column_config.TextColumn('Promotor'),
                'Resultado':st.column_config.ProgressColumn('Resultado',min_value=0,max_value=max(1,int(seleccion['Resultado'].max())),format='%d'),
            })
            st.download_button('Descargar ranking CSV',seleccion.to_csv(index=False).encode('utf-8-sig'),file_name=f'ddv_ranking_{indicador_rank}.csv',mime='text/csv',key='csv_ranking')
        else:
            st.info('El período no contiene promotores con ventas identificadas.')
        if indicador_rank=='ung' and not detalle_tbd_ung(xf)[1].empty:
            st.warning('TBD UNG es parcial: hay combos vendidos sin desglosar en SKU.')
        st.caption('Los puestos se asignan según resultado descendente: los empates comparten posición. No se aplican objetivos por promotor porque solo tenemos objetivos generales de distribuidora.')
    else:
        st.info('Para armar el ranking es necesario conectar las ventas de Drive.')

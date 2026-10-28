"""Dashboard ejecutivo GTA VI para Rockstar (ADY1104).
Ejecutar:  streamlit run dashboard/app.py   (requiere streamlit, pandas, openpyxl)
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GTA VI · Dashboard para Rockstar", layout="wide")

RUTA = Path(__file__).resolve().parent.parent / "data" / "GTA_VI_Datos_Visualizacion.xlsx"
SENT = ["Positivo", "Neutral", "Negativo"]
# Paleta Vice City: cian (positivo), lila gris (neutral), rosa neón (negativo).
# Cian vs rosa se distingue bien incluso con daltonismo; además cada gráfico lleva etiquetas.
CIAN, LILA, ROSA, APAGADO, TEXTO = "#00E5FF", "#A79BD6", "#FF2D95", "#6D5FB0", "#F6F0FF"
COLOR = alt.Scale(domain=SENT, range=[CIAN, LILA, ROSA])
FOCO = ["Plataformas y rendimiento", "Lanzamiento y espera"]

import html
from urllib.parse import quote

# Palmera (silueta) para el fondo, estilo Vice City
PALMERA = quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='260' height='430' viewBox='0 0 260 430'>"
    "<g fill='#05030F' fill-opacity='0.7'><path d='M118 430C124 300 116 220 138 118L152 120C134 222 142 300 142 430Z'/>"
    "<path d='M146 114Q205 60 255 100Q205 84 146 122Z'/><path d='M146 114Q200 95 240 150Q196 118 146 124Z'/>"
    "<path d='M146 114Q87 60 37 100Q87 84 146 122Z'/><path d='M146 114Q92 95 52 150Q96 118 146 124Z'/>"
    "<path d='M146 114Q128 50 160 18Q160 70 150 118Z'/></g></svg>"
)
CSS = """<style>
    @import url('https://fonts.googleapis.com/css2?family=Bowlby+One&display=swap');
    /* Si añades la tipografía oficial en dashboard/static/ (pricedown.otf), se usa en vez de Bowlby One */
    @font-face {font-family: 'Pricedown';
        src: url('app/static/pricedown.otf') format('opentype'), url('app/static/pricedown.ttf') format('truetype');}
    [data-testid="stAppViewContainer"] {
        background:
            url("data:image/svg+xml,PALMERA_URI") no-repeat right 30px bottom 0 / 230px,
            url("data:image/svg+xml,PALMERA_URI") no-repeat right 240px bottom 0 / 150px,
            linear-gradient(180deg, #090418 0%, #1E0A45 50%, #4A0F6B 78%, #A31F7A 94%, #E8503F 100%);
        background-attachment: fixed;}
    [data-testid="stHeader"] {background: transparent;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #1B0B3A 0%, #0E0A26 100%);
        border-right: 2px solid #FF2D95; box-shadow: 0 0 16px rgba(255, 45, 149, .35);}
    .gta-title {font-family: 'Pricedown', 'Bowlby One', 'Arial Black', Impact, sans-serif; font-weight: 400;
        color: #FF2D95; font-size: 2.4rem; line-height: 1.2; letter-spacing: 1px; margin: .4rem 0 1.2rem;
        text-shadow: 3px 3px 0 #00E5FF, 0 0 22px rgba(255, 45, 149, .55);}
    .gta-title::after {content: ""; display: block; width: 150px; height: 7px; margin-top: 16px; border-radius: 4px;
        background: linear-gradient(90deg, #FF2D95, #00E5FF);}
    [data-testid="stMetricValue"] {color: #00E5FF;}
    [data-testid="stCaptionContainer"] {color: #CDBFF0 !important;}
    </style>"""
st.markdown(CSS.replace("PALMERA_URI", PALMERA), unsafe_allow_html=True)


def titulo(texto):
    st.markdown(f'<div class="gta-title">{html.escape(texto)}</div>', unsafe_allow_html=True)


@st.cache_data
def cargar():
    d = pd.read_excel(RUTA, sheet_name="Datos")
    # Se oculta un nombre de usuario que quedó dentro del texto (anonimización)
    d["comentario"] = d["comentario"].str.replace("calvojackk47:", "usuario:", regex=False)
    return d


df = cargar()
videos = sorted(df.video.unique())
temas = sorted(df.tema_principal.unique())

# ---------- Filtros ----------
st.sidebar.header("Filtros")
OPCIONES = {"f_video": videos, "f_sent": SENT, "f_tema": temas}
for k in OPCIONES:
    st.session_state.setdefault(k, [])  # al abrir, sin selección = se muestran todos


def restablecer():
    for k in OPCIONES:
        st.session_state[k] = []


v = st.sidebar.multiselect("Video", videos, key="f_video", placeholder="Todos")
s = st.sidebar.multiselect("Sentimiento", SENT, key="f_sent", placeholder="Todos")
t = st.sidebar.multiselect("Tema principal", temas, key="f_tema", placeholder="Todos")
st.sidebar.button("Restablecer filtros", on_click=restablecer)
st.sidebar.caption("Sin selección se muestran todos. Elige una o varias opciones para filtrar.")
v, s, t = v or videos, s or SENT, t or temas
st.sidebar.caption(
    "Muestra: 439 comentarios de 3 videos. Etiquetas asistidas, sin validación humana. "
    "No representa a toda la comunidad."
)
f = df[df.video.isin(v) & df.sentimiento.isin(s) & df.tema_principal.isin(t)]
if f.empty:
    st.warning("Los filtros no dejan ningún comentario. Amplía la selección.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["1 · Resumen ejecutivo", "2 · Temas y comparaciones", "3 · Evidencia y calidad"])

# ---------- Vista 1 ----------
with tab1:
    foco = df[df.tema_principal.isin(FOCO)]
    p_com = 100 * len(foco) / len(df)
    p_neg = 100 * (foco.sentimiento == "Negativo").sum() / (df.sentimiento == "Negativo").sum()
    titulo("La preocupación se concentra en plataformas, rendimiento y fecha de lanzamiento")
    st.caption(
        f"Esos dos temas son el {p_com:.0f}% de los comentarios, pero reúnen el {p_neg:.0f}% de los negativos "
        "(muestra completa, sin filtros)."
    )

    n_foco = int(f.tema_principal.isin(FOCO).sum())
    c = st.columns(5)
    c[0].metric("Comentarios", len(f))
    c[1].metric("% positivos", f"{100 * (f.sentimiento == 'Positivo').mean():.1f}%")
    c[2].metric("% negativos", f"{100 * (f.sentimiento == 'Negativo').mean():.1f}%")
    c[3].metric("% preguntas", f"{100 * (f.es_pregunta == 'Sí').mean():.1f}%")
    c[4].metric("Sobre plataformas y fecha", f"{n_foco} ({100 * n_foco / len(f):.0f}%)")

    izq, der = st.columns([3, 2])
    with izq:
        st.subheader("Comparación: % de comentarios negativos por tema")
        g = f.groupby("tema_principal").agg(
            n=("id_registro", "size"), neg=("sentimiento", lambda x: (x == "Negativo").sum())
        ).reset_index()
        g["pct"] = 100 * g.neg / g.n
        g["tema"] = g.tema_principal + " (n=" + g.n.astype(str) + ")"
        g["lbl"] = g.pct.round(0).astype(int).astype(str) + "%"
        base = alt.Chart(g).encode(
            y=alt.Y("tema:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320)),
            x=alt.X("pct:Q", title="% negativos dentro del tema"),
        )
        resaltado = alt.condition(
            alt.FieldOneOfPredicate(field="tema_principal", oneOf=FOCO), alt.value(ROSA), alt.value(APAGADO)
        )
        st.altair_chart(
            base.mark_bar().encode(color=resaltado)
            + base.mark_text(align="left", dx=4, color=TEXTO).encode(text="lbl:N"),
            use_container_width=True,
        )
        st.caption("En rosa, los temas del hallazgo. Temas con n menor a 15 varían mucho: léelos con cautela.")
    with der:
        st.subheader("Composición del sentimiento")
        comp = f.sentimiento.value_counts().reindex(SENT).fillna(0).rename("n").reset_index()
        comp.columns = ["sentimiento", "n"]
        comp["pct"] = 100 * comp.n / comp.n.sum()
        comp["lbl"] = comp.pct.round(1).astype(str) + "%"
        b2 = alt.Chart(comp).encode(
            x=alt.X("sentimiento:N", sort=SENT, title=None),
            y=alt.Y("pct:Q", title="% de comentarios"),
        )
        st.altair_chart(
            b2.mark_bar().encode(color=alt.Color("sentimiento:N", scale=COLOR, legend=None))
            + b2.mark_text(dy=-8, color=TEXTO).encode(text="lbl:N"),
            use_container_width=True,
        )

    st.success(
        "**Decisión para Rockstar:** en la próxima comunicación, aclarar plataformas, rendimiento (fps) "
        "y fecha de lanzamiento antes de seguir reforzando personajes e historia, que ya genera "
        "entusiasmo y cero comentarios negativos.  \n"
        "**Comprobación:** repetir este análisis con los comentarios del siguiente tráiler y revisar si baja "
        "el % de negativos en esos dos temas."
    )
    st.warning(
        "**Alcance y límites:** son reacciones a 3 videos, no experiencia de juego. El sentimiento y el tema son "
        "propuestas asistidas (palabras clave) sin validación humana. No se pueden hacer afirmaciones causales ni "
        "generalizar a todos los jugadores."
    )

# ---------- Vista 2 ----------
with tab2:
    titulo("¿Dónde se origina la señal?")
    n_v = f.video.value_counts()
    pv = pd.crosstab(f.video, f.sentimiento).reindex(columns=SENT, fill_value=0)
    pp = pv.div(pv.sum(axis=1), axis=0).mul(100).round(1)
    pp.index = [f"{i} (n={n_v[i]})" for i in pp.index]
    st.subheader("Sentimiento por video (% dentro de cada video)")
    lg = pp.reset_index(names="video").melt("video", var_name="sentimiento", value_name="pct")
    st.altair_chart(
        alt.Chart(lg).mark_bar().encode(
            y=alt.Y("video:N", title=None),
            x=alt.X("pct:Q", title="% de comentarios", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("sentimiento:N", scale=COLOR, sort=SENT),
            order=alt.Order("sentimiento:N"),
            tooltip=["video", "sentimiento", "pct"],
        ),
        use_container_width=True,
    )
    st.dataframe(pp, use_container_width=True)
    st.caption("Los tres videos tienen un perfil casi idéntico: la diferencia está en los temas, no en el sentimiento.")

    st.subheader("Temas principales (n° de comentarios)")
    ct = f.tema_principal.value_counts().rename("n").reset_index()
    ct.columns = ["tema", "n"]
    b3 = alt.Chart(ct).encode(
        y=alt.Y("tema:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320)),
        x=alt.X("n:Q", title="Comentarios"),
    )
    st.altair_chart(
        b3.mark_bar(color="#B66DFF") + b3.mark_text(align="left", dx=4, color=TEXTO).encode(text="n:Q"),
        use_container_width=True,
    )
    st.subheader("Tema × video (n° de comentarios)")
    st.dataframe(pd.crosstab(f.tema_principal, f.video), use_container_width=True)
    st.caption("'Tráiler y comunicación' proviene sobre todo del Video 1 y casi no tiene negativos: no es una señal de queja.")

# ---------- Vista 3 ----------
with tab3:
    titulo("Evidencia y calidad: ¿qué sostiene la lectura?")
    q = st.columns(3)
    q[0].metric("Sin validación humana", f"{(f.estado_revision.str.contains('sin validación')).sum()} de {len(f)}")
    q[1].metric("Posibles señales mixtas", int((f.posible_mixto == "Sí").sum()))
    corto = f[f.extension == "Corto"]
    q[2].metric("Neutrales entre comentarios cortos", f"{100 * (corto.sentimiento == 'Neutral').mean():.0f}%" if len(corto) else "—")

    busca = st.text_input("Buscar en los comentarios (por ejemplo: fps, retraso, PC)")
    ev = f if not busca else f[f.comentario.str.contains(busca, case=False, regex=False)]
    st.caption(f"{len(ev)} comentarios. Usa id_registro para rastrear cada cita hasta el dataset.")
    st.dataframe(
        ev[["id_registro", "video", "sentimiento", "tema_principal", "es_pregunta", "comentario"]],
        use_container_width=True, hide_index=True,
    )
    st.subheader("Limitaciones")
    st.markdown(
        "- Etiquetas de sentimiento y tema asistidas por reglas de palabras clave, sin validación humana.\n"
        "- Algunos retrasos de lanzamiento quedaron en 'Otros temas': la regla de temas no los detecta todos.\n"
        "- Casi no hay señales mixtas (1 caso), por lo que no se grafican.\n"
        "- Son videos de reacción de creadores: parte de los comentarios habla del creador y no de GTA VI.\n"
        "- Video 2 tiene solo 52 comentarios y varios temas tienen 9 o menos.\n"
        "- No hay fecha por comentario: no se puede analizar evolución en el tiempo."
    )

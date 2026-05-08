# IMPORTACION DE LIBRERIAS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# CONFIGURACION DE PAGINA
st.set_page_config(
    page_title="Superstore | Análisis de Rentabilidad",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# PALETA DE COLORES CORPORATIVA
# Verde = ganancia / Rojo = perdida / Naranja = alerta
COLOR_GANANCIA = "#2ECC71"
COLOR_PERDIDA  = "#E74C3C"
COLOR_NEUTRO   = "#2C3E50"
COLOR_ACENTO   = "#F39C12"
COLOR_FONDO    = "#F4F6F9"
PALETTE_CAT    = ["#2ECC71", "#F39C12", "#E74C3C"]
PALETTE_SEQ    = ["#27AE60", "#F1C40F", "#E67E22", "#E74C3C", "#C0392B"]


# CSS PERSONALIZADO
st.markdown("""
            <style>
                [data-testid="stAppViewContainer"] { background-color: #F4F6F9 !important; }
                .main .block-container { background-color: #F4F6F9 !important; }
                .main * { color: #2C3E50 !important; }
                p, span, div, label { color: #2C3E50 !important; }
                [data-testid="stSidebar"] { background-color: #2C3E50 !important; }
                [data-testid="stSidebar"] * { color: #ECF0F1 !important; }
                [data-testid="stSidebar"] .stMultiSelect span { color: #2C3E50 !important; }
                h1, h2, h3, h4, h5 { color: #2C3E50 !important; }
                div[data-testid="metric-container"] {
                    background-color: white !important;
                    border-radius: 12px !important;
                    padding: 16px 20px !important;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
                }
                div[data-testid="metric-container"] * { color: #2C3E50 !important; }
                div[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #2ECC71 !important; }
                div[data-testid="stAlert"] { background-color: #EBF5FB !important; }
                div[data-testid="stAlert"] * { color: #2C3E50 !important; }
                .section-title {
                    font-size: 22px !important;
                    font-weight: 700 !important;
                    color: #2C3E50 !important;
                    border-bottom: 3px solid #E74C3C !important;
                    padding-bottom: 6px !important;
                    margin: 32px 0 16px 0 !important;
                }
            </style>
""", unsafe_allow_html=True)



# CARGA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv", encoding="latin-1")
    df["Order Date"]   = pd.to_datetime(df["Order Date"])
    df["Profit_Ratio"] = df["Profit"] / df["Sales"]
    df["Resultado"]    = df["Profit"].apply(lambda x: "Pérdida" if x < 0 else "Ganancia")
    df["Año"]          = df["Order Date"].dt.year
    df["Discount_Pct"] = (df["Discount"] * 100).round(0).astype(int).astype(str) + "%"
    return df

df = load_data()


# SIDEBAR — FILTROS GLOBALES
with st.sidebar:
    st.markdown("## 🎛️ Filtros")
    st.markdown("---")

    regiones = st.multiselect(
        "📍 Región",
        options=sorted(df["Region"].unique()),
        default=sorted(df["Region"].unique())
    )

    categorias = st.multiselect(
        "📦 Categoría",
        options=sorted(df["Category"].unique()),
        default=sorted(df["Category"].unique())
    )

    segmentos = st.multiselect(
        "👥 Segmento de cliente",
        options=sorted(df["Segment"].unique()),
        default=sorted(df["Segment"].unique())
    )

    descuento_max = st.slider(
        "🏷️ Descuento máximo (%)",
        min_value=0, max_value=80,
        value=80, step=10
    )

    años = st.multiselect(
        "📅 Año",
        options=sorted(df["Año"].unique()),
        default=sorted(df["Año"].unique())
    )

    st.markdown("---")
    st.markdown("**📌 Proyecto Final**")
    st.markdown("Herramientas y Visualización")

# Aplicar filtros
mask = (
    df["Region"].isin(regiones) &
    df["Category"].isin(categorias) &
    df["Segment"].isin(segmentos) &
    (df["Discount"] <= descuento_max / 100) &
    df["Año"].isin(años)
)
dff = df[mask]


# ADVERTENCIA SI NO HAY DATOS
if dff.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados. Ajusta los filtros del sidebar.")
    st.stop()



# ENCABEZADO
st.markdown("""
            <h1 style='text-align:center; color:#2C3E50; margin-bottom:4px;'>
                📊 Análisis de Rentabilidad — Superstore Giant
            </h1>
            <p style='text-align:center; color:#7F8C8D; font-size:16px; margin-bottom:32px;'>
                ¿En qué áreas y productos la estrategia de descuentos está comprometiendo la rentabilidad?
            </p>
""", unsafe_allow_html=True)

# Dato clave calculado dinamicamente con los filtros activos
alto_desc = dff[dff["Discount"] > 0.2]
pct_perdida_alto_desc = (alto_desc["Profit"] < 0).mean() * 100 if len(alto_desc) > 0 else 0

st.info(f"💡 **Hallazgo clave:** El **{pct_perdida_alto_desc:.1f}%** de las ventas con descuento mayor al 20% "
        f"generan pérdida operativa. Tables y Bookcases venden mucho, pero destruyen valor. "
        f"Usa los filtros para explorar el impacto por región, categoría y segmento de cliente.")


# KPIs
k1, k2, k3, k4, k5, k6 = st.columns(6)

total_sales  = dff["Sales"].sum()
total_profit = dff["Profit"].sum()
profit_ratio = dff["Profit_Ratio"].mean() * 100
pct_perdidas = (dff["Profit"] < 0).mean() * 100
avg_discount = dff["Discount"].mean() * 100
total_orders = dff["Order ID"].nunique()

k1.metric("💰 Ventas Totales", f"${total_sales:,.0f}")
k2.metric("📈 Utilidad Total", f"${total_profit:,.0f}",
          delta=f"{'+' if total_profit > 0 else ''}{total_profit:,.0f}")
k3.metric("📊 Margen Promedio", f"{profit_ratio:.1f}%")
k4.metric("⚠️ Ventas en Pérdida", f"{pct_perdidas:.1f}%")
k5.metric("🏷️ Descuento Promedio", f"{avg_discount:.1f}%")
k6.metric("📦 Órdenes Totales", f"{total_orders:,}")

st.markdown("<br>", unsafe_allow_html=True)


# SECCION 1 — DESCUENTO DESTRUYE UTILIDAD
st.markdown('<p class="section-title">🔻 Los descuentos altos generan pérdidas directas</p>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    # GRAFICO 1 — Scatter Discount vs Profit
    fig1 = px.scatter(
        dff, x="Discount", y="Profit",
        color="Category",
        color_discrete_sequence=PALETTE_CAT,
        opacity=0.55,
        size_max=8,
        title="A partir del 20% de descuento, la mayoría de ventas generan pérdidas",
        labels={"Discount": "Descuento aplicado", "Profit": "Utilidad (USD)", "Category": "Categoría"},
        hover_data=["Sub-Category", "Sales", "Segment"]
    )
    fig1.add_vline(x=0.2, line_dash="dash", line_color=COLOR_ACENTO,
                   annotation_text="Umbral crítico: 20%", annotation_position="top right",
                   annotation_font_color=COLOR_ACENTO)
    fig1.add_hline(y=0, line_color=COLOR_PERDIDA, line_width=1.5)
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # GRAFICO 2 — Profit promedio por nivel de descuento
    disc_profit = dff.groupby("Discount")["Profit"].mean().reset_index()
    disc_profit["color"] = disc_profit["Profit"].apply(
        lambda x: COLOR_PERDIDA if x < 0 else COLOR_GANANCIA)
    disc_profit["Discount_Label"] = (disc_profit["Discount"] * 100).astype(int).astype(str) + "%"

    fig2 = go.Figure(go.Bar(
        x=disc_profit["Discount_Label"],
        y=disc_profit["Profit"],
        marker_color=disc_profit["color"],
        text=disc_profit["Profit"].round(0),
        texttemplate="%{text:,.0f}",
        textposition="outside"
    ))
    fig2.update_layout(
        title="Con descuentos ≥ 30%, el margen promedio es negativo",
        xaxis_title="Nivel de Descuento",
        yaxis_title="Utilidad Promedio (USD)",
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        showlegend=False
    )
    fig2.add_hline(y=0, line_color=COLOR_NEUTRO, line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown(f"""
            <div style='background:#FDECEA; border-left:4px solid #E74C3C; padding:12px 16px; border-radius:6px; margin-bottom:8px;'>
            📌 <b>Conclusión:</b> Existe una correlación negativa entre descuento y utilidad (-0.22).
            El <b>{pct_perdida_alto_desc:.1f}%</b> de las ventas con descuento mayor al 20% terminan en pérdida.
            Los descuentos superiores al 20% convierten transacciones rentables en pérdidas operativas,
            especialmente en la categoría <b>Furniture</b>.
            </div>
""", unsafe_allow_html=True)


# SECCION 2 — CATEGORIAS Y SUBCATEGORIAS
st.markdown('<p class="section-title">📦 Furniture vende mucho, pero pierde dinero</p>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    # GRAFICO 3 — Bar horizontal: Profit por Sub-Category
    subcat = dff.groupby("Sub-Category")["Profit"].sum().reset_index().sort_values("Profit")
    subcat["color"] = subcat["Profit"].apply(
        lambda x: COLOR_PERDIDA if x < 0 else COLOR_GANANCIA)

    fig3 = go.Figure(go.Bar(
        x=subcat["Profit"],
        y=subcat["Sub-Category"],
        orientation="h",
        marker_color=subcat["color"],
        text=subcat["Profit"].round(0),
        texttemplate="%{text:,.0f}",
        textposition="outside"
    ))

    fig3.update_layout(
        title="Tables y Bookcases son los principales destructores de valor",
        xaxis_title="Utilidad Total (USD)",
        yaxis_title="",
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        height=450
    )

    fig3.add_vline(x=0, line_color=COLOR_NEUTRO, line_width=1.5)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # GRAFICO 4 — Treemap Sales vs Profit
    treemap_df = dff.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    treemap_df["Profit_Ratio"] = (treemap_df["Profit"] / treemap_df["Sales"] * 100).round(1)

    fig4 = px.treemap(
        treemap_df,
        path=[px.Constant("Superstore"), "Category", "Sub-Category"],
        values="Sales",
        color="Profit",
        color_continuous_scale=["#E74C3C", "#F39C12", "#2ECC71"],
        color_continuous_midpoint=0,
        title="Subcategorías con mayor venta no siempre son las más rentables",
        hover_data={"Profit": ":,.0f", "Profit_Ratio": ":.1f"}
    )

    fig4.update_layout(
        paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        coloraxis_colorbar=dict(title="Utilidad $")
    )

    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
            <div style='background:#EAF9F0; border-left:4px solid #2ECC71; padding:12px 16px; border-radius:6px; margin-bottom:8px;'>
            📌 <b>Conclusión:</b> Technology y Office Supplies son las categorías más rentables.
            Furniture concentra el mayor riesgo: <b>Tables genera pérdidas de más de $17,000</b>
            a pesar de su alto volumen de ventas. El tamaño no garantiza rentabilidad.
            </div>
""", unsafe_allow_html=True)


# SECCION 3 — ANALISIS GEOGRAFICO
st.markdown('<p class="section-title">🗺️ Texas y Ohio concentran las mayores pérdidas del país</p>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    # GRAFICO 5 — Heatmap Region × Categoria
    heat_df = dff.groupby(["Region", "Category"])["Profit"].sum().reset_index()
    heat_pivot = heat_df.pivot(index="Category", columns="Region", values="Profit")

    fig5 = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0, "#E74C3C"], [0.5, "#F8F9FA"], [1, "#2ECC71"]],
        zmid=0,
        text=[[f"${v:,.0f}" for v in row] for row in heat_pivot.values],
        texttemplate="%{text}",
        showscale=True,
        colorbar=dict(title="Utilidad $")
    ))

    fig5.update_layout(
        title="Furniture pierde dinero en todas las regiones excepto South",
        xaxis_title="Región",
        yaxis_title="Categoría",
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO
    )

    st.plotly_chart(fig5, use_container_width=True)

with col6:
    # GRAFICO 6 — Top estados con mas perdidas y mas ganancias
    state_profit = dff.groupby("State")["Profit"].sum().reset_index().sort_values("Profit")
    top_bottom = pd.concat([state_profit.head(7), state_profit.tail(5)]).drop_duplicates()
    top_bottom["color"] = top_bottom["Profit"].apply(
        lambda x: COLOR_PERDIDA if x < 0 else COLOR_GANANCIA)

    fig6 = go.Figure(go.Bar(
        x=top_bottom["Profit"],
        y=top_bottom["State"],
        orientation="h",
        marker_color=top_bottom["color"],
        text=top_bottom["Profit"].round(0),
        texttemplate="%{text:,.0f}",
        textposition="outside"
    ))

    fig6.update_layout(
        title="Texas y Ohio destruyen más utilidad que cualquier otro estado",
        xaxis_title="Utilidad Total (USD)",
        yaxis_title="",
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        height=420
    )

    fig6.add_vline(x=0, line_color=COLOR_NEUTRO, line_width=1.5)
    
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("""
            <div style='background:#FEF9E7; border-left:4px solid #F39C12; padding:12px 16px; border-radius:6px; margin-bottom:8px;'>
            📌 <b>Conclusión:</b> La región Central es la más problemática, liderada por Texas (-$25,729) y Ohio (-$16,971).
            Furniture pierde dinero en casi todas las regiones del país.
            Office Supplies mantiene rentabilidad consistente en todos los territorios.
            </div>
""", unsafe_allow_html=True)


# SECCION 4 — ANALISIS POR SEGMENTO
st.markdown('<p class="section-title">👥 El segmento Consumer concentra el mayor volumen de pérdidas</p>', unsafe_allow_html=True)

col7, col8 = st.columns(2)

with col7:
    # GRAFICO 7 — Boxplot descuentos por categoria
    fig7 = px.box(
        dff, x="Category", y="Discount",
        color="Category",
        color_discrete_sequence=PALETTE_CAT,
        title="Furniture recibe los descuentos más agresivos y variables",
        labels={"Discount": "Descuento aplicado", "Category": "Categoría"},
        points="outliers"
    )

    fig7.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        showlegend=False,
        yaxis_tickformat=".0%"
    )

    st.plotly_chart(fig7, use_container_width=True)

with col8:
    # GRAFICO 8 — Profit por Segmento y Categoria
    seg_cat = dff.groupby(["Segment", "Category"])["Profit"].sum().reset_index()

    fig8 = px.bar(
        seg_cat, x="Segment", y="Profit",
        color="Category",
        barmode="group",
        color_discrete_sequence=PALETTE_CAT,
        title="Consumer lidera pérdidas en Furniture en todos los segmentos",
        labels={"Profit": "Utilidad (USD)", "Segment": "Segmento", "Category": "Categoría"}
    )

    fig8.add_hline(y=0, line_color=COLOR_NEUTRO, line_width=1)
    
    fig8.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("""
            <div style='background:#EAF9F0; border-left:4px solid #2ECC71; padding:12px 16px; border-radius:6px; margin-bottom:8px;'>
            📌 <b>Conclusión:</b> El segmento Consumer es el más grande pero también el más expuesto a pérdidas en Furniture.
            Corporate y Home Office muestran mejores márgenes relativos, lo que sugiere que la política de descuentos
            agresivos está concentrada en el canal de consumo masivo.
            </div>
""", unsafe_allow_html=True)


# SECCION 5 — TENDENCIA TEMPORAL
st.markdown('<p class="section-title">📅 Las ventas crecen, pero la utilidad de Furniture no mejora</p>', unsafe_allow_html=True)

time_df = dff.groupby(["Año", "Category"]).agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).reset_index()

col9, col10 = st.columns(2)

with col9:
    fig9 = px.line(
        time_df, x="Año", y="Sales",
        color="Category",
        markers=True,
        color_discrete_sequence=PALETTE_CAT,
        title="El crecimiento en ventas de Furniture no se traduce en ganancias",
        labels={"Sales": "Ventas (USD)", "Año": "Año", "Category": "Categoría"}
    )
    
    fig9.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig9, use_container_width=True)

with col10:
    fig10 = px.line(
        time_df, x="Año", y="Profit",
        color="Category",
        markers=True,
        color_discrete_sequence=PALETTE_CAT,
        title="La utilidad de Technology crece consistentemente año a año",
        labels={"Profit": "Utilidad (USD)", "Año": "Año", "Category": "Categoría"}
    )
    
    fig10.add_hline(y=0, line_dash="dot", line_color=COLOR_PERDIDA)
    
    fig10.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_color=COLOR_NEUTRO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig10, use_container_width=True)

st.markdown("""
            <div style='background:#FDECEA; border-left:4px solid #E74C3C; padding:12px 16px; border-radius:6px; margin-bottom:8px;'>
            📌 <b>Conclusión:</b> Technology muestra crecimiento sostenido en utilidad año tras año.
            Furniture crece en ventas pero su utilidad permanece estancada cerca de cero,
            confirmando que el problema no es de demanda sino de estructura de precios y descuentos.
            </div>
""", unsafe_allow_html=True)


# CONCLUSIONES ESTRATEGICAS FINALES
st.markdown('<p class="section-title">🎯 Recomendaciones Estratégicas para la Gerencia</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
                <div style='background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #E74C3C;'>
                <h4 style='color:#E74C3C;'>🚫 Eliminar descuentos &gt; 20% en Furniture</h4>
                <p style='color:#555; font-size:14px;'>Tables y Bookcases generan pérdidas netas con descuentos altos.
                Limitar los descuentos al 15% podría recuperar más de $17,000 en utilidad perdida anualmente.</p>
                </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
                <div style='background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #F39C12;'>
                <h4 style='color:#F39C12;'>⚠️ Auditar operaciones en Texas y Ohio</h4>
                <p style='color:#555; font-size:14px;'>Estos dos estados concentran más de $40,000 en pérdidas acumuladas.
                Se recomienda revisar las políticas de descuento locales y renegociar condiciones con distribuidores.</p>
                </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
                <div style='background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #2ECC71;'>
                <h4 style='color:#2ECC71;'>✅ Potenciar Technology y Office Supplies</h4>
                <p style='color:#555; font-size:14px;'>Estas categorías tienen márgenes positivos y crecientes.
                Redirigir el presupuesto de marketing hacia estos productos maximizaría la rentabilidad total.</p>
                </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
            <div style='text-align:center; color:#BDC3C7; font-size:13px; padding:16px;'>
            Proyecto Final — Herramientas y Visualización | Superstore Giant Dashboard
            </div>
""", unsafe_allow_html=True)
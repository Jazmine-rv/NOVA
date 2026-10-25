import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Tablero de ausentismo · Salud Nova",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS FORZADO · PALETA WCAG 2.1 AA
# Azul marino #0B2545 textos · Azul #1D4E89 acento
# Gris #6B7280 contexto · Naranja #B54708 alertas
# Blanco roto #FAF8F3 fondo · Bloque #EDF1F6 secciones
# ============================================================
st.markdown("""
<style>
    /* Fondo blanco roto #FAF8F3 */
    .stApp {
        background-color: #FAF8F3;
    }
    /* Texto azul marino #0B2545 en títulos y párrafos */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stCaption {
        color: #0B2545 !important;
    }
    /* Bloque gris azulado #EDF1F6 para las secciones */
    .bloque-seccion {
        background-color: #EDF1F6;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    /* Métricas: fondo blanco, borde gris, texto azul marino */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #C5CCD6;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] {
        color: #4B5563 !important;
    }
    [data-testid="stMetricValue"] {
        color: #0B2545 !important;
    }
    /* Sidebar: fondo blanco y texto azul marino */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] * {
        color: #0B2545 !important;
    }
    /* Forzar modo claro (evita que el tema oscuro rompa el contraste) */
    :root {
        color-scheme: light;
    }
    /* Enlaces y botones con azul de acento #1D4E89 */
    a, .stButton>button {
        color: #1D4E89 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS SIMULADOS
# ============================================================
ESPECIALIDADES = ["Cardiología", "Neurología", "Traumatología", "Clínica médica", "Pediatría"]
ST = [34.0, 32.0, 28.0, 24.0, 22.0]      # histórico
EN = [29.0, 27.0, 24.0, 20.0, 17.5]       # semana 12
OV = [28.0, 27.4, 26.8, 26.2, 25.6, 25.0, 24.6, 24.3, 24.0, 23.8, 23.6, 23.5]
SOB = [5, 4, 2, 2, 1]
WT = [[45, 39], [47, 41], [46, 41], [20, 18], [15, 14]]
TURNOS = [
    [0, "T-49012", "Vie 23/10 · 11:00", 88],
    [0, "T-48213", "Lun 19/10 · 09:00", 86],
    [0, "T-48811", "Mié 21/10 · 10:30", 83],
    [1, "T-48377", "Lun 19/10 · 10:30", 81],
    [1, "T-48852", "Jue 22/10 · 08:00", 79],
    [0, "T-48402", "Lun 19/10 · 11:15", 78],
    [2, "T-48977", "Vie 23/10 · 08:45", 77],
    [3, "T-48901", "Jue 22/10 · 09:15", 75],
    [2, "T-48519", "Mar 20/10 · 08:30", 74],
    [1, "T-48934", "Jue 22/10 · 16:30", 73],
    [1, "T-48633", "Mar 20/10 · 15:00", 72],
    [3, "T-49044", "Vie 23/10 · 12:15", 72],
    [0, "T-48790", "Mié 21/10 · 09:45", 71],
    [4, "T-49090", "Vie 23/10 · 15:30", 71],
]

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def serie_especialidad(idx):
    factor = [(v - 23.5) / 4.5 for v in OV]
    return [EN[idx] + (ST[idx] - EN[idx]) * f for f in factor]

def formato_pct(n):
    return f"{n:.1f} %".replace(".", ",")

def formato_dinero(n):
    return f"$ {n:.2f} M".replace(".", ",")

# ============================================================
# SIDEBAR · FILTROS
# ============================================================
st.sidebar.header("⚙️ Filtros")
periodo = st.sidebar.selectbox(
    "Período",
    options=[12, 8, 4],
    format_func=lambda x: f"Últimas {x} semanas",
    index=0
)
especialidad_sel = st.sidebar.selectbox(
    "Especialidad",
    options=["Todas"] + ESPECIALIDADES,
    index=0
)
idx_esp = -1 if especialidad_sel == "Todas" else ESPECIALIDADES.index(especialidad_sel)

# ============================================================
# TÍTULO
# ============================================================
st.title("🏥 Tablero de ausentismo · Salud Nova")
st.caption(
    "Prototipo con datos simulados: ausentismo histórico de 28 % y "
    "$ 18,5 M ARS mensuales de capacidad ociosa."
)

# ============================================================
# NIVEL 1 · VISIÓN GENERAL (4 KPIs) — bloque #EDF1F6
# ============================================================
st.markdown('<div class="bloque-seccion">', unsafe_allow_html=True)
st.header("Nivel 1 · Visión general")

if idx_esp < 0:
    no_show_actual = OV[-1]
    no_show_base = 28.0
else:
    no_show_actual = EN[idx_esp]
    no_show_base = ST[idx_esp]

total_rescatado = 18.5 * (28 - OV[-1]) / 28
if idx_esp < 0:
    dinero_rescatado = total_rescatado
else:
    dinero_rescatado = total_rescatado * (ST[idx_esp] - EN[idx_esp]) / 22.5

sobreturnos_hoy = 14 if idx_esp < 0 else SOB[idx_esp]
espera = WT[0] if idx_esp < 0 else WT[idx_esp]
nombre_esp = "Todas las especialidades" if idx_esp < 0 else ESPECIALIDADES[idx_esp]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Tasa de No-Show (semana 12)",
        value=formato_pct(no_show_actual),
        delta=f"-{no_show_base - no_show_actual:.1f} pp vs. {no_show_base:.0f} % histórico".replace(".", ","),
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Dinero rescatado (mes)",
        value=formato_dinero(dinero_rescatado),
        delta="de $ 18,5 M ARS en juego" if idx_esp < 0 else f"parte de los $ {total_rescatado:.2f} M totales".replace(".", ","),
        delta_color="off"
    )

with col3:
    st.metric(
        label="Sobreturnos preventivos hoy",
        value=str(sobreturnos_hoy),
        delta="en turnos de riesgo alto (> 70 %)",
        delta_color="off"
    )

with col4:
    st.metric(
        label=f"Espera media en {nombre_esp if idx_esp >= 0 else 'Cardiología'}",
        value=f"{espera[1]} días",
        delta=f"-{espera[0] - espera[1]} días vs. {espera[0]} días previos",
        delta_color="inverse"
    )
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# NIVEL 2 · CONTEXTO Y COMPARACIÓN — bloque #EDF1F6
# ============================================================
st.markdown('<div class="bloque-seccion">', unsafe_allow_html=True)
st.header("Nivel 2 · Contexto y comparación")

col_graf1, col_graf2 = st.columns(2)

# --- Gráfico de líneas (tendencia) ---
with col_graf1:
    serie = OV[-periodo:] if idx_esp < 0 else serie_especialidad(idx_esp)[-periodo:]
    semanas = list(range(12 - periodo + 1, 13))
    base = 28.0 if idx_esp < 0 else ST[idx_esp]
    nombre = "Todas las especialidades" if idx_esp < 0 else ESPECIALIDADES[idx_esp]

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=semanas, y=serie,
        mode="lines+markers",
        line=dict(color="#1D4E89", width=3),
        marker=dict(size=8, color="#1D4E89"),
        name=nombre,
        hovertemplate="Semana %{x}: %{y:.1f} %<extra></extra>"
    ))
    fig_line.add_hline(
        y=base, line_dash="dash", line_color="#6B7280",
        annotation_text=f"Histórico {base:.0f} %",
        annotation_position="top right",
        annotation_font_color="#0B2545"
    )
    fig_line.update_layout(
        title=dict(text=f"Evolución del No-Show en {nombre}", font=dict(color="#0B2545")),
        xaxis_title="Semana",
        yaxis_title="Tasa de No-Show (%)",
        yaxis_range=[min(serie) - 2, base + 2],
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#FAF8F3",
        paper_bgcolor="#FAF8F3",
        font=dict(color="#0B2545"),
        xaxis=dict(tickfont=dict(color="#0B2545"), title_font=dict(color="#0B2545")),
        yaxis=dict(tickfont=dict(color="#0B2545"), title_font=dict(color="#0B2545")),
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- Gráfico de barras (por especialidad) ---
with col_graf2:
    df_barras = pd.DataFrame({
        "Especialidad": ESPECIALIDADES,
        "No-Show (%)": EN
    }).sort_values("No-Show (%)", ascending=True)

    colores = ["#B54708" if v > 25 else "#6B7280" for v in df_barras["No-Show (%)"]]

    fig_bar = go.Figure(go.Bar(
        x=df_barras["No-Show (%)"],
        y=df_barras["Especialidad"],
        orientation="h",
        marker_color=colores,
        text=[f"{v:.1f} %".replace(".", ",") for v in df_barras["No-Show (%)"]],
        textposition="outside",
        textfont=dict(color="#0B2545"),
        hovertemplate="%{y}: %{x:.1f} %<extra></extra>"
    ))
    fig_bar.update_layout(
        title=dict(text="No-Show por especialidad (semana 12)", font=dict(color="#0B2545")),
        xaxis_title="Tasa de No-Show (%)",
        xaxis_range=[0, 36],
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#FAF8F3",
        paper_bgcolor="#FAF8F3",
        font=dict(color="#0B2545"),
        xaxis=dict(tickfont=dict(color="#0B2545"), title_font=dict(color="#0B2545")),
        yaxis=dict(tickfont=dict(color="#0B2545"), title_font=dict(color="#0B2545")),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.info(
    "💡 **Lectura:** Cardiología y Neurología siguen con el mayor ausentismo "
    "(más de 25 %): prioricemos allí los sobreturnos preventivos."
)

# --- Tabla de datos (equivalente al <details> del HTML) ---
with st.expander("📊 Ver los datos de los gráficos en una tabla"):
    df_tabla = pd.DataFrame({"Semana": list(range(1, 13)), "Todas": OV})
    for i, esp in enumerate(ESPECIALIDADES):
        df_tabla[esp] = serie_especialidad(i)
    st.dataframe(
        df_tabla.style.format("{:.1f}"),
        use_container_width=True,
        hide_index=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# NIVEL 3 · DETALLE A DEMANDA (drill-down) — bloque #EDF1F6
# ============================================================
st.markdown('<div class="bloque-seccion">', unsafe_allow_html=True)
st.header("Nivel 3 · Detalle a demanda")

turnos_filtrados = TURNOS if idx_esp < 0 else [t for t in TURNOS if t[0] == idx_esp]

if len(turnos_filtrados) == 0:
    st.warning("No hay turnos de riesgo alto para esta especialidad.")
else:
    with st.expander(f"🔴 Ver los {len(turnos_filtrados)} turnos de riesgo alto (> 70 %) de esta semana"):
        df_turnos = pd.DataFrame([
            {
                "ID de turno": t[1],
                "Especialidad": ESPECIALIDADES[t[0]],
                "Fecha y hora": t[2],
                "Riesgo": f"▲ {t[3]} % · Alto",
                "Acción sugerida": "Llamada de Recepción y sugerir sobreturno" if t[3] >= 75 else "Llamada de confirmación"
            }
            for t in turnos_filtrados
        ])
        st.dataframe(df_turnos, use_container_width=True, hide_index=True)
        st.caption(
            "Solo ID anónimo: sin nombre ni diagnóstico del paciente. "
            "Datos simulados para el prototipo."
        )
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PIE DE PÁGINA
# ============================================================
st.divider()
st.caption(
    "TIF · Taller de Comunicación · Salud Nova · Prototipo con datos simulados. "
    "Accesibilidad: contraste AA (4.5:1 texto, 3:1 gráficos), codificación por color + texto "
    "(apto para daltonismo), modo claro forzado."
)

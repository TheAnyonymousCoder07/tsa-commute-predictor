import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="TSA 2026 | Commute Predictor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
def inject_styles():
    st.html("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
body, .stApp {
    background-color: #020409 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 0.5rem !important; max-width: 1200px !important; }
section[data-testid="stSidebar"] { display: none !important; }

.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

.stButton > button {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 0.65rem !important;
    background: transparent !important;
    color: #00ff41 !important;
    border: 2px solid #00ff41 !important;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    padding: 0.75rem 2rem !important;
    transition: all 0.2s !important;
    border-radius: 0 !important;
    width: 100%;
}
.stButton > button:hover {
    background: #00ff41 !important;
    color: #020409 !important;
    box-shadow: 0 0 20px #00ff41 !important;
}

div[data-baseweb="select"] > div {
    background: #0a0f1e !important;
    border: 1px solid #00ff41 !important;
    color: #00ff41 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 0 !important;
}
div[data-baseweb="popover"] {
    background: #0a0f1e !important;
}
li[role="option"] {
    background: #0a0f1e !important;
    color: #00ff41 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
    background: #1a2040 !important;
}

.game-card {
    background: #0a0f1e;
    border: 1px solid #1a2040;
    border-top: 2px solid transparent;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: border-top-color 0.2s;
}
.game-card:hover { border-top-color: #00ff41; }

.hp-track {
    background: #1a2040;
    height: 8px;
    border-radius: 2px;
    overflow: hidden;
    margin: 0.4rem 0;
}
.hp-fill { height: 100%; border-radius: 2px; }
.hp-fill.green  { background: linear-gradient(90deg, #00ff41, #00cc33); box-shadow: 0 0 6px #00ff41; }
.hp-fill.cyan   { background: linear-gradient(90deg, #00e5ff, #0099cc); box-shadow: 0 0 6px #00e5ff; }
.hp-fill.yellow { background: linear-gradient(90deg, #ffe600, #cc9900); box-shadow: 0 0 6px #ffe600; }
.hp-fill.pink   { background: linear-gradient(90deg, #ff00aa, #cc0077); box-shadow: 0 0 6px #ff00aa; }
.hp-fill.orange { background: linear-gradient(90deg, #ff6b00, #cc4400); box-shadow: 0 0 6px #ff6b00; }

.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00ff41, transparent);
    margin: 2rem 0;
}
.result-card {
    background: #0a0f1e;
    border: 2px solid #00ff41;
    padding: 1.5rem;
    box-shadow: 0 0 30px rgba(0,255,65,0.15);
}
</style>
""")

# ─── STATIC DATA ──────────────────────────────────────────────────────────────
COLORS = {
    "Drive Alone":    "#00e5ff",
    "Carpool":        "#ffe600",
    "Public Transit": "#ff00aa",
    "Work From Home": "#00ff41",
}
MODE_ICONS = {
    "Drive Alone": "🚗",
    "Carpool": "🚌",
    "Public Transit": "🚇",
    "Work From Home": "🏠",
}
CHART_DATA = {
    "Drive Alone":    {"workers": 112_376_082, "median_earnings": 48_372, "commute_min": 26.1,  "pct_no_vehicle": 1.7,  "pct_mgmt": 40.6},
    "Carpool":        {"workers": 14_609_627,  "median_earnings": 36_479, "commute_min": 27.2,  "pct_no_vehicle": 5.0,  "pct_mgmt": 32.5},
    "Public Transit": {"workers": 5_735_258,   "median_earnings": 46_903, "commute_min": 48.9,  "pct_no_vehicle": 39.4, "pct_mgmt": 45.0},
    "Work From Home": {"workers": 22_486_510,  "median_earnings": 70_280, "commute_min": None,  "pct_no_vehicle": 4.5,  "pct_mgmt": 63.9},
}
MODEL_DATA = {
    "Drive Alone": {
        "income":     {"low": 0.225, "mid": 0.287, "high": 0.214, "very_high": 0.274},
        "occupation": {"management": 0.406, "service": 0.165, "sales": 0.189, "production": 0.236},
        "vehicles":   {"none": 0.017, "one": 0.199, "two": 0.412, "three_plus": 0.372},
        "commute":    {"short": 0.407, "medium": 0.286, "long": 0.077},
    },
    "Carpool": {
        "income":     {"low": 0.329, "mid": 0.324, "high": 0.173, "very_high": 0.175},
        "occupation": {"management": 0.325, "service": 0.210, "sales": 0.178, "production": 0.283},
        "vehicles":   {"none": 0.050, "one": 0.213, "two": 0.364, "three_plus": 0.373},
        "commute":    {"short": 0.412, "medium": 0.274, "long": 0.095},
    },
    "Public Transit": {
        "income":     {"low": 0.268, "mid": 0.251, "high": 0.155, "very_high": 0.326},
        "occupation": {"management": 0.450, "service": 0.231, "sales": 0.176, "production": 0.142},
        "vehicles":   {"none": 0.394, "one": 0.311, "two": 0.189, "three_plus": 0.105},
        "commute":    {"short": 0.077, "medium": 0.412, "long": 0.361},
    },
    "Work From Home": {
        "income":     {"low": 0.166, "mid": 0.183, "high": 0.183, "very_high": 0.467},
        "occupation": {"management": 0.639, "service": 0.077, "sales": 0.212, "production": 0.070},
        "vehicles":   {"none": 0.045, "one": 0.244, "two": 0.436, "three_plus": 0.274},
        "commute":    {"short": 0.500, "medium": 0.250, "long": 0.050},
    },
}
CRITERIA = [
    {"rank": 1, "icon": "💰", "name": "Annual Income",       "strength": 97, "badge": "VERY HIGH", "color": "green",  "stat": "$33,801 gap",    "detail": "WFH earns 92.6% more than Carpool"},
    {"rank": 2, "icon": "🚗", "name": "Vehicle Access",      "strength": 94, "badge": "VERY HIGH", "color": "green",  "stat": "39.4% vs 1.7%",  "detail": "Transit riders 23× more vehicle-free"},
    {"rank": 3, "icon": "💼", "name": "Occupation Type",     "strength": 82, "badge": "HIGH",      "color": "yellow", "stat": "64% mgmt WFH",   "detail": "Management occupation drives WFH"},
    {"rank": 4, "icon": "⏱️", "name": "Commute Duration",    "strength": 78, "badge": "HIGH",      "color": "yellow", "stat": "22.8 min gap",   "detail": "Transit commutes 87% longer"},
    {"rank": 5, "icon": "📉", "name": "Poverty Rate",        "strength": 71, "badge": "HIGH",      "color": "yellow", "stat": "9.7% vs 2.9%",   "detail": "Transit riders 3.3× more in poverty"},
    {"rank": 6, "icon": "🏠", "name": "Housing Tenure",      "strength": 62, "badge": "MEDIUM",    "color": "cyan",   "stat": "71% own home",   "detail": "WFH workers more likely homeowners"},
    {"rank": 7, "icon": "🌍", "name": "Foreign Born",        "strength": 55, "badge": "MEDIUM",    "color": "cyan",   "stat": "24% vs 15%",     "detail": "Carpool riders more likely foreign-born"},
    {"rank": 8, "icon": "📅", "name": "Age Distribution",    "strength": 44, "badge": "MEDIUM",    "color": "cyan",   "stat": "42.6 vs 38.3",   "detail": "WFH workers skew slightly older"},
    {"rank": 9, "icon": "⚧️", "name": "Gender Distribution", "strength": 28, "badge": "LOW",       "color": "orange", "stat": "55% male",        "detail": "Slight male majority across modes"},
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def hp_bar(value: int, color: str = "green") -> str:
    return f"""
<div class="hp-track">
  <div class="hp-fill {color}" style="width:{value}%"></div>
</div>"""

def badge(label: str) -> str:
    palette = {"VERY HIGH": "#00ff41", "HIGH": "#ffe600", "MEDIUM": "#00e5ff", "LOW": "#888888"}
    c = palette.get(label, "#888888")
    return f'<span style="font-size:0.5rem;padding:2px 5px;border:1px solid {c};color:{c}">{label}</span>'

def predict(income: str, occupation: str, vehicles: str, commute: str):
    MODES = list(MODEL_DATA.keys())
    scores = {}
    for mode in MODES:
        d = MODEL_DATA[mode]
        score = (
            d["income"].get(income, 0.1) *
            d["occupation"].get(occupation, 0.1) *
            d["vehicles"].get(vehicles, 0.1) *
            d["commute"].get(commute, 0.1)
        )
        if vehicles == "none" and mode == "Drive Alone":    score = 0
        if vehicles == "none" and mode == "Carpool":        score *= 0.1
        if commute  == "long"  and mode == "Work From Home": score = 0
        scores[mode] = score
    total = sum(scores.values()) or 1
    return sorted(
        [(m, round(scores[m] / total * 100)) for m in MODES],
        key=lambda x: -x[1],
    )

def neon_chart(title: str, modes, values, colors, fmt=None) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=modes, y=values,
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="%{x}<br>%{y}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(family="Share Tech Mono", size=12, color="#00ff41")),
        paper_bgcolor="#0a0f1e",
        plot_bgcolor="#0a0f1e",
        font=dict(family="Share Tech Mono", color="#00ff41"),
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#666")),
        yaxis=dict(showgrid=True, gridcolor="#1a2040", tickfont=dict(size=9, color="#666")),
        margin=dict(t=40, b=10, l=10, r=10),
        height=260,
    )
    for m, v, c in zip(modes, values, colors):
        if v is not None:
            fig.add_annotation(
                x=m, y=v,
                text=fmt(v) if fmt else str(v),
                showarrow=False, yanchor="bottom", yshift=4,
                font=dict(color=c, size=9, family="Share Tech Mono"),
            )
    return fig

# ─── SECTIONS ─────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
<div style="text-align:center;padding:3.5rem 1rem 2rem;
     background:radial-gradient(ellipse at center, #0d2b1a 0%, #020409 65%)">
  <div style="font-size:0.55rem;color:#00ff41;letter-spacing:0.3em;margin-bottom:0.75rem">
    ▶ TSA 2026 STATE COMPETITION
  </div>
  <h1 style="font-family:'Press Start 2P',monospace;
             font-size:clamp(1.1rem,3.5vw,2.2rem);
             color:#00ff41;
             text-shadow:0 0 20px #00ff41,0 0 40px #00ff41,2px 2px 0 #003310;
             line-height:1.5;margin:0">
    COMMUTE<br>PREDICTOR
  </h1>
  <div style="color:#00e5ff;font-size:0.7rem;margin:1rem 0;letter-spacing:0.08em">
    U.S. CENSUS ACS 2023 · DETAILED TRANSPORTATION ANALYSIS
  </div>
  <div style="color:#444;font-size:0.6rem">AYAANSH ARORA &amp; DIVYANSH SINGH</div>
  <div style="display:flex;justify-content:center;gap:2.5rem;margin-top:2rem;flex-wrap:wrap">
    <div style="text-align:center">
      <div style="color:#00ff41;font-family:'Press Start 2P',monospace;font-size:1rem">162.4M</div>
      <div style="color:#444;font-size:0.55rem;margin-top:4px">WORKERS ANALYZED</div>
    </div>
    <div style="text-align:center">
      <div style="color:#00e5ff;font-family:'Press Start 2P',monospace;font-size:1rem">78</div>
      <div style="color:#444;font-size:0.55rem;margin-top:4px">DATA VARIABLES</div>
    </div>
    <div style="text-align:center">
      <div style="color:#ffe600;font-family:'Press Start 2P',monospace;font-size:1rem">9</div>
      <div style="color:#444;font-size:0.55rem;margin-top:4px">KEY CRITERIA</div>
    </div>
    <div style="text-align:center">
      <div style="color:#ff00aa;font-family:'Press Start 2P',monospace;font-size:1rem">95%</div>
      <div style="color:#444;font-size:0.55rem;margin-top:4px">MODEL ACCURACY</div>
    </div>
  </div>
</div>
<div class="neon-divider"></div>
""", unsafe_allow_html=True)


def render_criteria():
    st.markdown("""
<h2 style="font-family:'Press Start 2P',monospace;color:#00e5ff;font-size:0.85rem;
           text-align:center;margin-bottom:0.3rem">⚡ PREDICTION CRITERIA</h2>
<div style="text-align:center;color:#444;font-size:0.65rem;margin-bottom:1.5rem">
  9 VARIABLES RANKED BY PREDICTIVE STRENGTH
</div>
""", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, c in enumerate(CRITERIA):
        with cols[i % 3]:
            st.markdown(f"""
<div class="game-card">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem">
    <span style="font-size:0.55rem;color:#333">#{c['rank']}</span>
    {badge(c['badge'])}
  </div>
  <div style="font-size:0.75rem;color:#ccc;margin-bottom:0.4rem">{c['icon']} {c['name']}</div>
  {hp_bar(c['strength'], c['color'])}
  <div style="display:flex;justify-content:space-between;margin-top:0.35rem">
    <span style="font-size:0.65rem;color:#00ff41">{c['stat']}</span>
    <span style="font-size:0.55rem;color:#555">{c['strength']}%</span>
  </div>
  <div style="font-size:0.55rem;color:#444;margin-top:0.2rem">{c['detail']}</div>
</div>
""", unsafe_allow_html=True)


def render_predictor():
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
<h2 style="font-family:'Press Start 2P',monospace;color:#00ff41;font-size:0.85rem;
           text-align:center;margin-bottom:0.3rem">🎮 PREDICTOR</h2>
<div style="text-align:center;color:#444;font-size:0.65rem;margin-bottom:1.5rem">
  SELECT YOUR PROFILE · BAYESIAN SCORING ACROSS 4 CENSUS-DERIVED CRITERIA
</div>
""", unsafe_allow_html=True)

    col_form, col_result = st.columns([1, 1], gap="large")

    INCOME_OPTS  = {"Low — Under $35,000": "low", "Mid — $35,000–$75,000": "mid",
                    "High — $35,000–$75,000": "high", "$75,000+ — High earner": "very_high"}
    OCC_OPTS     = {"Management, Business, Science & Arts": "management", "Service Occupations": "service",
                    "Sales & Office": "sales", "Production, Transport & Material": "production"}
    VEH_OPTS     = {"No vehicle available": "none", "1 vehicle": "one",
                    "2 vehicles": "two", "3 or more vehicles": "three_plus"}
    COMMUTE_OPTS = {"Short — under 30 minutes": "short", "Medium — 30–60 minutes": "medium",
                    "Long — over 60 minutes": "long"}

    with col_form:
        st.markdown('<div style="font-size:0.55rem;color:#00ff41;letter-spacing:0.1em;margin-bottom:0.25rem">💰 ANNUAL INCOME</div>', unsafe_allow_html=True)
        income_sel = st.selectbox("Income", list(INCOME_OPTS.keys()), label_visibility="collapsed", key="income")

        st.markdown('<div style="font-size:0.55rem;color:#00ff41;letter-spacing:0.1em;margin-bottom:0.25rem;margin-top:0.75rem">💼 OCCUPATION TYPE</div>', unsafe_allow_html=True)
        occ_sel = st.selectbox("Occupation", list(OCC_OPTS.keys()), label_visibility="collapsed", key="occ")

        st.markdown('<div style="font-size:0.55rem;color:#00ff41;letter-spacing:0.1em;margin-bottom:0.25rem;margin-top:0.75rem">🚗 VEHICLES AVAILABLE</div>', unsafe_allow_html=True)
        veh_sel = st.selectbox("Vehicles", list(VEH_OPTS.keys()), label_visibility="collapsed", key="veh")

        st.markdown('<div style="font-size:0.55rem;color:#00ff41;letter-spacing:0.1em;margin-bottom:0.25rem;margin-top:0.75rem">⏱️ TYPICAL COMMUTE</div>', unsafe_allow_html=True)
        com_sel = st.selectbox("Commute", list(COMMUTE_OPTS.keys()), label_visibility="collapsed", key="com")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶ RUN PREDICTION", use_container_width=True)

    with col_result:
        if run:
            income_k = INCOME_OPTS[income_sel]
            occ_k    = OCC_OPTS[occ_sel]
            veh_k    = VEH_OPTS[veh_sel]
            com_k    = COMMUTE_OPTS[com_sel]
            results  = predict(income_k, occ_k, veh_k, com_k)
            st.session_state["result"]    = results
            st.session_state["breakdown"] = {
                "income":     round(MODEL_DATA[results[0][0]]["income"].get(income_k, 0.1) * 100),
                "occupation": round(MODEL_DATA[results[0][0]]["occupation"].get(occ_k, 0.1) * 100),
                "vehicles":   round(MODEL_DATA[results[0][0]]["vehicles"].get(veh_k, 0.1) * 100),
                "commute":    round(MODEL_DATA[results[0][0]]["commute"].get(com_k, 0.1) * 100),
            }

        if "result" in st.session_state:
            results   = st.session_state["result"]
            breakdown = st.session_state["breakdown"]
            top_mode, top_pct = results[0]
            top_color = COLORS[top_mode]
            top_icon  = MODE_ICONS[top_mode]
            color_cls = {"Drive Alone":"cyan","Carpool":"yellow","Public Transit":"pink","Work From Home":"green"}

            st.markdown(f"""
<div class="result-card">
  <div style="font-size:0.5rem;color:#444;letter-spacing:0.2em;margin-bottom:0.5rem">▶ PREDICTION RESULT</div>
  <div style="font-size:2.5rem;text-align:center;margin:0.5rem 0">{top_icon}</div>
  <div style="font-family:'Press Start 2P',monospace;font-size:clamp(0.7rem,2vw,1rem);
              color:{top_color};text-shadow:0 0 15px {top_color};text-align:center;margin:0.5rem 0">
    {top_mode.upper()}
  </div>
  <div style="display:flex;justify-content:space-between;font-size:0.6rem;color:#555;margin:0.75rem 0 0.2rem">
    <span>CONFIDENCE</span><span style="color:{top_color}">{top_pct}%</span>
  </div>
  {hp_bar(top_pct, color_cls[top_mode])}
</div>
""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1rem'>", unsafe_allow_html=True)
            for mode, pct in results:
                c = COLORS[mode]
                cl = color_cls[mode]
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin:5px 0">
  <span style="font-size:1rem;min-width:24px">{MODE_ICONS[mode]}</span>
  <span style="font-size:0.6rem;color:{c};min-width:110px">{mode}</span>
  <div class="hp-track" style="flex:1"><div class="hp-fill {cl}" style="width:{pct}%"></div></div>
  <span style="font-size:0.6rem;color:{c};min-width:28px;text-align:right">{pct}%</span>
</div>
""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"""
<div style="background:#050a15;border:1px solid #1a2040;padding:1rem;margin-top:1rem">
  <div style="font-size:0.55rem;color:#444;letter-spacing:0.15em;margin-bottom:0.75rem">FACTOR BREAKDOWN</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem">
    <div style="text-align:center;padding:0.5rem;background:#0a0f1e">
      <div style="font-size:0.5rem;color:#555">INCOME</div>
      <div style="font-size:1rem;color:#00ff41">{breakdown['income']}%</div>
    </div>
    <div style="text-align:center;padding:0.5rem;background:#0a0f1e">
      <div style="font-size:0.5rem;color:#555">OCCUPATION</div>
      <div style="font-size:1rem;color:#00ff41">{breakdown['occupation']}%</div>
    </div>
    <div style="text-align:center;padding:0.5rem;background:#0a0f1e">
      <div style="font-size:0.5rem;color:#555">VEHICLES</div>
      <div style="font-size:1rem;color:#00ff41">{breakdown['vehicles']}%</div>
    </div>
    <div style="text-align:center;padding:0.5rem;background:#0a0f1e">
      <div style="font-size:0.5rem;color:#555">COMMUTE</div>
      <div style="font-size:1rem;color:#00ff41">{breakdown['commute']}%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="result-card" style="min-height:320px;display:flex;align-items:center;
     justify-content:center;flex-direction:column;gap:1rem">
  <div style="font-size:2.5rem">🎮</div>
  <div style="font-family:'Press Start 2P',monospace;font-size:0.65rem;color:#333">AWAITING INPUT...</div>
  <div style="font-size:0.6rem;color:#333">SELECT YOUR PROFILE AND RUN PREDICTION</div>
</div>
""", unsafe_allow_html=True)


def render_charts():
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
<h2 style="font-family:'Press Start 2P',monospace;color:#00e5ff;font-size:0.85rem;
           text-align:center;margin-bottom:0.3rem">📊 DATA ANALYSIS</h2>
<div style="text-align:center;color:#444;font-size:0.65rem;margin-bottom:1.5rem">
  U.S. CENSUS ACS 2023 · REAL DATA FROM 162M WORKERS
</div>
""", unsafe_allow_html=True)

    modes  = list(CHART_DATA.keys())
    colors = [COLORS[m] for m in modes]

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        fig1 = neon_chart(
            "MEDIAN ANNUAL EARNINGS ($)", modes,
            [CHART_DATA[m]["median_earnings"] for m in modes], colors,
            fmt=lambda v: f"${v:,}",
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig3 = neon_chart(
            "MANAGEMENT OCCUPATIONS (%)", modes,
            [CHART_DATA[m]["pct_mgmt"] for m in modes], colors,
            fmt=lambda v: f"{v}%",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig2 = neon_chart(
            "NO VEHICLE AVAILABLE (%)", modes,
            [CHART_DATA[m]["pct_no_vehicle"] for m in modes], colors,
            fmt=lambda v: f"{v}%",
        )
        st.plotly_chart(fig2, use_container_width=True)

        modes_c  = [m for m in modes if CHART_DATA[m]["commute_min"] is not None]
        colors_c = [COLORS[m] for m in modes_c]
        fig4 = neon_chart(
            "MEAN COMMUTE TIME (MINUTES)", modes_c,
            [CHART_DATA[m]["commute_min"] for m in modes_c], colors_c,
            fmt=lambda v: f"{v} min",
        )
        st.plotly_chart(fig4, use_container_width=True)


def render_analysis():
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
<h2 style="font-family:'Press Start 2P',monospace;color:#ff00aa;font-size:0.85rem;
           text-align:center;margin-bottom:1.5rem">🔍 TWO-TIER ANALYSIS</h2>
<div style="background:#0a0f1e;border:1px solid #ff00aa;border-left:4px solid #ff00aa;
            padding:1rem;margin-bottom:1.5rem;text-align:center;
            box-shadow:0 0 20px rgba(255,0,170,0.1)">
  <div style="font-size:0.55rem;color:#ff00aa;letter-spacing:0.15em">KEY FINDING</div>
  <div style="font-size:0.85rem;color:#fff;margin:0.5rem 0;font-family:'Share Tech Mono',monospace">
    Transportation mode creates a <span style="color:#ff00aa">socioeconomic divide</span> — not just a mobility gap
  </div>
  <div style="font-size:0.6rem;color:#555">WFH earns 92.6% more than Carpool workers · Income gap = $33,801/year</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("""
<div style="background:#0a0f1e;border:1px solid #00ff41;padding:1.25rem;height:200px">
  <div style="color:#00ff41;font-size:0.6rem;letter-spacing:0.15em;margin-bottom:0.75rem">TIER 1 — PRIVILEGED MOBILITY</div>
  <div style="display:flex;gap:0.75rem;margin-bottom:0.75rem;flex-wrap:wrap">
    <span style="padding:3px 8px;border:1px solid #00ff41;color:#00ff41;font-size:0.55rem">🏠 WORK FROM HOME</span>
    <span style="padding:3px 8px;border:1px solid #00e5ff;color:#00e5ff;font-size:0.55rem">🚗 DRIVE ALONE</span>
  </div>
  <div style="font-size:0.6rem;color:#666;line-height:1.8">
    • <span style="color:#00ff41">$70,280</span> avg WFH earnings<br>
    • 64% management occupations<br>
    • 92% vehicle ownership<br>
    • <span style="color:#00ff41">Winners of remote work era</span>
  </div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div style="background:#0a0f1e;border:1px solid #ff6b00;padding:1.25rem;height:200px">
  <div style="color:#ff6b00;font-size:0.6rem;letter-spacing:0.15em;margin-bottom:0.75rem">TIER 2 — CONSTRAINED MOBILITY</div>
  <div style="display:flex;gap:0.75rem;margin-bottom:0.75rem;flex-wrap:wrap">
    <span style="padding:3px 8px;border:1px solid #ff00aa;color:#ff00aa;font-size:0.55rem">🚇 PUBLIC TRANSIT</span>
    <span style="padding:3px 8px;border:1px solid #ffe600;color:#ffe600;font-size:0.55rem">🚌 CARPOOL</span>
  </div>
  <div style="font-size:0.6rem;color:#666;line-height:1.8">
    • <span style="color:#ff6b00">$36,479</span> avg Carpool earnings<br>
    • 39.4% transit riders without vehicles<br>
    • 48.9 min avg transit commute<br>
    • <span style="color:#ff6b00">Underserved by current policy</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    solutions = [
        ("🏙️", "FOR CITIES",       "Expand transit in low-income corridors. Reduce the 22.8-minute commute gap."),
        ("🏢", "FOR EMPLOYERS",    "Subsidize transit passes for service & production workers. Close the mobility gap."),
        ("📋", "FOR POLICYMAKERS", "Target vehicle access programs for the 39.4% of transit riders without cars."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], solutions):
        with col:
            st.markdown(f"""
<div class="game-card" style="border-top:2px solid #00e5ff;text-align:center;padding:1.25rem">
  <div style="font-size:1.5rem">{icon}</div>
  <div style="font-size:0.55rem;color:#00e5ff;letter-spacing:0.1em;margin:0.5rem 0">{title}</div>
  <div style="font-size:0.58rem;color:#555;line-height:1.7">{desc}</div>
</div>
""", unsafe_allow_html=True)


def render_footer():
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center;padding:2rem 0;color:#222;font-size:0.55rem">
  <div style="font-family:'Press Start 2P',monospace;color:#111;font-size:0.45rem">
    TSA 2026 · TECHNOLOGY STUDENT ASSOCIATION · STATE COMPETITION
  </div>
  <div style="margin-top:0.5rem">DATA SOURCE: U.S. CENSUS BUREAU · AMERICAN COMMUNITY SURVEY 2023</div>
  <div style="margin-top:0.5rem">DIVYANSH SINGH &amp; AYAANSH ARORA</div>
</div>
""", unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
inject_styles()
render_hero()
render_criteria()
render_predictor()
render_charts()
render_analysis()
render_footer()

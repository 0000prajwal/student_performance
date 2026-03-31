import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; }
    .metric-label { font-size: 0.9rem; opacity: 0.85; margin-top: 4px; }
    h1 { color: #2d3748; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("StudentPerformanceFactors.csv")
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.title("🎛️ Filters")
st.sidebar.markdown("---")

gender_opts = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
gender = st.sidebar.selectbox("Gender", gender_opts)

school_opts = ["All"] + sorted(df["School_Type"].dropna().unique().tolist())
school = st.sidebar.selectbox("School Type", school_opts)

income_opts = ["All"] + ["Low", "Medium", "High"]
income = st.sidebar.selectbox("Family Income", income_opts)

motivation_opts = ["All"] + ["Low", "Medium", "High"]
motivation = st.sidebar.selectbox("Motivation Level", motivation_opts)

score_range = st.sidebar.slider(
    "Exam Score Range",
    int(df["Exam_Score"].min()),
    int(df["Exam_Score"].max()),
    (int(df["Exam_Score"].min()), int(df["Exam_Score"].max())),
)

# Apply filters
mask = pd.Series([True] * len(df))
if gender != "All":
    mask &= df["Gender"] == gender
if school != "All":
    mask &= df["School_Type"] == school
if income != "All":
    mask &= df["Family_Income"] == income
if motivation != "All":
    mask &= df["Motivation_Level"] == motivation
mask &= (df["Exam_Score"] >= score_range[0]) & (df["Exam_Score"] <= score_range[1])

dff = df[mask].copy()
st.sidebar.markdown(f"**{len(dff):,} students** selected")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎓 Student Performance Analytics Dashboard")
st.markdown("Explore factors that influence student exam scores across **6,607 students**.")
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(dff):,}</div>
        <div class="metric-label">Students</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{dff['Exam_Score'].mean():.1f}</div>
        <div class="metric-label">Avg Exam Score</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{dff['Attendance'].mean():.1f}%</div>
        <div class="metric-label">Avg Attendance</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{dff['Hours_Studied'].mean():.1f}</div>
        <div class="metric-label">Avg Hours Studied</div></div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{dff['Tutoring_Sessions'].mean():.1f}</div>
        <div class="metric-label">Avg Tutoring Sessions</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "🔍 Factor Analysis", "📈 Correlations", "🗂️ Raw Data"]
)

# ────────────────────────── TAB 1: OVERVIEW ──────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Exam Score Distribution")
        fig = px.histogram(
            dff, x="Exam_Score", nbins=30, color_discrete_sequence=["#667eea"],
            labels={"Exam_Score": "Exam Score", "count": "Count"},
            template="plotly_white",
        )
        fig.update_layout(bargap=0.05, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Score by Gender")
        fig = px.box(
            dff, x="Gender", y="Exam_Score",
            color="Gender", color_discrete_map={"Male": "#667eea", "Female": "#f093fb"},
            template="plotly_white",
            labels={"Exam_Score": "Exam Score"},
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("School Type Distribution")
        counts = dff["School_Type"].value_counts()
        fig = px.pie(
            values=counts.values, names=counts.index,
            color_discrete_sequence=["#667eea", "#f093fb"],
            hole=0.45, template="plotly_white",
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Avg Score by School Type & Gender")
        grp = dff.groupby(["School_Type", "Gender"])["Exam_Score"].mean().reset_index()
        fig = px.bar(
            grp, x="School_Type", y="Exam_Score", color="Gender", barmode="group",
            color_discrete_map={"Male": "#667eea", "Female": "#f093fb"},
            template="plotly_white",
            labels={"Exam_Score": "Avg Exam Score"},
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────── TAB 2: FACTOR ANALYSIS ──────────────────────────────
with tab2:
    st.subheader("How Categorical Factors Affect Exam Scores")

    cat_cols = {
        "Parental Involvement": "Parental_Involvement",
        "Access to Resources": "Access_to_Resources",
        "Motivation Level": "Motivation_Level",
        "Family Income": "Family_Income",
        "Teacher Quality": "Teacher_Quality",
        "Peer Influence": "Peer_Influence",
        "Parental Education": "Parental_Education_Level",
        "Internet Access": "Internet_Access",
        "Extracurricular Activities": "Extracurricular_Activities",
        "Learning Disabilities": "Learning_Disabilities",
        "Distance from Home": "Distance_from_Home",
    }

    selected_factor = st.selectbox("Select a factor to explore:", list(cat_cols.keys()))
    col_name = cat_cols[selected_factor]

    col1, col2 = st.columns([3, 2])

    with col1:
        grp = dff.groupby(col_name)["Exam_Score"].agg(["mean", "std", "count"]).reset_index()
        grp.columns = [col_name, "Mean Score", "Std Dev", "Count"]
        fig = px.bar(
            grp, x=col_name, y="Mean Score",
            error_y="Std Dev",
            color="Mean Score",
            color_continuous_scale="Viridis",
            template="plotly_white",
            text="Mean Score",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Group Statistics**")
        st.dataframe(
            grp.style.format({"Mean Score": "{:.2f}", "Std Dev": "{:.2f}"}),
            use_container_width=True, height=300,
        )

    st.markdown("---")
    st.subheader("Numeric Factor vs Exam Score")

    num_cols = {
        "Hours Studied": "Hours_Studied",
        "Attendance (%)": "Attendance",
        "Sleep Hours": "Sleep_Hours",
        "Previous Scores": "Previous_Scores",
        "Tutoring Sessions": "Tutoring_Sessions",
        "Physical Activity": "Physical_Activity",
    }

    selected_num = st.selectbox("Select a numeric factor:", list(num_cols.keys()))
    num_col = num_cols[selected_num]

    fig = px.scatter(
        dff, x=num_col, y="Exam_Score",
        color="Gender",
        color_discrete_map={"Male": "#667eea", "Female": "#f093fb"},
        opacity=0.5, trendline="ols",
        template="plotly_white",
        labels={num_col: selected_num, "Exam_Score": "Exam Score"},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────── TAB 3: CORRELATIONS ─────────────────────────────────
with tab3:
    st.subheader("Correlation Matrix — Numeric Variables")

    num_df = dff[["Hours_Studied", "Attendance", "Sleep_Hours",
                  "Previous_Scores", "Tutoring_Sessions", "Physical_Activity", "Exam_Score"]]
    corr = num_df.corr()

    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, template="plotly_white",
        labels={"color": "Correlation"},
    )
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Feature Impact on Exam Score (Avg Score by Quartile)")

    q_col = st.selectbox("Choose variable for quartile analysis:", list(num_cols.keys()), key="q_sel")
    qc = num_cols[q_col]

    dff["Quartile"] = pd.qcut(dff[qc], q=4, labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"])
    grp_q = dff.groupby("Quartile", observed=True)["Exam_Score"].mean().reset_index()

    fig = px.line(
        grp_q, x="Quartile", y="Exam_Score", markers=True,
        color_discrete_sequence=["#667eea"],
        template="plotly_white",
        labels={"Exam_Score": "Avg Exam Score", "Quartile": f"{q_col} Quartile"},
    )
    fig.update_traces(line_width=3, marker_size=10)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Exam Score by Multiple Categorical Dimensions")
    c1, c2 = st.columns(2)
    with c1:
        dim1 = st.selectbox("X-axis category:", list(cat_cols.keys()), key="hm1")
    with c2:
        dim2 = st.selectbox("Y-axis category:", list(cat_cols.keys()), index=1, key="hm2")

    pivot = dff.pivot_table(
        values="Exam_Score",
        index=cat_cols[dim1],
        columns=cat_cols[dim2],
        aggfunc="mean",
    )
    fig = px.imshow(
        pivot, text_auto=".1f", color_continuous_scale="Viridis",
        template="plotly_white",
        labels={"color": "Avg Score", "x": dim2, "y": dim1},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────── TAB 4: RAW DATA ─────────────────────────────────────
with tab4:
    st.subheader(f"Filtered Dataset — {len(dff):,} rows")
    st.dataframe(dff.reset_index(drop=True), use_container_width=True, height=500)

    csv_bytes = dff.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_student_data.csv",
        mime="text/csv",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📂 Data: StudentPerformanceFactors.csv  |  Built with Streamlit + Plotly")

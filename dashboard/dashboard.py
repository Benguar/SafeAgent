import sys
from pathlib import Path

# Add the project root (parent of this file's folder) to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px 
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
from src.config.settings import settings
# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="SafeAgent Dashboard",
    page_icon="\U0001F6E1\uFE0F",
    layout="wide",
    initial_sidebar_state="expanded",
)

DECISION_COLORS = {
    "ALLOW": "#2ecc71",
    "SANITIZE": "#f39c12",
    "BLOCK": "#e74c3c",
}

# --------------------------------------------------------------------------
# Database connection
# --------------------------------------------------------------------------
@st.cache_resource
def get_engine():
    conn_str = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    return create_engine(conn_str, pool_pre_ping=True) 


@st.cache_data(ttl=60, show_spinner=False)
def load_table(table_name: str, start, end) -> pd.DataFrame:
    """Load a logging table filtered by created_at range."""
    engine = get_engine()
    query = f"""
        SELECT * FROM public.{table_name}
        WHERE created_at BETWEEN %(start)s AND %(end)s
        ORDER BY created_at ASC
    """
    df = pd.read_sql(query, engine, params={"start": start, "end": end})
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def flatten_violations(df: pd.DataFrame) -> pd.Series:
    """Turn a jsonb violations column (list of strings/objects) into a flat
    list of individual violation labels for counting."""
    all_v = []
    if "violations" not in df.columns:
        return pd.Series(all_v, dtype=str)
    for val in df["violations"].dropna():
        items = val
        if isinstance(val, str):
            try:
                items = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                items = [val]
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    label = item.get("type") or item.get("name") or str(item)
                else:
                    label = str(item)
                all_v.append(label)
        elif items:
            all_v.append(str(items))
    return pd.Series(all_v, dtype=str)


def decision_pie(df: pd.DataFrame, title: str):
    if df.empty or "decision" not in df.columns:
        st.info("No data for this range.")
        return
    counts = df["decision"].value_counts().reset_index()
    counts.columns = ["decision", "count"]
    fig = px.pie(
        counts,
        names="decision",
        values="count",
        title=title,
        color="decision",
        color_discrete_map=DECISION_COLORS,
        hole=0.45,
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def timeline_chart(df: pd.DataFrame, title: str, freq: str = "h"):
    if df.empty:
        st.info("No data for this range.")
        return
    ts = (
        df.set_index("created_at")
        .groupby([pd.Grouper(freq=freq), "decision"])
        .size()
        .reset_index(name="count")
    )
    fig = px.line(
        ts,
        x="created_at",
        y="count",
        color="decision",
        title=title,
        color_discrete_map=DECISION_COLORS,
        markers=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def kpi_row(df: pd.DataFrame):
    total = len(df)
    allow = int((df["decision"] == "ALLOW").sum()) if "decision" in df.columns else 0
    sanitize = int((df["decision"] == "SANITIZE").sum()) if "decision" in df.columns else 0
    block = int((df["decision"] == "BLOCK").sum()) if "decision" in df.columns else 0
    flagged_rate = ((sanitize + block) / total * 100) if total else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total events", f"{total:,}")
    c2.metric("Allowed", f"{allow:,}")
    c3.metric("Sanitized", f"{sanitize:,}")
    c4.metric("Blocked", f"{block:,}")
    c5.metric("Flagged rate", f"{flagged_rate:.1f}%")


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
st.sidebar.title("\U0001F6E1\uFE0F SafeAgent")
st.sidebar.caption("Security middleware logging dashboard")

default_start = datetime.now() - timedelta(days=7)
default_end = datetime.now()

date_range = st.sidebar.date_input(
    "Date range",
    value=(default_start.date(), default_end.date()),
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start.date(), default_end.date()

start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

if st.sidebar.button("\U0001F504 Refresh data"):
    st.cache_data.clear()

st.sidebar.markdown("---")
decision_filter = st.sidebar.multiselect(
    "Filter by decision",
    options=["ALLOW", "SANITIZE", "BLOCK"],
    default=["ALLOW", "SANITIZE", "BLOCK"],
)

# --------------------------------------------------------------------------
# Load data
# --------------------------------------------------------------------------
with st.spinner("Loading logs from Postgres..."):
    try:
        prompt_df = load_table("prompt_logging", start_dt, end_dt)
        tool_df = load_table("tool_output_logging", start_dt, end_dt)
        final_df = load_table("final_output_logging", start_dt, end_dt)
    except Exception as e:
        st.error(f"Could not connect to the database: {e}")
        st.stop()

if decision_filter:
    if "decision" in prompt_df.columns:
        prompt_df = prompt_df[prompt_df["decision"].isin(decision_filter)]
    if "decision" in tool_df.columns:
        tool_df = tool_df[tool_df["decision"].isin(decision_filter)]
    if "decision" in final_df.columns:
        final_df = final_df[final_df["decision"].isin(decision_filter)]

# --------------------------------------------------------------------------
# Header + overall KPIs
# --------------------------------------------------------------------------
st.title("SafeAgent Logging Dashboard")
st.caption(
    f"Showing events from **{start_date}** to **{end_date}** "
    f"\u2014 prompt: {len(prompt_df):,} \u00b7 tool: {len(tool_df):,} \u00b7 final: {len(final_df):,}"
)

frames = []
if not prompt_df.empty:
    frames.append(prompt_df.assign(source="prompt"))
if not tool_df.empty:
    frames.append(tool_df.assign(source="tool"))
if not final_df.empty:
    frames.append(final_df.assign(source="final"))
combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["decision", "created_at", "source"])

kpi_row(combined)

st.markdown("---")

# --------------------------------------------------------------------------
# Tabs per table
# --------------------------------------------------------------------------
tab_overview, tab_prompt, tab_tool, tab_final = st.tabs(
    ["\U0001F4CA Overview", "\U0001F4AC Prompt Logging", "\U0001F527 Tool Output", "\u2705 Final Output"]
)

# ---- Overview ----
with tab_overview:
    col1, col2 = st.columns(2)
    with col1:
        decision_pie(combined, "Decisions across all pipelines")
    with col2:
        timeline_chart(combined, "Event volume over time", freq="h")

    st.subheader("Top violation types")
    viol = flatten_violations(combined)
    if not viol.empty:
        top_viol = viol.value_counts().head(15).reset_index()
        top_viol.columns = ["violation", "count"]
        fig = px.bar(top_viol, x="count", y="violation", orientation="h", title="Most common violations")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No violations recorded in this range.")

    st.subheader("Breakdown by pipeline stage")
    if not combined.empty and "source" in combined.columns:
        stage_decision = combined.groupby(["source", "decision"]).size().reset_index(name="count")
        fig = px.bar(
            stage_decision,
            x="source",
            y="count",
            color="decision",
            barmode="group",
            color_discrete_map=DECISION_COLORS,
            title="Decisions by pipeline stage",
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- Prompt Logging ----
with tab_prompt:
    st.subheader("Prompt Logging")
    kpi_row(prompt_df)
    col1, col2 = st.columns(2)
    with col1:
        decision_pie(prompt_df, "Prompt decisions")
    with col2:
        if not prompt_df.empty and "ml_score" in prompt_df.columns:
            fig = px.histogram(
                prompt_df,
                x="ml_score",
                color="decision",
                nbins=30,
                color_discrete_map=DECISION_COLORS,
                title="ML score distribution",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ML score data available.")

    if not prompt_df.empty and "user_id" in prompt_df.columns:
        st.subheader("Activity by user")
        by_user = (
            prompt_df.groupby("user_id").size().reset_index(name="count").sort_values("count", ascending=False)
        )
        st.dataframe(by_user, use_container_width=True, hide_index=True)

    st.subheader("Raw prompt log")
    display_cols = [c for c in ["created_at", "user_id", "chat_id", "role", "prompt", "decision", "ml_score", "violations"] if c in prompt_df.columns]
    st.dataframe(prompt_df[display_cols].sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)

# ---- Tool Output Logging ----
with tab_tool:
    st.subheader("Tool Output Logging")
    kpi_row(tool_df)
    col1, col2 = st.columns(2)
    with col1:
        decision_pie(tool_df, "Tool output decisions")
    with col2:
        if not tool_df.empty and "name" in tool_df.columns:
            by_tool = tool_df["name"].value_counts().reset_index()
            by_tool.columns = ["tool_name", "count"]
            fig = px.bar(by_tool.head(15), x="count", y="tool_name", orientation="h", title="Calls by tool name")
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    if not tool_df.empty and {"name", "decision"}.issubset(tool_df.columns):
        st.subheader("Decision rate per tool")
        rate = tool_df.groupby(["name", "decision"]).size().reset_index(name="count")
        fig = px.bar(
            rate,
            x="name",
            y="count",
            color="decision",
            barmode="stack",
            color_discrete_map=DECISION_COLORS,
            title="Decisions per tool",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw tool output log")
    display_cols = [c for c in ["created_at", "role", "tool_call_id", "name", "content", "decision", "violations"] if c in tool_df.columns]
    st.dataframe(tool_df[display_cols].sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)

# ---- Final Output Logging ----
with tab_final:
    st.subheader("Final Output Logging")
    kpi_row(final_df)
    col1, col2 = st.columns(2)
    with col1:
        decision_pie(final_df, "Final output decisions")
    with col2:
        timeline_chart(final_df, "Final outputs over time", freq="h")

    st.subheader("Raw final output log")
    display_cols = [c for c in ["created_at", "output", "decision", "violations"] if c in final_df.columns]
    st.dataframe(final_df[display_cols].sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("SafeAgent \u00b7 built with Streamlit, SQLAlchemy & Plotly")
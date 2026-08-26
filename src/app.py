import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "clean" / "labour_tidy.csv"

METRIC_LABELS = {
    "unemployment_rate": "Unemployment rate (%)",
    "employment_rate": "Employment rate (%)",
    "participation_rate": "Participation rate (%)",
    "employment": "Employment (thousands of persons)",
    "unemployment": "Unemployment (thousands of persons)",
    "population": "Population (thousands of persons)",
    "labour_force": "Labour force (thousands of persons)",
}

st.set_page_config(page_title="Canadian Labour Market Dashboard", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


df = load_data()

st.title("Canadian Labour Market Dashboard")
st.markdown(
    "Monthly labour force data for Montréal, Toronto, and Vancouver "
    "(Census Metropolitan Areas), seasonally adjusted, from Statistics Canada "
    "[Table 14-10-0460-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410046001). "
    "**Note:** 'Toronto' here is the Toronto CMA, StatCan's standard geography — "
    "not the City of Toronto or the broader GTA boundary."
)

with st.sidebar:
    st.header("Filters")
    metric = st.selectbox(
        "Metric",
        options=list(METRIC_LABELS.keys()),
        format_func=lambda k: METRIC_LABELS[k],
    )
    cities = st.multiselect(
        "Cities",
        options=sorted(df["City"].unique()),
        default=sorted(df["City"].unique()),
    )
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.slider(
        "Date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="YYYY-MM",
    )

filtered = df[
    df["City"].isin(cities)
    & (df["date"] >= date_range[0])
    & (df["date"] <= date_range[1])
]

if filtered.empty or not cities:
    st.warning("No data for the current filter selection. Pick at least one city.")
    st.stop()

st.subheader(f"{METRIC_LABELS[metric]}")
chart_data = filtered.pivot(index="date", columns="City", values=metric)
st.line_chart(chart_data)

st.subheader(f"{METRIC_LABELS[metric]} — most recent month in range")
latest_date = filtered["date"].max()
latest = filtered[filtered["date"] == latest_date].set_index("City")[metric]
st.caption(f"As of {latest_date.strftime('%B %Y')}")
st.bar_chart(latest)

with st.expander("View underlying data"):
    st.dataframe(
        filtered[["date", "City", metric]].sort_values(["City", "date"]),
        use_container_width=True,
    )
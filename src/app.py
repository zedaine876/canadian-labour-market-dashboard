import pandas as pd
import plotly.express as px
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

# Rate metrics are already in percentage points; count metrics are thousands of persons.
RATE_METRICS = {"unemployment_rate", "employment_rate", "participation_rate"}

#Custom city colours (readability)
CITY_COLORS = {
    "Montreal": "#636EFA",
    "Toronto": "#EF553B",
    "Vancouver": "#00CC96",
}

st.set_page_config(
    page_title="Canadian Labour Market Dashboard", page_icon="🍁", layout="wide"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


df = load_data()

st.title("Canadian Labour Market Dashboard")
st.markdown(
    "Monthly labour force data for Montréal, Toronto, and Vancouver "
    "(Census Metropolitan Areas), seasonally adjusted, from Statistics Canada "
    "[Table 14-10-0460-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410046001). "
    "**Note:** 'Toronto' here is the Toronto CMA, StatCan's standard geography, "
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

#Implementing a set of quick view KPI cards at the top
is_rate = metric in RATE_METRICS
value_suffix = "%" if is_rate else "K"
delta_suffix = " pp" if is_rate else "K"

latest_date = filtered["date"].max()
sorted_dates = sorted(filtered["date"].unique())
prior_date = sorted_dates[-2] if len(sorted_dates) > 1 else None

st.caption(f"As of {latest_date.strftime('%B %Y')}")
cols = st.columns(len(cities))
for col, city in zip(cols, sorted(cities)):
    city_df = filtered[filtered["City"] == city]
    latest_row = city_df[city_df["date"] == latest_date]
    if latest_row.empty:
        continue
    latest_value = latest_row[metric].iloc[0]
    delta = None
    if prior_date is not None:
        prior_row = city_df[city_df["date"] == prior_date]
        if not prior_row.empty:
            delta = latest_value - prior_row[metric].iloc[0]
    col.metric(
        city,
        f"{latest_value:,.1f}{value_suffix}",
        f"{delta:+.1f}{delta_suffix}" if delta is not None else None,
        delta_color="inverse" if metric in {"unemployment_rate", "unemployment"} else "normal",
    )

st.subheader(f"{METRIC_LABELS[metric]}")
line_fig = px.line(
    filtered.sort_values("date"),
    x="date",
    y=metric,
    color="City",
    color_discrete_map=CITY_COLORS,
    labels={"date": "", metric: METRIC_LABELS[metric]},
)
line_fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FAFAFA",
    legend_title_text="",
    hovermode="x unified",
)
st.plotly_chart(line_fig, width="stretch")

st.subheader(f"{METRIC_LABELS[metric]} — most recent month in range")
st.caption(f"As of {latest_date.strftime('%B %Y')}")
latest = filtered[filtered["date"] == latest_date].sort_values("City")
bar_fig = px.bar(
    latest,
    x="City",
    y=metric,
    color="City",
    color_discrete_map=CITY_COLORS,
    labels={metric: METRIC_LABELS[metric]},
)
bar_fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FAFAFA",
    showlegend=False,
)
bar_fig.update_xaxes(title=None)
st.plotly_chart(bar_fig, width="stretch")


# 
# with st.expander("View underlying data"):
    # st.dataframe(
        # filtered[["date", "City", metric]].sort_values(["City", "date"]),
        # width="stretch",
    # )
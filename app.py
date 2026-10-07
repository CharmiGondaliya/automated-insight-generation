import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Automated Insight Generation",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Automated Insight Generation")
st.write(
    "An Auto-Analytics Engine for detecting trends, outliers, "
    "correlations and generating human-readable insights."
)

st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload Healthcare CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("dataset.csv")

st.subheader("Dataset Preview")

st.dataframe(
    df,
    use_container_width=True
)

st.subheader("Data Validation")

required_columns = [
    "month",
    "district",
    "anc_coverage",
    "institutional_delivery",
    "immunization",
    "high_risk_cases"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {missing_columns}"
    )
    st.stop()

st.success("All required columns are present.")

missing_values = df.isnull().sum()

st.write("Missing Values")

st.dataframe(
    missing_values.to_frame("Missing Count"),
    use_container_width=True
)

df["month"] = pd.to_datetime(df["month"])

df = df.sort_values(
    ["district", "month"]
)

indicators = [
    "anc_coverage",
    "institutional_delivery",
    "immunization",
    "high_risk_cases"
]

st.sidebar.header("Filters")

district_options = ["All"] + sorted(
    df["district"].unique().tolist()
)

selected_district = st.sidebar.selectbox(
    "District",
    district_options
)

month_options = ["All"] + sorted(
    df["month"].dt.strftime("%Y-%m").unique().tolist()
)

selected_month = st.sidebar.selectbox(
    "Month",
    month_options
)

indicator_options = ["All"] + indicators

selected_indicator = st.sidebar.selectbox(
    "Indicator",
    indicator_options
)

filtered_df = df.copy()

# District filter
if selected_district != "All":
    filtered_df = filtered_df[
        filtered_df["district"] == selected_district
    ]

# Month filter
if selected_month != "All":
    filtered_df = filtered_df[
        filtered_df["month"].dt.strftime("%Y-%m")
        == selected_month
    ]

# Indicator filter
if selected_indicator != "All":
    filtered_df = filtered_df[
        [
            "month",
            "district",
            selected_indicator
        ]
    ]

st.subheader("Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

st.sidebar.header("Analysis Configuration")

trend_threshold = st.sidebar.slider(
    "Trend Threshold (%)",
    min_value=1,
    max_value=50,
    value=10
)

def detect_trends(data, threshold):
    trends = []

    for district in data["district"].unique():

        district_data = data[
            data["district"] == district
        ].sort_values("month")

        for indicator in indicators:

            values = district_data[
                ["month", indicator]
            ].dropna()

            if len(values) < 2:
                continue

            previous = values.iloc[-2][indicator]
            current = values.iloc[-1][indicator]

            if previous == 0:
                continue

            change_pct = (
                (current - previous)
                / previous
            ) * 100

            if abs(change_pct) >= threshold:

                if abs(change_pct) >= threshold * 2:
                    severity = "High"
                else:
                    severity = "Medium"

                trends.append({
                    "type": "trend",
                    "indicator": indicator,
                    "entity": district,
                    "period": values.iloc[-1]["month"].strftime("%Y-%m"),
                    "value": current,
                    "prev_value": previous,
                    "change_pct": round(change_pct, 2),
                    "severity": severity,
                    "explanation": (
                        f"{indicator.replace('_', ' ').title()} "
                        f"in {district} changed by "
                        f"{change_pct:.1f}% compared to the "
                        f"previous month."
                    )
                })

    return pd.DataFrame(trends)

trend_results = detect_trends(
    df,
    trend_threshold
)

st.subheader("📈 Trend Detection")

if trend_results.empty:
    st.info("No significant trends detected.")
else:
    st.dataframe(
        trend_results,
        use_container_width=True
    )

outlier_method = st.sidebar.selectbox(
    "Outlier Method",
    ["IQR", "Z-score"]
)

z_threshold = st.sidebar.slider(
    "Z-score Threshold",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.5
)

def detect_outliers(data, method="IQR", z_threshold=3):

    outliers = []

    for month in sorted(data["month"].unique()):

        month_data = data[data["month"] == month]

        for indicator in indicators:

            values = month_data[indicator].dropna()

            if len(values) < 4:
                continue

            if method == "IQR":

                q1 = values.quantile(0.25)
                q3 = values.quantile(0.75)

                iqr = q3 - q1

                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                mask = (
                    (month_data[indicator] < lower) |
                    (month_data[indicator] > upper)
                )

            else:

                scores = np.abs(
                    zscore(values)
                )

                mask = pd.Series(
                    False,
                    index=month_data.index
                )

                mask.loc[values.index] = (
                    scores > z_threshold
                )

            detected = month_data[mask]

            for _, row in detected.iterrows():

                outliers.append({
                    "type": "outlier",
                    "indicator": indicator,
                    "entity": row["district"],
                    "period": row["month"].strftime("%Y-%m"),
                    "value": row[indicator],
                    "prev_value": np.nan,
                    "change_pct": np.nan,
                    "severity": "High",
                    "explanation": (
                        f"{indicator.replace('_', ' ').title()} "
                        f"for {row['district']} was identified "
                        f"as an outlier in "
                        f"{row['month'].strftime('%Y-%m')} "
                        f"using the {method} method."
                    )
                })

    return pd.DataFrame(outliers)

outlier_results = detect_outliers(
    df,
    outlier_method,
    z_threshold
)

st.subheader("🚨 Outlier Detection")

if outlier_results.empty:
    st.info("No outliers detected.")
else:
    st.dataframe(
        outlier_results,
        use_container_width=True
    )

correlation_threshold = st.sidebar.slider(
    "Correlation Threshold",
    min_value=0.50,
    max_value=1.00,
    value=0.70,
    step=0.05
)

def detect_correlations(data, threshold):

    correlation_matrix = data[
        indicators
    ].corr(method="pearson")

    correlations = []

    for i in range(len(indicators)):

        for j in range(i + 1, len(indicators)):

            indicator_1 = indicators[i]
            indicator_2 = indicators[j]

            correlation = correlation_matrix.loc[
                indicator_1,
                indicator_2
            ]

            if abs(correlation) >= threshold:

                if abs(correlation) >= 0.85:
                    severity = "High"
                else:
                    severity = "Medium"

                correlations.append({
                    "type": "correlation",
                    "indicator": (
                        f"{indicator_1}:{indicator_2}"
                    ),
                    "entity": "All Districts",
                    "period": "Overall",
                    "value": np.nan,
                    "prev_value": np.nan,
                    "change_pct": round(correlation, 3),
                    "severity": severity,
                    "explanation": (
                        f"{indicator_1.replace('_', ' ').title()} "
                        f"and {indicator_2.replace('_', ' ').title()} "
                        f"have a Pearson correlation of "
                        f"{correlation:.2f}."
                    )
                })

    return correlation_matrix, pd.DataFrame(correlations)

correlation_matrix, correlation_results = detect_correlations(
    df,
    correlation_threshold
)

st.subheader("🔗 Correlation Matrix")

st.dataframe(
    correlation_matrix.round(2),
    use_container_width=True
)

fig_heatmap = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    aspect="auto",
    title="Pearson Correlation Heatmap"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

insights = pd.concat(
    [
        trend_results,
        outlier_results,
        correlation_results
    ],
    ignore_index=True
)

if not insights.empty:
    insights.insert(
        0,
        "insight_id",
        [
            f"INS-{i:04d}"
            for i in range(
                1,
                len(insights) + 1
            )
        ]
    )

    # Create required assignment columns
    insights["metric"] = insights["value"]
    insights["change"] = insights["change_pct"]

    # Keep only the required insight fields
    insights = insights[
        [
            "insight_id",
            "type",
            "indicator",
            "entity",
            "period",
            "metric",
            "change",
            "severity",
            "explanation"
        ]
    ]



st.subheader("💡 Generated Insights")

if insights.empty:

    st.info(
        "No insights were generated using the current thresholds."
    )

else:

    st.dataframe(
        insights,
        use_container_width=True
    )

st.subheader("⚠️ Severity Summary")

if not insights.empty:

    severity_counts = (
        insights["severity"]
        .value_counts()
        .reset_index()
    )

    severity_counts.columns = [
        "severity",
        "count"
    ]

    fig = px.bar(
        severity_counts,
        x="severity",
        y="count",
        text="count",
        title="Insights by Severity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.subheader("📈 District Trend Visualization")

chart_indicator = st.selectbox(
    "Select Indicator for Line Chart",
    indicators
)

chart_data = df.copy()

fig_line = px.line(
    chart_data,
    x="month",
    y=chart_indicator,
    color="district",
    markers=True,
    title=f"{chart_indicator.replace('_', ' ').title()} by District"
)

st.plotly_chart(
    fig_line,
    use_container_width=True
)

if not insights.empty:

    csv_data = insights.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Insights CSV",
        data=csv_data,
        file_name="insights.csv",
        mime="text/csv"
    )

correlation_csv = (
    correlation_matrix
    .to_csv()
    .encode("utf-8")
)

st.download_button(
    label="⬇️ Download Correlation Matrix",
    data=correlation_csv,
    file_name="correlation_matrix.csv",
    mime="text/csv"
)


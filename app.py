import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import joblib
import os

BASE_DIR = os.path.dirname(__file__)

st.set_page_config(
    page_title="InventoryWise AI",
    page_icon="♻️",
    layout="wide"
)


# =========================================================
# CACHED DATA / MODEL LOADING
# =========================================================

@st.cache_data
def load_csv_data():
    sku_summary = pd.read_csv(
        os.path.join(BASE_DIR, "sku_summary.csv")
    )

    action_required = pd.read_csv(
        os.path.join(BASE_DIR, "action_required.csv")
    )

    scenario_inventory = pd.read_csv(
        os.path.join(BASE_DIR, "scenario_inventory.csv")
    )

    return sku_summary, action_required, scenario_inventory


@st.cache_resource
def load_model():
    return joblib.load(
        os.path.join(
            BASE_DIR,
            "demand_forecasting_model.pkl"
        )
    )


sku_summary, action_required, scenario_inventory = load_csv_data()

# Human-readable product names for the dashboard
category_display_names = {
    "ReadyMeal": "Ready Meal",
    "SnackBar": "Snack Bar"
}

sku_to_category = (
    scenario_inventory.groupby("sku")["category"]
    .first()
    .to_dict()
)

def product_label(sku):
    category = sku_to_category.get(sku, "Product")
    category = category_display_names.get(category, category)
    return f"{category} — {sku}"

promo_model = load_model()

forecast_history = pd.read_csv("forecast_history.csv")
forecast_history["date"] = pd.to_datetime(
    forecast_history["date"]
)

sku_features = [
    c for c in promo_model.feature_names_in_
    if c.startswith("sku_")
]

sku_promo_features = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
    "day_of_week",
    "promotion_flag"
] + sku_features

daily_sales_promo = forecast_history.copy()


# =========================================================
# AI FORECAST
# =========================================================

@st.cache_data
def forecast_demand(sku, days, promotion_flag):

    history = (
        daily_sales_promo[
            daily_sales_promo["sku"] == sku
        ]
        .sort_values("date")
        .copy()
    )

    sales_history = history["units_sold"].tolist()
    date_history = history["date"].tolist()

    forecasts = []

    for _ in range(days):

        next_date = (
            date_history[-1]
            + pd.Timedelta(days=1)
        )

        lag_1 = sales_history[-1]
        lag_7 = sales_history[-7]

        rolling_mean_7 = np.mean(
            sales_history[-7:]
        )

        rolling_mean_14 = np.mean(
            sales_history[-14:]
        )

        day_of_week = next_date.dayofweek

        input_data = pd.DataFrame([{
            "lag_1": lag_1,
            "lag_7": lag_7,
            "rolling_mean_7": rolling_mean_7,
            "rolling_mean_14": rolling_mean_14,
            "day_of_week": day_of_week,
            "promotion_flag": promotion_flag
        }])

        for sku_col in sku_features:
            input_data[sku_col] = 0

        input_data["sku_" + sku] = 1

        input_data = input_data[
            sku_promo_features
        ]

        prediction = float(
            promo_model.predict(input_data)[0]
        )

        prediction = max(0, prediction)

        forecasts.append({
            "date": next_date,
            "predicted_demand": prediction
        })

        sales_history.append(prediction)
        date_history.append(next_date)

    return pd.DataFrame(forecasts)


# =========================================================
# DASHBOARD CALCULATIONS
# =========================================================

total_inventory = scenario_inventory[
    "scenario_inventory"
].sum()

potential_surplus = scenario_inventory[
    "potential_surplus"
].sum()

at_risk_batches = (
    scenario_inventory[
        "potential_surplus"
    ] > 0
).sum()

critical_high_risk = scenario_inventory[
    scenario_inventory["waste_risk"].isin(
        ["Critical", "High Risk"]
    )
].shape[0]

surplus_exposure = (
    potential_surplus /
    total_inventory *
    100
    if total_inventory > 0
    else 0
)


# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("♻️ InventoryWise AI")

st.subheader(
    "AI-Powered Perishable Inventory Waste Prevention System"
)
st.write(
    "Demand forecasting + shelf-life analysis + "
    "explainable intervention support"
)

st.divider()


# =========================================================
# KPI DASHBOARD
# =========================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Scenario Inventory",
        f"{total_inventory:,.0f} units"
    )

with c2:
    st.metric(
        "Potential Surplus",
        f"{potential_surplus:,.2f} units"
    )

with c3:
    st.metric(
        "At-Risk Batches",
        f"{at_risk_batches}"
    )

with c4:
    st.metric(
        "Critical / High Risk",
        f"{critical_high_risk}"
    )

with c5:
    st.metric(
        "Surplus Exposure",
        f"{surplus_exposure:.2f}%"
    )

st.caption(
    "Prototype scenario metrics — not measured "
    "real-world food waste."
)

st.divider()


# =========================================================
# CHARTS
# =========================================================

left, right = st.columns(2)

with left:

    st.subheader("Risk Overview")

    risk_counts = (
        scenario_inventory["waste_risk"]
        .value_counts()
        .reindex(
            [
                "Critical",
                "High Risk",
                "Medium Risk",
                "Low Risk",
                "No Risk"
            ],
            fill_value=0
        )
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "SKU Count"
    ]

    fig = px.bar(
        risk_counts,
        x="Risk Level",
        y="SKU Count",
        title="SKU Waste-Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with right:

    st.subheader("Potential Surplus")

    surplus_chart = (
        scenario_inventory[
            scenario_inventory[
                "potential_surplus"
            ] > 0
        ]
        .groupby(
            "sku",
            as_index=False
        )["potential_surplus"]
        .sum()
        .sort_values(
            "potential_surplus",
            ascending=False
        )
    )
    surplus_chart["product"] = surplus_chart["sku"].map(product_label)

    fig2 = px.bar(
        surplus_chart,
        x="product",
        y="potential_surplus",
        title="Potential Surplus by At-Risk SKU"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


st.divider()


# =========================================================
# ACTION CENTER
# =========================================================

st.header("⚠️ Action Center")

if action_required.empty:

    st.success(
        "No immediate intervention required."
    )

else:

    for _, row in action_required.iterrows():

        risk = row["waste_risk"]

        if risk == "Critical":
            box = st.error

        elif risk == "High Risk":
            box = st.warning

        else:
            box = st.info

        box(
            f'{product_label(row["sku"])} — {risk}'
        )

        a, b, c, d = st.columns(4)

        with a:
            st.metric(
                "Inventory",
                f'{row["total_inventory"]:,.0f}'
            )

        with b:
            st.metric(
                "Potential Surplus",
                f'{row["potential_surplus"]:.2f}'
            )

        with c:
            st.metric(
                "Shelf Life",
                f'{row["shortest_shelf_life_days"]} day(s)'
            )

        with d:
            st.metric(
                "Priority",
                f'{row["highest_priority_score"]:.2f}'
            )

        st.write(
            f'**Recommended action:** '
            f'{row["recommended_action"]}'
        )

        st.divider()


# =========================================================
# PRODUCT ANALYSIS
# =========================================================

st.header("🔎 Product Analysis")

sku_list = sorted(
    scenario_inventory["sku"].unique()
)

selected_sku = st.selectbox(
    "Select a Product",
    sku_list,
    format_func=product_label
)

st.caption(
    f"Currently analyzing: **{product_label(selected_sku)}**"
)

selected_sku_data = scenario_inventory[
    scenario_inventory["sku"] == selected_sku
].copy()


p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric(
        "Scenario Inventory",
        f'{selected_sku_data["scenario_inventory"].sum():,.0f}'
    )

with p2:
    st.metric(
        "Potential Surplus",
        f'{selected_sku_data["potential_surplus"].sum():.2f}'
    )

with p3:
    st.metric(
        "Shortest Shelf Life",
        f'{selected_sku_data["remaining_shelf_life_days"].min()} day(s)'
    )

with p4:
    st.metric(
        "Risk",
        selected_sku_data[
            "waste_risk"
        ].iloc[0]
    )


# =========================================================
# AI DEMAND FORECAST
# =========================================================

st.subheader("🤖 AI Demand Forecast")

forecast_batch = st.selectbox(
    "Select batch for forecast horizon",
    selected_sku_data["batch_id"].tolist()
)

batch_row = selected_sku_data[
    selected_sku_data["batch_id"] ==
    forecast_batch
].iloc[0]

forecast_days = int(
    batch_row["remaining_shelf_life_days"]
)


# Use the same promotion assumption as
# the original batch forecasting logic:
latest_promotion = int(
    daily_sales_promo[
        daily_sales_promo["sku"] ==
        selected_sku
    ]
    .sort_values("date")
    ["promotion_flag"]
    .iloc[-1]
)


forecast_df = forecast_demand(
    selected_sku,
    forecast_days,
    latest_promotion
)

total_forecast = (
    forecast_df["predicted_demand"]
    .sum()
)


f1, f2, f3 = st.columns(3)

with f1:
    st.metric(
        "Forecast Horizon",
        f"{forecast_days} day(s)"
    )

with f2:
    st.metric(
        "Expected Sales",
        f"{total_forecast:.2f} units"
    )

with f3:
    st.metric(
        "Average Daily Forecast",
        f"{forecast_df['predicted_demand'].mean():.2f} units"
    )


forecast_chart = px.line(
    forecast_df,
    x="date",
    y="predicted_demand",
    markers=True,
    title="Random Forest Predicted Daily Demand"
)

st.plotly_chart(
    forecast_chart,
    use_container_width=True
)

st.caption(
    "AI model: Random Forest regression trained on "
    "historical FMCG sales using lagged demand, "
    "rolling demand, day-of-week, SKU identity and "
    "promotion status."
)


# =========================================================
# BATCH-LEVEL REASONING
# =========================================================

st.subheader("Batch-Level Reasoning")

display_columns = [
    "batch_id",
    "scenario_inventory",
    "remaining_shelf_life_days",
    "forecast_daily_demand",
    "expected_sales_before_expiry",
    "potential_surplus",
    "surplus_percentage",
    "waste_risk",
    "recommended_action"
]

st.dataframe(
    selected_sku_data[display_columns],
    use_container_width=True
)


# =========================================================
# DECISION LOGIC
# =========================================================

st.subheader(
    "How the Decision Is Calculated"
)

st.info("""
1. **AI demand forecast** — Random Forest forecasts
near-term demand from historical sales patterns,
recent demand, day-of-week behaviour, SKU identity
and promotion status.

2. **Expected sales before expiry** — the forecast is
projected across the remaining shelf-life window.

3. **Potential surplus** — scenario inventory minus
expected sales before expiry.

4. **Waste risk** — surplus exposure is considered
together with remaining shelf life.

5. **Intervention recommendation** — the system
produces a recommendation that a human inventory
manager can review.
""")


# =========================================================
# RESPONSIBLE AI
# =========================================================

st.divider()

st.header(
    "ℹ️ Prototype Scope & Responsible AI"
)

st.write(
    "This is a prototype decision-support system "
    "using synthetic/public benchmark FMCG sales data. "
    "Product shelf-life and batch inventory exposure "
    "are simulated for demonstration because the "
    "source dataset does not contain real batch-level "
    "expiry records."
)

st.write(
    "The AI component forecasts demand; it does not "
    "directly predict food waste. Recommendations are "
    "decision support and should be verified by a human "
    "operator before operational use."
)

st.write(
    "**Primary SDG:** SDG 12 — Responsible Consumption "
    "and Production"
)

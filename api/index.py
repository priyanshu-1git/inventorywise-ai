from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import joblib

app = FastAPI(
    title="InventoryWise AI",
    description="AI-Powered Perishable Inventory Waste Prevention System",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# =========================================================
# LOAD DATA
# =========================================================

def load_data():
    sku_summary = pd.read_csv(
        os.path.join(BASE_DIR, "sku_summary.csv")
    )

    action_required = pd.read_csv(
        os.path.join(BASE_DIR, "action_required.csv")
    )

    scenario_inventory = pd.read_csv(
        os.path.join(BASE_DIR, "scenario_inventory.csv")
    )

    forecast_history = pd.read_csv(
        os.path.join(BASE_DIR, "forecast_history.csv")
    )

    forecast_history["date"] = pd.to_datetime(
        forecast_history["date"]
    )

    return (
        sku_summary,
        action_required,
        scenario_inventory,
        forecast_history
    )


# =========================================================
# LOAD MODEL
# =========================================================

def load_model():
    return joblib.load(
        os.path.join(
            BASE_DIR,
            "demand_forecasting_model.pkl"
        )
    )


sku_summary, action_required, scenario_inventory, forecast_history = load_data()




# =========================================================
# BASIC PRODUCT LABEL
# =========================================================

category_display_names = {
    "ReadyMeal": "Ready Meal",
    "SnackBar": "Snack Bar"
}


sku_to_category = (
    scenario_inventory
    .groupby("sku")["category"]
    .first()
    .to_dict()
)


def product_label(sku):
    category = sku_to_category.get(sku, "Product")
    category = category_display_names.get(
        category,
        category
    )

    return f"{category} — {sku}"


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "name": "InventoryWise AI",
        "description": "AI-Powered Perishable Inventory Waste Prevention System",
        "status": "online"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        
    }


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@app.get("/api/summary")
def summary():

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

    return {
        "total_inventory": float(total_inventory),
        "potential_surplus": float(potential_surplus),
        "at_risk_batches": int(at_risk_batches),
        "critical_high_risk": int(critical_high_risk),
        "surplus_exposure": float(surplus_exposure)
    }


# =========================================================
# PRODUCTS
# =========================================================

@app.get("/api/products")
def products():

    products = []

    for sku in sorted(
        scenario_inventory["sku"].unique()
    ):
        products.append({
            "sku": sku,
            "name": product_label(sku)
        })

    return products


# =========================================================
# ACTION CENTER
# =========================================================

@app.get("/api/actions")
def actions():

    return action_required.to_dict(
        orient="records"
    )
# =========================================================
# DEMAND FORECAST
# =========================================================

from datetime import timedelta
import numpy as np


@app.get("/api/forecast/{sku}")
def forecast(sku: str, days: int = 5, promotion_flag: int = 0):

    if sku not in forecast_history["sku"].unique():
        return {
            "error": f"Unknown SKU: {sku}"
        }

    if days < 1 or days > 30:
        return {
            "error": "Days must be between 1 and 30."
        }

    # Load the model only when forecasting is requested
    model = load_model()

    history = (
        forecast_history[
            forecast_history["sku"] == sku
        ]
        .sort_values("date")
        .copy()
    )

    sales_history = history["units_sold"].tolist()
    date_history = history["date"].tolist()

    # Get the exact SKU feature columns expected by the model
    sku_features = [
        c for c in model.feature_names_in_
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

        sku_column = "sku_" + sku

        if sku_column in input_data.columns:
            input_data[sku_column] = 1

        input_data = input_data[
            sku_promo_features
        ]

        prediction = float(
            model.predict(input_data)[0]
        )

        prediction = max(
            0,
            prediction
        )

        forecasts.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "predicted_demand": prediction
        })

        sales_history.append(prediction)
        date_history.append(next_date)

    total_forecast = sum(
        item["predicted_demand"]
        for item in forecasts
    )

    return {
        "sku": sku,
        "days": days,
        "promotion_flag": promotion_flag,
        "total_forecast": total_forecast,
        "forecast": forecasts
    }
# =========================================================
# INVENTORY DATA
# =========================================================

@app.get("/api/inventory")
def inventory():

    records = scenario_inventory.to_dict(
        orient="records"
    )

    return records


# =========================================================
# PRODUCT ANALYSIS
# =========================================================

@app.get("/api/product/{sku}")
def product_analysis(sku: str):

    product_data = scenario_inventory[
        scenario_inventory["sku"] == sku
    ]

    if product_data.empty:
        return {
            "error": f"Unknown SKU: {sku}"
        }

    return {
        "sku": sku,
        "records": product_data.to_dict(
            orient="records"
        )
    }


# =========================================================
# RISK OVERVIEW
# =========================================================

@app.get("/api/risk-overview")
def risk_overview():

    risk_counts = (
        scenario_inventory["waste_risk"]
        .value_counts()
        .to_dict()
    )

    return {
        "risk_distribution": {
            str(key): int(value)
            for key, value in risk_counts.items()
        }
    }


# =========================================================
# SURPLUS BY SKU
# =========================================================

@app.get("/api/surplus-overview")
def surplus_overview():

    surplus = (
        scenario_inventory
        .groupby(
            ["sku", "category"],
            as_index=False
        )["potential_surplus"]
        .sum()
        .sort_values(
            "potential_surplus",
            ascending=False
        )
    )

    return surplus.to_dict(
        orient="records"
    )
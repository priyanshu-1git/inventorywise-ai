# ♻️ InventoryWise AI

### AI-Powered Perishable Inventory Waste Prevention System

> A prototype decision-support system that combines **AI demand
> forecasting**, **inventory analysis**, and **shelf-life reasoning** to
> identify potential perishable inventory surplus before expiry and
> surface interpretable intervention suggestions for human review.

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Machine
Learning](https://img.shields.io/badge/AI-Machine%20Learning-purple)](https://scikit-learn.org/)
[![Scikit-learn](https://img.shields.io/badge/Library-Scikit--learn-orange)](https://scikit-learn.org/)
[![Random
Forest](https://img.shields.io/badge/Model-Random%20Forest-green)](https://scikit-learn.org/stable/modules/ensemble.html#random-forests)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly-blue)](https://plotly.com/)
[![Vercel](https://img.shields.io/badge/Deployment-Vercel-black)](https://vercel.com/)
[![SDG
12](https://img.shields.io/badge/SDG-12%20Responsible%20Consumption-orange)](https://sdgs.un.org/goals/goal12)
[![Status](https://img.shields.io/badge/Status-Prototype-yellow)]()

🔗 **Live Demo:** https://inventorywise-ai.vercel.app/

📦 **Source Code:** https://github.com/priyanshu-1git/inventorywise-ai

📄 **Responsible AI & data disclosure:**
[RESPONSIBLE_AI.md](./RESPONSIBLE_AI.md)

------------------------------------------------------------------------

## 📌 Table of Contents

-   [Problem](#-problem)
-   [Solution](#-solution)
-   [How It Works](#️-how-it-works)
-   [AI Component](#-ai-component)
-   [Decision Logic](#-decision-logic)
-   [Dashboard Features](#-dashboard-features)
-   [Example Scenario](#-example-scenario)
-   [Technology Stack](#️-technology-stack)
-   [Dataset](#-dataset)
-   [Model Evaluation](#-model-evaluation)
-   [System Architecture](#️-system-architecture)
-   [Repository Structure](#-repository-structure)
-   [Getting Started](#-getting-started)
-   [Deployment](#-deployment)
-   [Limitations & Responsible AI](#️-limitations--responsible-ai)
-   [Future Improvements](#-future-improvements)
-   [SDG Alignment](#-sdg-alignment)
-   [Contributing](#-contributing)
-   [License](#-license)

------------------------------------------------------------------------

## 🌍 Problem

Perishable products such as milk, yogurt, juice, and ready meals have a
limited shelf life. When inventory exceeds the quantity likely to be
sold before expiry, products can become potential waste.

Traditional inventory monitoring can show current stock and historical
sales, but it does not directly answer:

> **"How much of this inventory is likely to remain unsold before
> expiry?"**

InventoryWise AI is designed as a prototype decision-support workflow
for surfacing that risk earlier.

------------------------------------------------------------------------

## 💡 Solution

InventoryWise AI combines:

-   **AI-based demand forecasting**
-   **Current inventory information**
-   **Remaining shelf-life information**
-   **Potential surplus calculation**
-   **Risk classification**
-   **Interpretable intervention recommendations**

The AI model forecasts expected product demand. A downstream decision
layer then compares expected sales during the remaining shelf-life
period with at-risk inventory.

This distinction is important: **the machine-learning model predicts
demand, not food waste directly.**

------------------------------------------------------------------------

## ⚙️ How It Works

``` mermaid
flowchart LR
    A[Historical Sales] --> B[Feature Engineering]
    B --> C[AI Demand Forecast]
    C --> D[Expected Sales Before Expiry]

    E[Inventory] --> F[Potential Surplus]
    G[Remaining Shelf Life] --> D
    D --> F

    F --> H[Waste Risk Assessment]
    H --> I[Recommended Intervention]
    I --> J[Human Inventory Manager]
```

### Decision workflow

1.  **Historical Sales** --- daily sales are organized by SKU.
2.  **Feature Engineering** --- lag demand, rolling averages,
    day-of-week, promotion status, and SKU identity are used as model
    inputs.
3.  **AI Demand Forecast** --- a Random Forest regression model
    estimates future daily demand.
4.  **Expected Sales Before Expiry** --- forecasted demand is combined
    with the remaining shelf-life period.
5.  **Potential Surplus** --- inventory is compared with expected sales
    before expiry.
6.  **Risk Classification** --- surplus exposure and remaining shelf
    life are used to classify the scenario.
7.  **Recommended Intervention** --- the system surfaces an
    interpretable suggestion for human review.

------------------------------------------------------------------------

## 🤖 AI Component

### Demand Forecasting Model

**Model:** Random Forest Regressor

The model is trained to forecast **daily product demand**. It does not
directly predict food waste.

### Features

  Feature             Description
  ------------------- -----------------------------------------
  `lag_1`             Previous day's sales
  `lag_7`             Sales from the previous week
  `rolling_mean_7`    Average sales over the previous 7 days
  `rolling_mean_14`   Average sales over the previous 14 days
  `day_of_week`       Day-of-week demand pattern
  `promotion_flag`    Whether the product was under promotion
  SKU features        Product-specific demand patterns

The deployed forecasting endpoint performs recursive multi-day
forecasting using the latest available historical context.

### Forecast assumptions

For future forecast dates, promotion status can be supplied as an input
to the forecasting endpoint. The prototype therefore supports a simple
promotion/no-promotion scenario rather than claiming to forecast future
promotions automatically.

------------------------------------------------------------------------

## 🧠 Decision Logic

The system converts forecasted demand into a potential-surplus signal:

``` text
Expected Sales Before Expiry
    = Forecasted Daily Demand × Remaining Shelf-Life Days

Potential Surplus
    = Inventory − Expected Sales Before Expiry

Potential Surplus
    = max(Potential Surplus, 0)
```

The resulting surplus exposure is then interpreted together with
remaining shelf life.

### Risk categories

  -----------------------------------------------------------------------
  Risk Level                          Interpretation
  ----------------------------------- -----------------------------------
  🔴 Critical                         Significant surplus exposure with
                                      very little shelf life remaining

  🟠 High Risk                        Meaningful surplus exposure with
                                      limited shelf life

  🟡 Medium Risk                      Moderate surplus exposure requiring
                                      monitoring

  🔵 Low Risk                         Lower surplus exposure that can be
                                      monitored

  🟢 No Risk                          No immediate potential surplus
                                      identified
  -----------------------------------------------------------------------

Depending on the scenario, the system may suggest:

-   FEFO (First Expired, First Out) prioritization
-   short-term markdown/promotion review
-   closer demand monitoring
-   redistribution or donation consideration if surplus remains

**Recommendations are decision-support outputs for human review. The
prototype does not automatically execute inventory actions.**

------------------------------------------------------------------------

## 📊 Dashboard Features

The current web dashboard provides the following sections:

### Overview

-   Total/simulated inventory
-   Potential surplus exposure
-   At-risk batch count
-   Critical/high-risk count
-   Surplus exposure percentage

### Risk Overview

Visualizes the distribution of simulated batches across risk categories.

### Potential Surplus

Highlights SKUs with potential surplus exposure based on the decision
layer.

### Action Center

Surfaces batches requiring attention and provides an interpretable
recommended intervention.

### Product Analysis

Provides product-level inventory, shelf-life, demand, surplus, and risk
information.

### AI Demand Forecast

Allows a user to:

-   select a product
-   choose a forecast horizon
-   toggle promotion status
-   generate a multi-day demand forecast
-   inspect the predicted demand trend

### Batch-Level Reasoning

Shows the underlying inventory/shelf-life reasoning for individual
batches, including expected sales, potential surplus, risk, and
recommended action.

### Responsible AI

Documents the prototype scope, data limitations, simulated inventory
layer, and the distinction between demand forecasting and food-waste
prediction.

------------------------------------------------------------------------

## 🧪 Example Scenario

A simulated **Ready Meal --- RE-004** batch illustrates the decision
logic:

  Variable                           Value
  ------------------------- --------------
  Inventory                      264 units
  Remaining shelf life               1 day
  Forecasted daily demand     164.86 units
  Potential surplus            99.14 units
  Surplus exposure                 ≈37.55%

``` text
Expected sales before expiry = 164.86 × 1
                             = 164.86 units

Potential surplus            = 264 − 164.86
                             = 99.14 units

Surplus percentage           = 99.14 / 264 × 100
                             ≈ 37.55%
```

**Result:** The simulated scenario is classified as **Critical** because
substantial inventory remains relative to expected sales with only one
day of shelf life remaining.

A corresponding intervention can include immediate FEFO prioritization
and a short-term markdown/promotion review.

> ⚠️ This is a simulated prototype scenario, not real retailer data and
> not a measured food-waste reduction result.

------------------------------------------------------------------------

## 🛠️ Technology Stack

### Data & Machine Learning

-   Python
-   Pandas
-   NumPy
-   Scikit-learn
-   Random Forest Regression
-   Joblib

### Backend

-   FastAPI
-   Uvicorn
-   REST-style JSON API endpoints

### Frontend & Visualization

-   HTML
-   CSS
-   JavaScript
-   Plotly

### Data & Model Assets

-   CSV-based prototype datasets
-   Serialized Random Forest model (`.pkl`)
-   Git LFS for the trained model artifact

### Development & Deployment

-   Google Colab / Python development environment
-   Git
-   GitHub
-   Vercel

> The project originally had a Streamlit prototype. The current live
> deployment uses a FastAPI backend with a static web frontend on
> Vercel.

------------------------------------------------------------------------

## 📁 Dataset

**FMCG Daily Sales Data (2022--2024)**\
https://www.kaggle.com/datasets/beatafaron/fmcg-daily-sales-data-to-2022-2024

The dataset contains historical FMCG sales information used for demand
forecasting.

The source data does **not** provide the complete batch-level expiry
information required for the waste-risk layer. Therefore, the prototype
adds a simulated inventory/batch/shelf-life scenario for demonstrating
the downstream decision logic.

This limitation is intentional and documented in
[RESPONSIBLE_AI.md](./RESPONSIBLE_AI.md).

------------------------------------------------------------------------

## 📈 Model Evaluation

The forecasting dataset is split chronologically to avoid using future
observations for model training:

-   **Training period:** 2022--2023
-   **Test period:** 2024
-   **Evaluation metric:** Mean Absolute Error (MAE)

The SKU-aware Random Forest benchmark achieved approximately:

> **MAE ≈ 27.08 units**

on the 2024 test period.

This should be interpreted as a **prototype benchmark on the selected
dataset**, not as evidence of production-level forecasting accuracy.

------------------------------------------------------------------------

## 🏗️ System Architecture

The current application separates the user interface from the prediction
and data APIs:

``` text
┌─────────────────────────────────────┐
│       InventoryWise AI Web UI       │
│      HTML + CSS + JavaScript        │
│              Plotly                 │
└──────────────────┬──────────────────┘
                   │
                   │ HTTP / JSON
                   ▼
┌─────────────────────────────────────┐
│          FastAPI Backend             │
│                                     │
│  Summary   Products   Actions       │
│  Forecast  Inventory  Risk APIs     │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌─────────────────┐   ┌────────────────────┐
│ CSV Data Assets │   │ Random Forest Model│
│                 │   │       .pkl         │
└─────────────────┘   └────────────────────┘
```

### Forecast request flow

``` text
User selects SKU
       ↓
Forecast API request
       ↓
Historical SKU data loaded
       ↓
Feature construction
       ↓
Random Forest prediction
       ↓
Recursive multi-day forecast
       ↓
JSON response
       ↓
Plotly forecast chart
```

------------------------------------------------------------------------

## 📂 Repository Structure

``` text
inventorywise-ai/
│
├── api/
│   └── index.py                   # FastAPI application and API endpoints
│
├── static/
│   └── index.html                 # InventoryWise AI web dashboard
│
├── demand_forecasting_model.pkl   # Trained Random Forest model
├── forecast_history.csv           # Historical sales data used by forecasting
├── scenario_inventory.csv         # Simulated inventory/batch/shelf-life scenarios
├── sku_summary.csv                # SKU-level inventory/risk summary
├── action_required.csv            # Batches requiring attention
│
├── app.py                         # Original Streamlit prototype
├── requirements.txt               # Python dependencies
├── README.md
├── RESPONSIBLE_AI.md              # Responsible AI, limitations & data disclosure
├── LICENSE
└── .gitattributes                 # Git LFS configuration
```

> The original `app.py` Streamlit implementation is retained as part of
> the project's development history. The current live application is
> served through the FastAPI + static frontend architecture.

------------------------------------------------------------------------

<details>
<summary><strong>🧰 Getting Started — Run Locally</strong></summary>

### 1. Clone the repository

``` bash
git clone https://github.com/priyanshu-1git/inventorywise-ai.git
cd inventorywise-ai
```

### 2. Install dependencies

``` bash
pip install -r requirements.txt
```

### 3. Pull the Git LFS model

``` bash
git lfs pull
```

### 4. Run the FastAPI application

``` bash
uvicorn api.index:app --reload
```

The API will be available at:

``` text
http://127.0.0.1:8000
```

The dashboard is available at:

``` text
http://127.0.0.1:8000/
```

### Useful API endpoints

``` text
GET /api/health
GET /api/summary
GET /api/products
GET /api/actions
GET /api/inventory
GET /api/risk-overview
GET /api/surplus-overview
GET /api/product/{sku}
GET /api/forecast/{sku}
```

Example:

``` text
GET /api/forecast/RE-004?days=5&promotion_flag=0
```

------------------------------------------------------------------------

## 🚀 Deployment

The current production deployment is hosted on **Vercel**.

### Production architecture

``` text
GitHub
   ↓
Vercel Deployment
   ↓
FastAPI serverless backend + static frontend
   ↓
InventoryWise AI dashboard
```

### Live application

**https://inventorywise-ai.vercel.app/**

The trained model is stored using **Git LFS**, allowing the deployment
to retrieve the model artifact required by the forecasting endpoint.

------------------------------------------------------------------------

## ⚠️ Limitations & Responsible AI

InventoryWise AI is an **educational/prototype decision-support
system**, not a production inventory-management platform.

### Current limitations

-   The historical sales data is public/synthetic benchmark data.
-   The source dataset does not contain complete batch-level expiry
    information.
-   Inventory, batch, and shelf-life values used by the risk layer are
    simulated.
-   Future promotion status is provided as a simple scenario input.
-   The model forecasts demand; it does **not** directly predict food
    waste.
-   Forecast accuracy depends on the characteristics and quality of the
    available historical data.
-   The prototype has not been validated in a live supermarket or
    warehouse environment.
-   Recommendations are advisory and require human verification.
-   No claim is made that the prototype has prevented real food waste or
    generated real financial savings.

For the complete transparency and data disclosure, see
[RESPONSIBLE_AI.md](./RESPONSIBLE_AI.md).

------------------------------------------------------------------------

## 🔮 Future Improvements

-   **Real-time inventory integration** --- connect to POS/warehouse
    systems instead of simulated inventory.
-   **Real batch-level expiry data** --- use batch IDs, production
    dates, and expiry dates.
-   **Advanced forecasting** --- evaluate Gradient Boosting, XGBoost,
    LightGBM, or deep-learning time-series models.
-   **Promotion-aware forecasting** --- incorporate discount percentage,
    promotion duration, and price elasticity.
-   **Multi-store optimization** --- identify opportunities to
    redistribute at-risk inventory between locations.
-   **Automated monitoring** --- continuously detect batches entering
    high-risk status.
-   **Improved uncertainty estimation** --- provide prediction intervals
    alongside point forecasts.
-   **Model monitoring** --- track forecasting error and model drift
    over time.

------------------------------------------------------------------------

## 🌱 SDG Alignment

InventoryWise AI is aligned with **UN Sustainable Development Goal 12:
Responsible Consumption and Production**.

The prototype demonstrates an earlier-intervention workflow by
attempting to flag potential perishable inventory surplus **before
expiry**, rather than only identifying waste after it occurs.

It does **not** claim measured real-world waste reduction.

------------------------------------------------------------------------

## 🤝 Contributing

Contributions are welcome.

1.  Fork the repository.
2.  Create a feature branch:

``` bash
git checkout -b feature/your-feature
```

3.  Make your changes.
4.  Commit the changes:

``` bash
git add .
git commit -m "Describe your change"
```

5.  Push the branch:

``` bash
git push origin feature/your-feature
```

6.  Open a pull request describing what you changed and why.

------------------------------------------------------------------------

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

------------------------------------------------------------------------

### 🔗 Project Links

-   **Live Demo:** https://inventorywise-ai.vercel.app/
-   **Source Code:** https://github.com/priyanshu-1git/inventorywise-ai
-   **Responsible AI:** [RESPONSIBLE_AI.md](./RESPONSIBLE_AI.md)

⭐ If you find the project interesting, consider giving the repository a
star.

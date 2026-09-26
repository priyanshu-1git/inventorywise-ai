# 🛡️ Responsible AI & Data Disclosure — WasteWise AI

This document covers the transparency, oversight, and data-limitation details behind WasteWise AI in full. The main [README](./README.md) links here rather than repeating it.

---

## 🔍 Transparency

The system keeps six stages clearly separated so the reasoning stays inspectable:

1. AI demand forecasting
2. Inventory calculations
3. Shelf-life assumptions
4. Surplus calculations
5. Risk classification
6. Recommended actions

---

## 👤 Human Oversight

The system does **not** automatically apply discounts, change inventory levels, redistribute or donate products, or place purchase orders. Every recommendation is intended for review by a human inventory manager.

---

## 📊 Data Limitations

The prototype uses synthetic/public benchmark sales data ([FMCG Daily Sales Data, Kaggle](https://www.kaggle.com/datasets/beatafaron/fmcg-daily-sales-data-to-2022-2024)), which includes date, SKU, brand, segment, category, channel, region, pack type, unit price, promotion flag, delivery days, stock availability, delivered quantity, and units sold — but **no reliable batch-level expiry information**.

A real deployment would additionally require: batch-level inventory, actual expiration dates, product-level sales history, promotion information, and store/channel-level inventory.

---

## ⚠️ Prototype Assumptions

Because the source dataset lacks batch-level expiry data, the current prototype introduces a **simulated inventory and shelf-life scenario layer** on top of the real historical sales data. These simulated values are explicitly separated from the historical data and are not presented as real inventory measurements.

---

## 🚫 Avoiding Overclaiming

The prototype does **not** claim to have:

- Prevented actual food waste
- Generated actual financial savings
- Operated in a real supermarket
- Predicted food waste directly (it predicts *demand*; waste risk is derived downstream)

It demonstrates how AI-assisted demand forecasting can support **earlier identification** of potential perishable inventory surplus — a decision-support concept, not a verified outcome.

---

## 🎯 Scope

Current focus: perishable FMCG categories (milk, yogurt, juice, ready meals, snacks) as a **proof-of-concept**, not a production-ready retail platform. The same architecture could extend to other perishable categories and real operational systems in the future.

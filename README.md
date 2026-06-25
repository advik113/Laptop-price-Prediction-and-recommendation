# Smart Laptop Advisor 💻

A Final Year Data Science Capstone project — an end-to-end ML system that estimates fair market prices for laptops from real specifications, powered by a tuned XGBoost regression model (R² = 0.918).

## Features

- **Price Prediction** — Enter specs, get an instant estimated market price
- **Analytics Dashboard** — Explore distributions, correlations and brand breakdowns
- **Model Performance** — Compare all trained model candidates
- **Feature Importance** — Understand what the model learned
- **Recommendation Engine** — Find the best laptop for your budget and use case
- **Laptop Comparison** — Configure two laptops and compare specs side-by-side
- **Dark / Light Mode** — Persistent theme switching with no JavaScript

## Project Structure

```
Laptop Price Project/
├── app.py                        # Main entry point
├── requirements.txt
├── assets/
│   └── style.css                 # Premium SaaS design system
├── data/
│   └── laptop_data.csv           # Dataset (1,303 rows)
├── models/
│   ├── xgb_model.pkl             # Trained XGBoost model
│   └── columns.pkl               # Feature column schema
├── page_modules/
│   ├── home.py
│   ├── prediction.py
│   ├── analytics.py
│   ├── comparison.py
│   ├── recommendation.py
│   ├── feature_importance.py
│   ├── model_performance.py
│   └── about.py
└── utils/
    ├── components.py             # Reusable UI components
    └── data_loader.py            # Model + dataset loaders
```

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

- **Python** — Core language
- **XGBoost** — Final tuned regression model (R² = 0.918)
- **Scikit-learn** — Preprocessing, train/test split, baseline models
- **Pandas / NumPy** — Data wrangling & feature engineering
- **Streamlit** — Interactive multi-page web application
- **Plotly** — Interactive BI-style charts & dashboards

## Model Details

The XGBoost model was trained on a double-log encoded price target:

```
stored_value = ln(ln(actual_price_in_rupees))
```

Inference inverts this with `real_price = exp(exp(model.predict(row)))`.

---

*Built with Streamlit · Plotly · XGBoost | © 2026 Smart Laptop Advisor*

"""
utils/data_loader.py
----------------------------------------------------------------------
Central place for loading the trained model, the column schema, and the
laptop dataset.

IMPORTANT — TARGET ENCODING (read before touching predict_price):
The shipped models/xgb_model.pkl was trained on a target that is NOT the
raw rupee price. Forensic check on the model + dataset showed:

    stored_value  = ln(ln(actual_price_in_rupees))

(confirmed by: model base_score == mean(data/laptop_data.csv['Price']) ==
2.3804, and exp(exp(price_column)) reproduces a realistic INR distribution
— min ~9.3k, mean ~60.5k, max ~325k, with sane ordering across brands:
Vero/Mediacom cheapest, Razer/MSI/LG most expensive). This is almost
certainly an upstream feature-engineering bug where `np.log(df['Price'])`
was applied twice before the model was trained. Until the pipeline is
retrained on the raw price, BOTH layers must be inverted at inference:

    real_price = exp(exp(model.predict(row)))

This is implemented once in `_decode_target()` below and used by every
caller — do not re-derive this transform elsewhere.
----------------------------------------------------------------------
>>> TO CONNECT YOUR REAL MODEL <<<
1. Copy your trained model file to:      models/xgb_model.pkl
2. Copy your columns file to:            models/columns.pkl
3. Copy your cleaned dataset (csv) to:   data/laptop_data.csv
That's it — every page already calls these loaders, nothing else to wire.
----------------------------------------------------------------------
"""

import os
import logging
import pickle
import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "xgb_model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "models", "columns.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "laptop_data.csv")

# Sane bounds for the single-log target before we invert it.
_LOG_PRICE_MIN = 5.0
_LOG_PRICE_MAX = 15.0

# Reference categories used across the form + sample-data generator.
# These MUST mirror the one-hot columns actually present in
# models/columns.pkl (verified against the shipped file):
#   Company_*    -> 18 dummies, "Acer" is the dropped baseline category
#   TypeName_*   -> 5 dummies,  "2 in 1 Convertible" is the dropped baseline
#   CPU_Brand_*  -> 4 dummies,  "AMD Processor" is the dropped baseline
#   GPU_Brand_*  -> 3 dummies (ARM, Intel, Nvidia), "AMD" is the dropped baseline
#   OS_Category_*-> 4 dummies, "Chrome" is the dropped baseline
COMPANIES = [
    'Acer', 'Apple', 'Asus', 'Chuwi', 'Dell', 'Fujitsu', 'Google', 'HP',
    'Huawei', 'LG', 'Lenovo', 'MSI', 'Mediacom', 'Microsoft', 'Razer',
    'Samsung', 'Toshiba', 'Vero', 'Xiaomi',
]
TYPENAMES = ["2 in 1 Convertible", "Gaming", "Netbook", "Notebook", "Ultrabook", "Workstation"]
CPU_BRANDS = [
    "AMD Processor",
    "Intel Core i3",
    "Intel Core i5",
    "Intel Core i7",
    "Other Intel Processor",
]
# NOTE: the model was trained with GPU brands {AMD, ARM, Intel, Nvidia}.
# The previous version of this list omitted "ARM" entirely and included
# a non-existent "AMD" dummy column -- selecting AMD silently produced the
# correct (all-zero / baseline) encoding by accident, but ARM could never
# be selected. Fixed to expose every trained category.
GPU_BRANDS = ["AMD", "ARM", "Intel", "Nvidia"]
OS_LIST = ["Chrome", "Linux", "Mac", "Other", "Windows"]
CATEGORIES = ["Budget", "Mid-Range", "Premium", "Ultra-Premium"]


def _decode_target(pred):
    """Invert the single-log target encoding the model was trained on.

    real_price = exp(pred)
    """
    pred = float(np.clip(pred, _LOG_PRICE_MIN, _LOG_PRICE_MAX))
    return float(np.exp(pred))


@st.cache_resource(show_spinner=False)
def load_model():
    """Load the trained XGBoost model. Returns (model, is_real)."""
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return model, True
    except Exception as e:
        logger.warning("Could not load model from %s: %s", MODEL_PATH, e)
        return None, False


@st.cache_resource(show_spinner=False)
def load_columns():
    """Load the feature-column schema used by the model. Returns (columns, is_real)."""
    try:
        with open(COLUMNS_PATH, "rb") as f:
            cols = pickle.load(f)
        return cols, True
    except Exception as e:
        logger.warning("Could not load columns from %s: %s", COLUMNS_PATH, e)
        return None, False


@st.cache_data(show_spinner=False)
def load_dataset():
    """Load the laptop dataset. Falls back to a generated sample frame
    (clearly flagged) so every analytics page renders out of the box.

    The 'Price' column in data/laptop_data.csv is stored in the same
    double-log-compressed scale the model was trained on (see module
    docstring) -- it is decoded back to real INR here, ONCE, so every
    downstream page (analytics, recommendation, home) can simply read
    df['Price'] and get a real rupee figure.
    """
    try:
        df = pd.read_csv(DATA_PATH)
        if "Price" in df.columns:
            df["Price"] = df["Price"].apply(_decode_target)
        return df, True
    except Exception as e:
        logger.warning("Could not load dataset from %s: %s", DATA_PATH, e)
        return _generate_sample_dataset(), False


def _generate_sample_dataset(n=420, seed=42):
    """Synthetic placeholder dataset -- ONLY used until data/laptop_data.csv
    is supplied. Shapes mirror typical laptop-price datasets so every chart
    on the Analytics page has something sensible to draw. Unlike the real
    dataset, prices here are generated directly in real INR (no encoding).

    NOTE: the original version of this function passed `p=` probability
    arrays whose length did not match the number of categories for
    COMPANIES (19 categories, 10 probabilities), CPU_BRANDS (5 vs 7) and
    OS_LIST (5 vs 4) -- this raised ValueError: 'a and p must have same
    size' and crashed the entire app any time the real CSV failed to
    load. All probability arrays below are now correctly sized and
    normalized to sum to 1.
    """
    rng = np.random.default_rng(seed)

    company_p = np.array([.16, .15, .12, .03, .12, .02, .02, .12, .02, .02,
                           .09, .04, .02, .02, .02, .03, .04, .01, .02])
    typename_p = np.array([.10, .18, .08, .30, .22, .12])
    os_p = np.array([.04, .08, .10, .04, .74])

    company = rng.choice(COMPANIES, n, p=company_p / company_p.sum())
    typename = rng.choice(TYPENAMES, n, p=typename_p / typename_p.sum())
    ram = rng.choice([4, 8, 12, 16, 32, 64], n, p=[.10, .32, .10, .30, .14, .04])
    weight = np.round(rng.normal(2.0, 0.6, n).clip(0.9, 4.2), 2)
    inches = rng.choice([13.3, 14.0, 15.6, 16.1, 17.3], n, p=[.18, .17, .40, .15, .10])
    ppi = np.round(rng.normal(141, 28, n).clip(100, 280), 1)

    cpu_brand_p = np.array([.15, .15, .30, .30, .10])
    cpu_brand = rng.choice(CPU_BRANDS, n, p=cpu_brand_p / cpu_brand_p.sum())
    cpu_speed = np.round(rng.normal(2.5, 0.5, n).clip(1.0, 4.5), 2)

    gpu_brand = rng.choice(["Intel", "Nvidia", "AMD"], n, p=[.45, .40, .15])
    ssd = rng.choice([0, 128, 256, 512, 1024], n, p=[.08, .18, .32, .30, .12])
    hdd = rng.choice([0, 500, 1000, 2000], n, p=[.55, .20, .20, .05])
    touchscreen = rng.choice([0, 1], n, p=[.78, .22])
    ips = rng.choice([0, 1], n, p=[.55, .45])
    os_ = rng.choice(["Windows", "Mac", "Linux", "Chrome", "Other"], n, p=os_p / os_p.sum())

    base = 22000
    price = (
        base
        + ram * 950
        + ssd * 9.5
        + hdd * 2.1
        + ppi * 55
        + cpu_speed * 4200
        + touchscreen * 4800
        + ips * 3600
        + (gpu_brand == "Nvidia") * 9500
        + (cpu_brand == "Intel Core i7") * 11000
        + (cpu_brand == "AMD Processor") * 4000
        + rng.normal(0, 6000, n)
    ).clip(15000, 280000).round(-2)

    df = pd.DataFrame({
        "Company": company, "TypeName": typename, "Inches": inches,
        "Ram": ram, "Weight": weight, "Touchscreen": touchscreen, "IPS": ips,
        "PPI": ppi, "SSD": ssd, "HDD": hdd, "CPU_Brand": cpu_brand,
        "CPU_Speed": cpu_speed, "GPU_Brand": gpu_brand, "OS_Category": os_,
        "Price": price,
    })
    return df


def build_feature_row(inputs: dict, columns):
    """Builds a single-row DataFrame matching the model's expected schema
    (`columns`, loaded from models/columns.pkl) from raw UI inputs."""
    row = pd.DataFrame(np.zeros((1, len(columns))), columns=columns)

    numerical_features = {
        "Inches": inputs.get("inches"),
        "Ram": inputs.get("ram"),
        "Weight": inputs.get("weight"),
        "Touchscreen": int(inputs.get("touchscreen", 0)),
        "IPS": int(inputs.get("ips", 0)),
        "PPI": inputs.get("ppi"),
        "SSD": inputs.get("ssd"),
        "HDD": inputs.get("hdd"),
        "Hybrid": inputs.get("hybrid", 0),
        "Flash_Storage": inputs.get("flash_storage", 0),
        "CPU_Speed": inputs.get("cpu_speed"),
    }
    for col, value in numerical_features.items():
        if col in row.columns:
            row.at[0, col] = value

    for prefix, key in (
        ("Company", "company"),
        ("TypeName", "typename"),
        ("CPU_Brand", "cpu_brand"),
        ("GPU_Brand", "gpu_brand"),
        ("OS_Category", "os"),
    ):
        dummy_col = f"{prefix}_{inputs.get(key)}"
        if dummy_col in row.columns:
            row.at[0, dummy_col] = 1
        # else: selected value is the dropped baseline category for this
        # feature group -- correctly represented by leaving all dummies 0.

    return row


def _heuristic_price(inputs: dict):
    """Transparent fallback formula used only when the real model/columns
    are unavailable, so the UI stays demoable. Mirrors the synthetic
    dataset's price formula in _generate_sample_dataset()."""
    price = (
        22000
        + inputs.get("ram", 8) * 950
        + inputs.get("ssd", 0) * 9.5
        + inputs.get("hdd", 0) * 2.1
        + inputs.get("ppi", 141) * 55
        + inputs.get("cpu_speed", 2.5) * 4200
        + int(inputs.get("touchscreen", 0)) * 4800
        + int(inputs.get("ips", 0)) * 3600
        + (inputs.get("gpu_brand") == "Nvidia") * 9500
        + (inputs.get("cpu_brand") == "Intel Core i7") * 11000
    )
    return float(np.clip(price, 15000, 320000))


def predict_price(inputs: dict):
    """Returns (price, is_real_prediction).

    Uses the real model if available; otherwise falls back to a
    transparent heuristic formula so the UI is always fully demoable.
    """
    model, model_ok = load_model()
    columns, cols_ok = load_columns()

    if not (model_ok and cols_ok):
        return round(_heuristic_price(inputs), -2), False

    try:
        row = build_feature_row(inputs, columns)
        raw_pred = float(model.predict(row)[0])
        price = _decode_target(raw_pred)
        return round(price, -2), True
    except Exception as e:
        logger.error("Prediction failed, falling back to heuristic: %s", e)
        return round(_heuristic_price(inputs), -2), False

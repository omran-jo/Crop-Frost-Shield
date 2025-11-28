import pandas as pd
import os

DATA_DIR = 'data'
CSV_FILE = os.path.join(DATA_DIR, 'frost_risk_dataset_1000.csv')

CROP_DB = {
    "بندورة (Tomato)": {"code": 1, "tolerance": 0.0},
    "بطاطا (Potato)": {"code": 2, "tolerance": -2.0},
    "قمح (Wheat)": {"code": 3, "tolerance": -5.0},
    "زيتون (Olive)": {"code": 4, "tolerance": -7.0},
    "فستق (Pistachio)": {"code": 5, "tolerance": -3.0}
}

def get_dataset():
    if os.path.exists(CSV_FILE): return pd.read_csv(CSV_FILE)
    return None

def save_dataset(file):
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    df = pd.read_csv(file)
    df.to_csv(CSV_FILE, index=False)
    return df
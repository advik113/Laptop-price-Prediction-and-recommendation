import pickle
import os

COLUMNS_PATH = r"c:\Users\user\Downloads\output\models\columns.pkl"

with open(COLUMNS_PATH, "rb") as f:
    cols = pickle.load(f)

print("Columns in models/columns.pkl (Count: {}):".format(len(cols)))
print(cols)

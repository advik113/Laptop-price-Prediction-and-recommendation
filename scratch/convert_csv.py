import pandas as pd
import numpy as np

DATA_PATH = r"c:\Users\user\Downloads\output\data\laptop_data.csv"
df = pd.read_csv(DATA_PATH)
print("Original first 5 prices (double-log):")
print(df['Price'].head())

# Convert from double-log to single-log: y_single = exp(y_double)
df['Price'] = np.exp(df['Price'])

print("\nConverted first 5 prices (single-log):")
print(df['Price'].head())

df.to_csv(DATA_PATH, index=False)
print("\nCSV updated successfully!")

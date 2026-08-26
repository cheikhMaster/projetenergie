import pandas as pd
import os

files = [
    "/data/TypeReseauProducteur.xlsx",
    "/data/Recap_Energie.xlsx",
]

for f in files:
    if os.path.exists(f):
        df = pd.read_excel(f)
        print(f"\n=== {f} ===")
        print("Colonnes:", df.columns.tolist())
        print(df.head(3).to_string())
    else:
        print(f"\n=== {f} === INTROUVABLE")

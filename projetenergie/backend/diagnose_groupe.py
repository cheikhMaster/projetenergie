import pandas as pd

df = pd.read_excel("/data/Groupe.xlsx")
df.dropna(how='all', inplace=True)

print(f"Total lignes (après dropna how='all'): {len(df)}")
print(f"Colonnes: {df.columns.tolist()}\n")

# Combien de lignes ont un IDGroupe manquant/invalide ?
id_col = df['IDGroupe']
missing = id_col.isna().sum()
print(f"IDGroupe manquant (NaN): {missing}")

# Convertir en int comme le fait le code (échoue silencieusement -> None)
def to_int(v):
    try:
        if pd.isna(v):
            return None
        return int(v)
    except (TypeError, ValueError):
        return None

df['id_int'] = df['IDGroupe'].apply(to_int)
invalid = df['id_int'].isna().sum()
print(f"IDGroupe non convertible en int: {invalid}")

valid = df['id_int'].notna()
print(f"IDGroupe valides: {valid.sum()}")

# Doublons parmi les IDGroupe valides
dupes = df[valid]['id_int'].duplicated().sum()
unique_valid = df[valid]['id_int'].nunique()
print(f"IDGroupe valides mais dupliqués (lignes en trop): {dupes}")
print(f"IDGroupe valides ET uniques: {unique_valid}")

print(f"\n=> Attendu inséré: {unique_valid} (vs 262 observé)")

# Exemples de doublons
if dupes > 0:
    dup_ids = df[valid][df[valid]['id_int'].duplicated(keep=False)]['id_int']
    print("\nExemples d'IDGroupe dupliqués (5 premiers):")
    print(dup_ids.value_counts().head(5))

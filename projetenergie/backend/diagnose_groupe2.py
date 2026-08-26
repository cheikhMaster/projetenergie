import pandas as pd

df = pd.read_excel("/data/Groupe.xlsx")
df.dropna(how='all', inplace=True)

# Regarder les 2 lignes pour IDGroupe = 11
sample = df[df['IDGroupe'] == 11]
print("=== Les 2 lignes pour IDGroupe=11 ===")
print(sample.to_string())

print("\n=== Les 2 lignes pour IDGroupe=12 ===")
print(df[df['IDGroupe'] == 12].to_string())

# Est-ce que les 2 lignes sont identiques, ou différent sur certaines colonnes ?
print("\n=== Colonnes qui diffèrent entre les 2 occurrences (sur 5 exemples) ===")
for gid in [11, 12, 13, 14, 15]:
    rows = df[df['IDGroupe'] == gid]
    if len(rows) == 2:
        r1, r2 = rows.iloc[0], rows.iloc[1]
        diffs = [col for col in df.columns if str(r1[col]) != str(r2[col])]
        print(f"IDGroupe={gid}: colonnes différentes = {diffs}")

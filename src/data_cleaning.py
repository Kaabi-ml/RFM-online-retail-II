import pandas as pd



# ── CONFIGURATION CLIENT ── 
fichier        = "online_retail_II.csv"
col_client     = "Customer ID"    # ← nom réel de la colonne client
col_date       = "InvoiceDate"    # ← nom réel de la colonne date
col_quantite   = "Quantity"       # ← nom réel de la colonne quantité
col_prix       = "Price"          # ← nom réel de la colonne prix
col_facture    = "Invoice"        # ← nom réel de la colonne commande
encoding       = "latin-1"        # ← "utf-8" ou "latin-1" selon le fichier
separateur     = ","              # ← "," ou ";" selon le CSV
# ─────────────────────────────────────────────────────────────────

df = pd.read_csv(fichier, encoding=encoding, sep=separateur)

# Renommer les colonnes pour que le reste du code fonctionne sans changer
df = df.rename(columns={
    col_client   : "Customer ID",
    col_date     : "InvoiceDate",
    col_quantite : "Quantity",
    col_prix     : "Price",
    col_facture  : "Invoice"
})

#NETTOYAGE

# 1. Supprimer les lignes sans Customer ID (inutilisables pour le RFM)
df = df.dropna(subset=["Customer ID"])

# 2. Supprimer les quantités négatives (retours produits)
df = df[df["Quantity"] > 0]

# 3. Supprimer les prix à zéro ou négatifs
df = df[df["Price"] > 0]

# 4. Convertir les dates en vrai format date
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
# 5. Convertir Customer ID en entier propre
df["Customer ID"] = df["Customer ID"].astype(int)

# Création du fichier
df.to_csv("filtered_retail.csv", index=False)

print(df.head())

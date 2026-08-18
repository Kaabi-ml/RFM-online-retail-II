import pandas as pd
import datetime

import matplotlib.pyplot as plt


# ── CONFIGURATION CLIENT ── à modifier à chaque nouveau client ──
fichier        = "/Users/aminkaabi/Downloads/filtered_retail.csv"
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



# Date de référence = lendemain de la dernière transaction du dataset
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
date_ref = df["InvoiceDate"].max() + datetime.timedelta(days=1)

# Créer une colonne CA par ligne
df["CA"] = df["Quantity"] * df["Price"]

# Calculer les 3 métriques RFM par client
rfm = df.groupby("Customer ID").agg(
    Recence    = ("InvoiceDate", lambda x: (date_ref - x.max()).days),
    Frequence  = ("Invoice",     "nunique"),   # nombre de commandes uniques
    Montant    = ("CA",          "sum")
).reset_index()

# Créer les scores de 1 à 5 pour chaque dimension
rfm["score_R"] = pd.qcut(rfm["Recence"],   5, labels=[5,4,3,2,1])  # inversé : moins = mieux
rfm["score_F"] = pd.qcut(rfm["Frequence"].rank(method="first"), 5, labels=[1,2,3,4,5])
rfm["score_M"] = pd.qcut(rfm["Montant"].rank(method="first"),   5, labels=[1,2,3,4,5])

# Score global
rfm["score_RFM"] = rfm["score_R"].astype(str) + rfm["score_F"].astype(str) + rfm["score_M"].astype(str)

# Segmentation en langage business
def segment(row):
    r = int(row["score_R"])
    f = int(row["score_F"])
    m = int(row["score_M"])
    if r >= 4 and f >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Clients fidèles"
    elif r >= 4 and f <= 2:
        return "Nouveaux clients"
    elif r <= 2 and f >= 3:
        return "A risque de churn"
    else:
        return "Clients perdus"

rfm["Segment"] = rfm.apply(segment, axis=1)

# 1. CA par segment — la question que tout e-commerçant pose en premier
ca_segment = rfm.groupby("Segment").agg(
    Nb_clients = ("Customer ID", "count"),
    CA_total   = ("Montant", "sum"),
    Montant_moyen = ("Montant", "mean")
).round(2)

ca_segment["% CA"] = (ca_segment["CA_total"] / ca_segment["CA_total"].sum() * 100).round(1)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Graphique 1 : répartition des clients par segment
rfm["Segment"].value_counts().plot(
    kind="bar", ax=axes[0], color=["#2ecc71","#e74c3c","#3498db","#f39c12","#9b59b6"]
)
axes[0].set_title("Nombre de clients par segment", fontsize=13, fontweight="bold")
axes[0].set_xlabel("")
axes[0].tick_params(axis="x", rotation=30)

# Graphique 2 : CA par segment
ca_segment["CA_total"].sort_values().plot(
    kind="barh", ax=axes[1], color="#3498db"
)
axes[1].set_title("Chiffre d'affaires par segment (€)", fontsize=13, fontweight="bold")

plt.tight_layout()
plt.savefig("rfm_analyse.png", dpi=150)
plt.show()

# Graphique 3 : le paradoxe Champions — bulles RFM

fig, ax = plt.subplots(figsize=(12, 7))

colors_map = {
    "Champions": "#2ecc71",        # vert
    "Clients fidèles": "#3498db",  # bleu
    "A risque de churn": "#e67e22",# orange
    "Nouveaux clients": "#9b59b6", # violet
    "Clients perdus": "#e74c3c"    # rouge
}

for segment, group in rfm.groupby("Segment"):
    ax.scatter(
        group["Recence"],
        group["Frequence"],
        s=group["Montant"] / 50,        # taille bulle = montant dépensé
        alpha=0.5,
        color=colors_map[segment],
        label=segment
    )

ax.set_xlabel("Récence (jours depuis dernière commande)", fontsize=11)
ax.set_ylabel("Fréquence (nombre de commandes)", fontsize=11)
ax.set_title("Carte des clients — taille = montant dépensé", fontsize=13, fontweight="bold")
ax.legend(title="Segment", bbox_to_anchor=(1.05, 1), loc="upper left")

plt.tight_layout()
plt.savefig("rfm_bulles.png", dpi=150)
plt.show()
print(ca_segment.sort_values("CA_total", ascending=False))

ca_segment.to_csv("/Users/aminkaabi/Downloads/rfm_segment.csv", index=False)
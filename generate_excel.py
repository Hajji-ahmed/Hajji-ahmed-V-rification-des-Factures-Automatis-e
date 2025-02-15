import pandas as pd

# 📌 Données principales de la facture
facture_data = {
    "N° Facture": ["N050195725"],
    "Date Facture": ["31/08/2024"],
    "Client": ["PATHE CINEMAS FRANCE"],
    "Adresse Client": ["32 RUE COULONGE, 44308 NANTES CEDEX 3"],
    "Montant HT": [2141.46],
    "TVA": ["20%"],
    "Montant TTC": [2569.75],
    "Mode de Règlement": ["Chèque"],
}

# 📌 Détails des prestations
prestations_data = {
    "N° Dossier": ["N051021182", "N051021183"],
    "Matériel": ["4 BACS ROULANTS 770L DE CARTON", "6 BACS ROULANTS 770L DE DIB"],
    "Qté": [4, 6],
    "Code CED": ["200101", "200301"],
    "Description": [
        "Papiers et cartons sortes ordinaires",
        "Déchets non recyclables en mélange",
    ],
    "Prix Unitaire HT": [11.28, 15.37],
    "Total HT": [45.12, 768.50],
    "TVA": ["20%", "20%"],
    "Total TTC": [54.14, 922.20],
}

# 📌 Détails des matières
matieres_data = {
    "Code CED": ["200101", "200301"],
    "Désignation": ["Papiers et cartons", "Déchets non recyclables"],
    "Quantité (kg)": [400, 600],
    "Prix Unitaire (€/kg)": [0.28, 0.45],
    "Total (€)": [112.00, 270.00],
}

# 📁 Création du fichier Excel
file_path = "facture_synthese.xlsx"
with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
    pd.DataFrame(facture_data).to_excel(writer, sheet_name="Facture", index=False)
    pd.DataFrame(prestations_data).to_excel(writer, sheet_name="Prestations", index=False)
    pd.DataFrame(matieres_data).to_excel(writer, sheet_name="Matières", index=False)

print(f"✅ Fichier Excel '{file_path}' généré avec succès !")

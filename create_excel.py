import pandas as pd

# 📌 Création des données sans boucle
data = {
    "nom_fournisseur": [
        "Alpha Corp", "Beta Ltd", "Gamma SA", "Delta Inc", "Epsilon LLC",
        "Zeta Group", "Eta Enterprises", "Theta Co", "Iota Trading", "Kappa Systems"
    ],
    "montant_total": [120.50, 250.75, 180.00, 305.40, 150.25, 270.10, 195.60, 220.90, 310.75, 275.50],
    "TVA": ["20%", "19%", "18%", "20%", "19%", "18%", "20%", "19%", "18%", "20%"],
    "numéro_facture": ["F1001", "F1002", "F1003", "F1004", "F1005", "F1006", "F1007", "F1008", "F1009", "F1010"]
}

# 📁 Création du fichier Excel
df = pd.DataFrame(data)
file_path = "base_reference.xlsx"
df.to_excel(file_path, index=False)

print(f"✅ Fichier Excel '{file_path}' généré avec succès !")

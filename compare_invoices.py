from fuzzywuzzy import fuzz
import pandas as pd

def compare_invoice_to_reference(invoice_data, reference_data):
    for index, row in reference_data.iterrows():
        similarity = fuzz.ratio(invoice_data["nom_fournisseur"], row["nom_fournisseur"])
        if similarity > 90:  # Si le nom est très similaire
            if abs(invoice_data["montant_total"] - row["montant_total"]) < 0.5:
                return "Facture correcte ✅"
            else:
                return "Écart détecté ⚠️"
    return "Facture inconnue ❌"

# Exemple d'utilisation
invoice = {"nom_fournisseur": "ABC Ltd.", "montant_total": 100.50}
reference_df = pd.read_excel("base_reference.xlsx")

result = compare_invoice_to_reference(invoice, reference_df)
print(result)

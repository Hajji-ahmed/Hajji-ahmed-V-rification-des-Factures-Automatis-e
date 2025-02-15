from fpdf import FPDF

# 📌 Création d'un PDF représentant une facture
class FacturePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(200, 10, "FACTURE", ln=True, align="C")
        self.ln(10)

# 📄 Données de la facture correspondant à "Beta Ltd"
facture_data = {
    "Facture N°": "F1002",
    "Fournisseur": "Beta Ltd",
    "Montant": "250.75 EUR",
    "TVA": "19%",
    "Date": "07/02/2025"
}

# 📁 Génération du fichier PDF
pdf = FacturePDF()
pdf.add_page()
pdf.set_font("Arial", "", 12)

# Ajout des données au PDF
for key, value in facture_data.items():
    pdf.cell(200, 10, f"{key}: {value}", ln=True)

# 📁 Sauvegarde du fichier PDF
file_path = "facture_test.pdf"
pdf.output(file_path)

print(f"✅ Fichier PDF '{file_path}' généré avec succès !")

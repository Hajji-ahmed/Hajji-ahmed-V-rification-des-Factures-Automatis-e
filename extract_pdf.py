import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)  # Ouvre le fichier PDF
    text = ""
    for page in doc:  # Parcourt chaque page
        text += page.get_text("text") + "\n"  # Extrait le texte
    return text

# Test avec un PDF
pdf_file = "facture_test.pdf"
extracted_text = extract_text_from_pdf(pdf_file)
print(extracted_text)

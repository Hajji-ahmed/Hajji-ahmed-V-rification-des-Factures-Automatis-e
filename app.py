import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openpyxl
import io
import re

# 📌 Fonction pour nettoyer et extraire les données du PDF
def extract_structured_data_from_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        
        structured_data = {}
        for line in text.split("\n"):
            if ":" in line:  # Supposons que les champs sont au format "Champ: Valeur"
                key, value = line.split(":", 1)
                structured_data[key.strip()] = value.strip()
        
        return structured_data
    except Exception as e:
        st.error(f"Erreur lors de l'extraction du texte : {e}")
        return {}

# 📌 Fonction pour comparer les données avec la base Excel
def compare_with_reference(extracted_data, reference_file):
    try:
        reference_df = pd.read_excel(reference_file)

        if reference_df.empty:
            st.warning("⚠️ La base de référence est vide.")
            return {}

        extracted_df = pd.DataFrame([extracted_data])
        discrepancies = {}

        for index, row in reference_df.iterrows():
            for col in reference_df.columns:
                if col in extracted_df.columns:
                    if str(row[col]).strip() != str(extracted_df[col].values[0]).strip():
                        discrepancies[col] = extracted_df[col].values[0]
        
        return discrepancies
    except Exception as e:
        st.error(f"Erreur lors de la comparaison : {e}")
        return {}

# 📌 Fonction pour générer un fichier Excel des écarts détectés
def generate_discrepancy_excel(discrepancies):
    output = io.BytesIO()
    df = pd.DataFrame([discrepancies])
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Écarts détectés")
    return output.getvalue()

# 🎨 Interface modernisée avec Streamlit
st.set_page_config(page_title="Vérification des Factures", page_icon="🧾", layout="wide")

# 🔵 En-tête stylisé
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔍 Vérification des Factures Automatisée</h1>", unsafe_allow_html=True)
st.write("📂 **Téléversez une facture PDF et une base de référence Excel pour détecter les écarts.**")

# 📂 Sidebar : Importation des fichiers
st.sidebar.header("📥 Téléversement des fichiers")
uploaded_pdf = st.sidebar.file_uploader("Téléverser une facture PDF", type=["pdf"])
uploaded_excel = st.sidebar.file_uploader("Téléverser la base de référence Excel", type=["xlsx"])

# 🟢 Étape 1 : Extraction des données du PDF
if uploaded_pdf:
    st.success("✅ Facture PDF téléversée avec succès !")
    with st.expander("📜 Voir le texte extrait", expanded=False):
        extracted_data = extract_structured_data_from_pdf(uploaded_pdf)
        st.json(extracted_data)

# 🟠 Étape 2 : Comparaison avec la base de référence
if uploaded_pdf and uploaded_excel:
    st.success("✅ Base de référence Excel téléversée avec succès !")
    discrepancies = compare_with_reference(extracted_data, uploaded_excel)

    if discrepancies:
        st.markdown("### ⚠️ Écarts détectés")
        st.write("Les différences suivantes ont été trouvées entre la facture et la base de référence :")
        st.table(pd.DataFrame([discrepancies]))

        # 📥 Bouton d'exportation en Excel
        excel_data = generate_discrepancy_excel(discrepancies)
        st.download_button(label="📥 Télécharger le rapport en Excel",
                           data=excel_data,
                           file_name="ecarts_detectes.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.success("❌ Aucun écart détecté !")

# 🎛️ Sidebar : Options avancées
st.sidebar.header("⚙️ Options avancées")
scroll_position = st.sidebar.slider("📜 Ajuster le défilement", 0, 100, 50)
brightness = st.sidebar.slider("💡 Luminosité de l'affichage", 0.5, 1.5, 1.0)
st.sidebar.image("https://via.placeholder.com/300", caption="Aperçu de la facture", use_container_width=True)

# 📌 Ajout d'une barre de séparation pour la fin de l'application
st.markdown("---")
st.write("✨ Merci d'utiliser notre application de contrôle des factures !")

import requests
import json
import os
import streamlit as st
import fitz  # PyMuPDF pour l'extraction du texte PDF
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO
from dotenv import load_dotenv

# ✅ Chargement de la clé API depuis .env
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    st.error("⚠️ Clé API introuvable ! Vérifiez le fichier .env et redémarrez l'application.")
    st.stop()

# ✅ URL de l'API Gemini
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

# ✅ Configuration de Streamlit
st.set_page_config(page_title="Validation des Factures", page_icon="📄", layout="wide")
st.title("📄 Validation Automatisée des Factures avec Gemini")

# 📌 Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(uploaded_file):
    """Extrait le texte brut d'un fichier PDF."""
    pdf_data = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
        for page in pdf:
            pdf_data += page.get_text("text") + "\n"
    return pdf_data.strip()

# 📌 Fonction pour structurer les données avec Gemini
def get_structured_data_from_gemini(extracted_text):
    """Envoie le texte brut à l'API Gemini et récupère une réponse JSON correcte."""
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": """Tu es un assistant d'extraction de factures.
                        Récupère uniquement les données sous ce format JSON strict :
                        {
                            "numéro_facture": "12345",
                            "date_facture": "2024-02-15",
                            "montant_total": "500",
                            "nom_client": "Entreprise XYZ"
                        }
                        ❌ Ne renvoie **aucun texte supplémentaire** en dehors du JSON.
                        ✅ Réponds uniquement avec un JSON valide."""
                    },
                    {"text": f"Facture brute : {extracted_text}"}
                ]
            }
        ],
        "generation_config": {"temperature": 0.2},  # Diminue la créativité pour stabiliser la réponse
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        st.write("🔍 Réponse brute de l'API :", result)  # Debugging

        if "candidates" not in result or not result["candidates"]:
            st.error("❌ Réponse vide de l'API Gemini. Vérifiez votre prompt ou les crédits API.")
            return None

        response_text = result["candidates"][0]["content"]["parts"][0]["text"]

        if not response_text.strip():  # Vérifie si la réponse est vide
            st.error("❌ L'API a renvoyé une réponse vide.")
            return None

        try:
            # ✅ Nettoyer la réponse brute pour éviter l'erreur de parsing
            response_text = response_text.strip("`json").strip("```").strip()

            # ✅ Trouver la position du premier `{` et du dernier `}`
            start = response_text.find("{")
            end = response_text.rfind("}")

            if start == -1 or end == -1:
                st.error("❌ Erreur : Aucun JSON valide trouvé dans la réponse de l'API.")
                return None

            json_cleaned = response_text[start:end+1]  # Extraire uniquement le JSON

            # ✅ Convertir en dictionnaire Python
            structured_data = json.loads(json_cleaned)
            return structured_data
        except json.JSONDecodeError as e:
            st.error(f"❌ Erreur de conversion JSON : {e}")
            st.write("🔍 Réponse brute après nettoyage :", response_text)  # Debugging
            return None
    else:
        st.error(f"❌ Erreur API Gemini : {response.status_code}")
        st.write("🔍 Contenu de la réponse :", response.text)  # Debugging
        return None

# 📌 Fonction pour charger la base de référence Excel
def load_reference_data(uploaded_excel):
    """Charge un fichier Excel et retourne la liste des feuilles."""
    xls = pd.ExcelFile(uploaded_excel)
    return xls

# 📌 Fonction pour comparer les données extraites avec la base de référence
def compare_data(extracted_data, reference_data):
    """Compare les données extraites avec la base de référence Excel."""
    extracted_df = pd.DataFrame([extracted_data])
    discrepancies = pd.concat([extracted_df, reference_data]).drop_duplicates(keep=False)
    return discrepancies

# 📌 Interface utilisateur pour télécharger les fichiers
st.sidebar.header("📂 Téléverser les fichiers")
uploaded_pdf = st.sidebar.file_uploader("📄 Téléverser une facture (PDF)", type="pdf")
uploaded_excel = st.sidebar.file_uploader("📊 Téléverser la base de référence (Excel)", type="xlsx")

# 📌 Extraction et affichage des données du PDF
if uploaded_pdf:
    st.subheader("📜 Données extraites du PDF")
    extracted_text = extract_text_from_pdf(uploaded_pdf)
    st.text_area("🔍 Texte extrait", extracted_text, height=200)

    # Structuration des données via Gemini
    structured_data = get_structured_data_from_gemini(extracted_text)
    
    if structured_data:
        st.subheader("📑 Données structurées par Gemini")
        structured_df = pd.DataFrame([structured_data])
        st.dataframe(structured_df)

# 📌 Chargement et affichage de la base Excel
if uploaded_excel:
    xls = load_reference_data(uploaded_excel)
    sheet_names = xls.sheet_names
    selected_sheet = st.selectbox("📜 Sélectionner une feuille", sheet_names)
    reference_data = pd.read_excel(xls, sheet_name=selected_sheet)

    st.subheader(f"📊 Base de référence : {selected_sheet}")
    st.dataframe(reference_data)

# 📌 Comparaison des données et affichage des écarts
if uploaded_pdf and uploaded_excel and structured_data:
    st.subheader("⚖️ Comparaison des données")
    discrepancies = compare_data(structured_data, reference_data)

    if not discrepancies.empty:
        st.error("⚠️ Des écarts ont été détectés !")
        st.dataframe(discrepancies)
    else:
        st.success("✅ Aucun écart détecté, la facture est conforme.")

# 📌 Téléchargement des résultats
if uploaded_pdf and uploaded_excel and structured_data:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        discrepancies.to_excel(writer, index=False, sheet_name="Écarts")
    output.seek(0)

    st.download_button(
        label="⬇️ Télécharger les écarts en Excel",
        data=output,
        file_name="ecarts_detectes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

import requests
import json
import os
import streamlit as st
import fitz  # PyMuPDF pour extraire le texte des factures
import pandas as pd
from fuzzywuzzy import fuzz
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
st.title("📄 Validation Automatisée des Factures ")

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

    prompt = """Tu es un assistant spécialisé dans l'extraction de factures.
    Récupère uniquement les données sous ce format JSON strict :
    {
        "numéro_facture": "12345",
        "date_facture": "2024-02-15",
        "date_echeance": "2024-03-15",
        "mode_reglement": "Virement",
        "client": {
            "nom": "Entreprise XYZ",
            "adresse": "123 Rue de Paris, 75001 Paris",
            "TVA_intracommunautaire": "FR123456789"
        },
        "banque": {
            "IBAN": "FR7612345678901234567890123",
            "BIC": "BNPAFRPP"
        },
        "montants": {
            "total_HT": "500",
            "TVA": "20%",
            "total_TVA": "100",
            "total_TTC": "600"
        },
        "produits": [
            {"nom": "Produit A", "quantité": 2, "prix_unitaire": 100},
            {"nom": "Produit B", "quantité": 3, "prix_unitaire": 50}
        ]
    }
    ❌ Ne renvoie **aucun texte supplémentaire** en dehors du JSON.
    ✅ Réponds uniquement avec un JSON valide."""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"text": f"Facture brute : {extracted_text}"}
                ]
            }
        ],
        "generation_config": {"temperature": 0.1},  
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        try:
            response_text = response_text.strip("`json").strip("```").strip()
            start = response_text.find("{")
            end = response_text.rfind("}")
            json_cleaned = response_text[start:end+1]
            structured_data = json.loads(json_cleaned)
            return structured_data
        except json.JSONDecodeError as e:
            st.error(f"❌ Erreur de conversion JSON : {e}")
            return None
    else:
        st.error(f"❌ Erreur API Gemini : {response.status_code}")
        return None

# 📌 Chatbot utilisant l'API Gemini
def chatbot_gemini(user_question, extracted_data, reference_data):
    """Envoie la question de l'utilisateur à l'API Gemini en lui donnant le contexte des données."""
    headers = {"Content-Type": "application/json"}

    prompt = f"""Tu es un assistant expert en facturation.
    L'utilisateur a une question concernant la facture et la base de données.
    Voici les informations de la facture :
    {json.dumps(extracted_data, indent=2)}
    Voici les données de référence :
    {reference_data.to_json(orient="records")}
    Réponds de manière claire et détaillée."""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"text": f"Question : {user_question}"}
                ]
            }
        ],
        "generation_config": {"temperature": 0.3},  
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Erreur API Gemini : {response.status_code}"

# 📌 Interface utilisateur
st.sidebar.header("📂 Téléverser les fichiers")
uploaded_pdf = st.sidebar.file_uploader("📄 Téléverser une facture (PDF)", type="pdf")
uploaded_excel = st.sidebar.file_uploader("📊 Téléverser la base de référence (Excel)", type="xlsx")

if uploaded_pdf:
    st.subheader("📜 Données extraites du PDF")
    extracted_text = extract_text_from_pdf(uploaded_pdf)
    st.text_area("🔍 Texte extrait", extracted_text, height=200)

    structured_data = get_structured_data_from_gemini(extracted_text)

    if structured_data:
        st.subheader("📑 Données structurées par Gemini")
        structured_df = pd.DataFrame([structured_data])
        st.dataframe(structured_df)

if uploaded_excel:
    xls = pd.ExcelFile(uploaded_excel)
    selected_sheet = st.selectbox("📜 Sélectionner une feuille", xls.sheet_names)
    reference_data = pd.read_excel(xls, sheet_name=selected_sheet)

    st.subheader(f"📊 Base de référence : {selected_sheet}")
    st.dataframe(reference_data)

# 📌 Chatbot interactif
if uploaded_pdf and uploaded_excel and structured_data is not None:
    st.subheader("💬 Chatbot : Posez vos questions sur la facture")
    user_question = st.text_input("❓ Posez une question sur la facture ou la base de données")

    if user_question:
        chatbot_response = chatbot_gemini(user_question, structured_data, reference_data)
        st.write("🧠 Réponse du chatbot :", chatbot_response)

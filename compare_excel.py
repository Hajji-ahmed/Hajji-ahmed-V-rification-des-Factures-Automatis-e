import pandas as pd

def load_reference_data(excel_path):
    df = pd.read_excel(excel_path)  # Charge le fichier Excel
    return df

# Test avec un fichier Excel
excel_file = "base_reference.xlsx"
reference_data = load_reference_data(excel_file)
print(reference_data.head())  # Affiche les premières lignes

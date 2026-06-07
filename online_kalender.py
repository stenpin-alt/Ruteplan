import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Konfiguration
st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

def load_and_process_data():
    if not os.path.exists('kundeliste.xlsx'):
        return None
    
    df = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df.columns = df.columns.astype(str).str.strip()
    
    plan = []
    # Eksempel på logik: Beregn datoer baseret på frekvens
    for _, row in df.iterrows():
        navn = row.get('Navn', 'Ukendt')
        konsulent = row.get('Konsulent', 'Ukendt')
        frekvens = float(row.get('Besøgsfrekvens', 0.1)) # Sikr numerisk værdi
        
        # Her skal din logik for dato-generering være baseret på frekvens
        # Simpel placeholder: Alle får en dato i 2026
        dato = datetime(2026, 6, 8) 
        
        plan.append({
            "title": navn,
            "start": dato.strftime('%Y-%m-%d'),
            "end": dato.strftime('%Y-%m-%d'),
            "Konsulent": konsulent
        })
    return pd.DataFrame(plan)

# Sørg for at data altid findes
if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = load_and_process_data()

df_plan = st.session_state['df_plan']

if df_plan is not None:
    valgt_konsulent = st.selectbox("Vælg konsulent:", df_plan['Konsulent'].unique())
    df_filt = df_plan[df_plan['Konsulent'] == valgt_konsulent]
    
    st.dataframe(df_filt)
else:
    st.error("Kunne ikke behandle 'kundeliste.xlsx'. Tjek filformatet.")

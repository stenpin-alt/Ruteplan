import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# Opsætning af siden
st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. DATAFUNKTION ---
@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        # Indlæs og rens kolonner
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# --- 2. BEREGNINGSLOGIK ---
def generate_plan(df):
    plan_data = []
    # HER SKAL DIT LOOP VÆRE
    # Eksempel på hvordan data skal struktureres for kalenderen:
    for _, row in df.iterrows():
        plan_data.append({
            "title": str(row.get("Navn", "Kunde")),
            "start": "2026-06-08", # Sæt din beregnede dato her (format: YYYY-MM-DD)
            "end": "2026-06-08",
            "Konsulent": str(row.get("Konsulent", "Ukendt"))
        })
    return pd.DataFrame(plan_data)

# --- 3. HOVEDPROGRAM ---
df_kunder = load_data()

if df_kunder is not None:
    # Beregn planen én gang og gem i session_state
    if 'df_plan' not in st.session_state:
        st.session_state['df_plan'] = generate_plan(df_kunder)
    
    df_plan = st.session_state['df_plan']

    # Vis konsulent-vælger
    konsulenter = df_plan['Konsulent'].unique()
    valgt = st.selectbox("Vælg konsulent:", konsulenter)

    # Filtrer og vis
    df_visning = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Rute for {valgt}")
    
    # Kalender-visning
    calendar_events = df_visning.to_dict('records')
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    
    # Tabel-visning
    st.subheader("📋 Detaljer")
    st.dataframe(df_visning)

else:
    st.error("Filen 'kundeliste.xlsx' blev ikke fundet i mappen. Tjek GitHub.")

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# Hent data
def get_clean_data():
    if not os.path.exists('kundeliste.xlsx'): return None
    df = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df.columns = df.columns.astype(str).str.strip()
    return df.drop_duplicates(subset=['Navn'])

df_raw = get_clean_data()

# Brug en session_state nøgle til at huske om vi allerede har genereret planen
if 'plan_genereret' not in st.session_state:
    st.session_state['plan_genereret'] = False
    st.session_state['df_final'] = pd.DataFrame()

if st.button("Generer plan"):
    plan_data = []
    start_dato = datetime(2026, 1, 5)
    
    for _, row in df_raw.iterrows():
        navn = str(row.get("Navn", "Ukendt"))
        konsulent = str(row.get("Konsulent", "Ukendt"))
        try:
            frekvens = float(str(row.get("Besøgsfrekvens", 0.1)).replace(',', '.'))
        except:
            frekvens = 0.1
            
        antal_besoeg = max(1, int(52 * frekvens))
        interval = 52 // antal_besoeg
        
        for i in range(antal_besoeg):
            dato = start_dato + timedelta(weeks=i * interval)
            plan_data.append({
                "Navn": navn,
                "start": dato.strftime('%Y-%m-%d'),
                "end": dato.strftime('%Y-%m-%d'),
                "Konsulent": konsulent
            })
    
    st.session_state['df_final'] = pd.DataFrame(plan_data)
    st.session_state['plan_genereret'] = True
    st.rerun()

# Visning - viser KUN hvis plan_genereret er True
if st.session_state['plan_genereret']:
    df = st.session_state['df_final']
    valgt = st.selectbox("Vælg konsulent:", sorted(df['Konsulent'].unique()))
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    events = [{"title": r["Navn"], "start": r["start"], "end": r["end"]} for _, r in df_filt.iterrows()]
    calendar(events=events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt, use_container_width=True)

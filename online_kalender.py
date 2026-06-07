import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

def generer_plan():
    if not os.path.exists('kundeliste.xlsx'):
        return None
        
    # Læs filen
    df_raw = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df_raw.columns = df_raw.columns.astype(str).str.strip()
    
    # SIKKERHED: Fjern dubletter med det samme baseret på Navn
    df_raw = df_raw.drop_duplicates(subset=['Navn'])
    
    plan_data = []
    start_dato = datetime(2026, 1, 5)
    
    for _, row in df_raw.iterrows():
        # Hent frekvens
        val = row.get("Besøgsfrekvens", 0.1)
        try:
            frekvens = float(str(val).replace(',', '.'))
        except:
            frekvens = 0.1
            
        navn = str(row.get("Navn", "Ukendt"))
        konsulent = str(row.get("Konsulent", "Ukendt"))
        
        # Beregn besøg
        antal_besoeg = max(1, int(52 * frekvens))
        interval = 52 // antal_besoeg
        
        for uge in range(0, 52, interval):
            dato = start_dato + timedelta(weeks=uge)
            plan_data.append({
                "Navn": navn,
                "start": dato.strftime('%Y-%m-%d'),
                "end": dato.strftime('%Y-%m-%d'),
                "Konsulent": konsulent
            })
    return pd.DataFrame(plan_data)

# Knap-logik
if st.button("Generer/Opdater plan"):
    st.session_state['df_final'] = generer_plan()

# Visning
if 'df_final' in st.session_state and st.session_state['df_final'] is not None:
    df = st.session_state['df_final']
    
    valgt = st.selectbox("Vælg konsulent:", sorted(df['Konsulent'].unique()))
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    events = [
        {"title": r["Navn"], "start": r["start"], "end": r["end"]} 
        for _, r in df_filt.iterrows()
    ]
    
    calendar(events=events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt, use_container_width=True)

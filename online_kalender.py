import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# Indlæs rådata direkte (uden cache for at sikre frisk data)
def load_raw_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# Byg planen direkte i selve kørslen
df_raw = load_raw_data()
plan_data = []

if df_raw is not None:
    start_dato = datetime(2026, 1, 5)
    
    for _, row in df_raw.iterrows():
        # Hent og konverter frekvens
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

    df = pd.DataFrame(plan_data)
    
    # Visning
    konsulenter = sorted(df['Konsulent'].unique())
    valgt = st.selectbox("Vælg konsulent:", konsulenter)
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    calendar_events = [
        {"title": r["Navn"], "start": r["start"], "end": r["end"]} 
        for _, r in df_filt.iterrows()
    ]
        
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt, use_container_width=True)
else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'.")

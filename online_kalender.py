import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        # Vi indlæser kun relevante kolonner for at undgå fejl
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# Initialisering af session state
if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = None

df_raw = load_data()

# Knap til at generere planen
if st.button("Generer plan"):
    if df_raw is not None:
        plan_data = []
        start_dato = datetime(2026, 1, 5)
        
        for _, row in df_raw.iterrows():
            # Hent og konverter frekvens sikkert
            val = row.get("Besøgsfrekvens", 0.1)
            try:
                frekvens = float(str(val).replace(',', '.'))
            except:
                frekvens = 0.1
                
            navn = str(row.get("Navn", "Ukendt"))
            konsulent = str(row.get("Konsulent", "Ukendt"))
            
            # Beregn antal besøg og interval
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
        
        st.session_state['df_plan'] = pd.DataFrame(plan_data)
        st.rerun() # Genindlæs siden for at vise data med det samme
    else:
        st.error("Kunne ikke finde 'kundeliste.xlsx'.")

# Visning af kalender og tabel
if st.session_state['df_plan'] is not None:
    df = st.session_state['df_plan']
    
    konsulenter = sorted(df['Konsulent'].unique())
    valgt = st.selectbox("Vælg konsulent:", konsulenter)
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    # Klargør data specifikt til kalenderen (kun nødvendige felter)
    calendar_events = [
        {"title": r["Navn"], "start": r["start"], "end": r["end"]} 
        for _, r in df_filt.iterrows()
    ]
        
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt, use_container_width=True)

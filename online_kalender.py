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
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = None

df_raw = load_data()

if st.button("Generer plan"):
    if df_raw is not None:
        plan_data = []
        start_dato = datetime(2026, 1, 5)
        
        for i, (_, row) in enumerate(df_raw.iterrows()):
            dato = start_dato + timedelta(days=i)
            # Vi opretter kun de absolut nødvendige felter og sikrer ingen None-værdier
            plan_data.append({
                "title": str(row.get("Navn", "Ukendt")),
                "start": dato.strftime('%Y-%m-%d'),
                "end": dato.strftime('%Y-%m-%d'),
                "Konsulent": str(row.get("Konsulent", "Ukendt"))
            })
        
        st.session_state['df_plan'] = pd.DataFrame(plan_data)
        st.success("Plan genereret!")

if st.session_state['df_plan'] is not None:
    df = st.session_state['df_plan']
    valgt = st.selectbox("Vælg konsulent:", df['Konsulent'].unique())
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    # RENSNING TIL KALENDER: Konverter til liste af ordbøger og fjern alt der ikke er 'title', 'start', 'end'
    calendar_events = []
    for _, row in df_filt.iterrows():
        calendar_events.append({
            "title": row["title"],
            "start": row["start"],
            "end": row["end"]
        })
        
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt)

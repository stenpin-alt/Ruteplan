import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# 1. Dataindlæsning
@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# 2. Initialisering af session state
if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = None

df_raw = load_data()

# 3. Knap-logik: Fordel kunder jævnt over året
if st.button("Generer plan (Ignorer leveringsdage)"):
    if df_raw is not None:
        plan_data = []
        start_dato = datetime(2026, 1, 5) # Første mandag i 2026
        
        # Vi fordeler kunderne med 1 dags interval pr. kunde
        for i, (_, row) in enumerate(df_raw.iterrows()):
            dato = start_dato + timedelta(days=i)
            plan_data.append({
                "title": row.get("Navn", "Ukendt"),
                "start": dato.strftime('%Y-%m-%d'),
                "end": dato.strftime('%Y-%m-%d'),
                "Konsulent": row.get("Konsulent", "Ukendt")
            })
        
        st.session_state['df_plan'] = pd.DataFrame(plan_data)
        st.success("Plan genereret!")
    else:
        st.error("Kunne ikke finde filen.")

# 4. Visning
if st.session_state['df_plan'] is not None:
    df = st.session_state['df_plan']
    valgt = st.selectbox("Vælg konsulent:", df['Konsulent'].unique())
    df_filt = df[df['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    calendar(events=df_filt.to_dict('records'), options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt)

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

def get_data():
    if not os.path.exists('kundeliste.xlsx'): return None
    df = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df.columns = df.columns.astype(str).str.strip()
    return df.drop_duplicates(subset=['Navn'])

df_raw = get_data()

if df_raw is not None:
    # Vi bruger en fast start-mandag
    start_date = datetime(2026, 1, 5)
    plan_data = []

    for _, row in df_raw.iterrows():
        navn = str(row.get("Navn", "Ukendt"))
        konsulent = str(row.get("Konsulent", "Ukendt"))
        
        # Frekvens-konvertering
        try:
            val = str(row.get("Besøgsfrekvens", 0.1)).replace(',', '.')
            frekvens = float(val)
        except:
            frekvens = 0.1
        
        # Beregn antal besøg
        antal = max(1, int(52 * frekvens))
        
        # SPREDNING: Vi fordeler besøgene jævnt over 52 uger
        for i in range(antal):
            # Beregn ugenummer (0 til 51) og læg til
            uge_offset = int((52 / antal) * i)
            dato = start_date + timedelta(weeks=uge_offset)
            
            plan_data.append({
                "Navn": navn,
                "start": dato.strftime('%Y-%m-%d'),
                "end": dato.strftime('%Y-%m-%d'),
                "Konsulent": konsulent
            })

    df_final = pd.DataFrame(plan_data)
    
    valgt = st.selectbox("Vælg konsulent:", sorted(df_final['Konsulent'].unique()))
    df_filt = df_final[df_final['Konsulent'] == valgt]
    
    # Kalender
    events = [{"title": r["Navn"], "start": r["start"], "end": r["end"]} for _, r in df_filt.iterrows()]
    calendar(events=events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt)
else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'.")

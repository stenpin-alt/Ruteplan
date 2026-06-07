import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# Læs data og fjern ALT der ligner dubletter med det samme
def get_clean_data():
    if not os.path.exists('kundeliste.xlsx'):
        return None
    df = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df.columns = df.columns.astype(str).str.strip()
    # Fjern rækker der er 100% ens
    return df.drop_duplicates()

df_raw = get_clean_data()

if df_raw is not None:
    plan_data = []
    start_dato = datetime(2026, 1, 5)
    
    # Vi bruger 'itertuples' i stedet for 'iterrows' - det er hurtigere og mere stabilt
    for row in df_raw.itertuples(index=False):
        # Hent værdier med 'getattr' for at undgå fejl
        navn = str(getattr(row, 'Navn', 'Ukendt'))
        konsulent = str(getattr(row, 'Konsulent', 'Ukendt'))
        val = getattr(row, 'Besøgsfrekvens', 0.1)
        
        try:
            frekvens = float(str(val).replace(',', '.'))
        except:
            frekvens = 0.1
        
        antal_besoeg = max(1, int(52 * frekvens))
        interval = 52 // antal_besoeg
        
        for i in range(antal_besoeg):
            dato = start_dato + timedelta(weeks=i * interval)
            # Tilføj kun hvis året er 2026
            if dato.year == 2026:
                plan_data.append({
                    "Navn": navn,
                    "start": dato.strftime('%Y-%m-%d'),
                    "end": dato.strftime('%Y-%m-%d'),
                    "Konsulent": konsulent
                })

    # Skab en helt ny dataframe og fjern eventuelle dubletter herfra også
    df_plan = pd.DataFrame(plan_data).drop_duplicates()

    # Visning
    konsulenter = sorted(df_plan['Konsulent'].unique())
    valgt = st.selectbox("Vælg konsulent:", konsulenter)
    df_filt = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    events = [{"title": r["Navn"], "start": r["start"], "end": r["end"]} for _, r in df_filt.iterrows()]
    
    calendar(events=events, options={"initialView": "dayGridMonth"})
    st.dataframe(df_filt, use_container_width=True)
else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'.")

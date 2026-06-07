import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# 1. Hent data uden cache for at sikre at vi altid læser den nyeste fil
def get_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# 2. Hovedlogik
df_raw = get_data()

if df_raw is not None:
    plan_data = []
    # Startdato er altid en mandag
    start_dato = datetime(2026, 1, 5) 
    
    for _, row in df_raw.iterrows():
        navn = str(row.get("Navn", "Ukendt"))
        konsulent = str(row.get("Konsulent", "Ukendt"))
        
        # Frekvens logik
        try:
            val = row.get("Besøgsfrekvens", 0.1)
            frekvens = float(str(val).replace(',', '.'))
        except:
            frekvens = 0.1
        
        # Beregn antal besøg (f.eks. 0.1 = 5 besøg om året)
        antal_besoeg = max(1, int(52 * frekvens))
        interval = 52 // antal_besoeg
        
        # Fordel besøg jævnt ved at lægge uger til startdatoen
        for i in range(antal_besoeg):
            dato = start_dato + timedelta(weeks=i * interval)
            # Sørg for vi holder os indenfor 2026
            if dato.year == 2026:
                plan_data.append({
                    "Navn": navn,
                    "start": dato.strftime('%Y-%m-%d'),
                    "end": dato.strftime('%Y-%m-%d'),
                    "Konsulent": konsulent
                })

    df_plan = pd.DataFrame(plan_data)

    # 3. Visning
    valgt = st.selectbox("Vælg konsulent:", sorted(df_plan['Konsulent'].unique()))
    df_filt = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Kalender for {valgt}")
    
    # Konverter til kalender format
    events = [{"title": r["Navn"], "start": r["start"], "end": r["end"]} for _, r in df_filt.iterrows()]
    
    calendar(events=events, options={"initialView": "dayGridMonth"})
    
    st.subheader("Data detaljer")
    st.dataframe(df_filt, use_container_width=True)

else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'.")

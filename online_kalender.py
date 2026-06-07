import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- HJÆLPEFUNKTION TIL DATOER ---
def get_date_from_week(year, week, day_of_week):
    """Konverterer ugenummer og dag (0=Man, 4=Fre) til en dato."""
    # Find første mandag i året
    jan1 = datetime(year, 1, 1)
    # Find første mandag (hvis jan1 er lør/søn, hop til næste uge)
    first_monday = jan1 + timedelta(days=(7-jan1.weekday()) % 7)
    # Beregn dato baseret på uge og dag
    target_date = first_monday + timedelta(weeks=week-1, days=day_of_week)
    return target_date

# --- BEREGNING ---
if os.path.exists('kundeliste.xlsx'):
    df = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df.columns = df.columns.astype(str).str.strip()

    plan_data = []
    # HER ER DIT LOOP - Sørg for at du har kolonnerne 'Uge' og 'Dag' i din Excel
    for _, row in df.iterrows():
        # Hvis du ikke har 'Uge'/'Dag' i Excel, skal de beregnes her!
        # Eksempel: Hvis du har en 'Dag'-kolonne med teksten "Mandag"
        uge = int(row.get('Uge', 1))
        
        # Konverter ugedag-tekst til tal (0-4)
        dag_tekst = str(row.get('Dag', 'Mandag')).lower()
        dag_tal = 0 # Default til mandag
        if 'tir' in dag_tekst: dag_tal = 1
        elif 'ons' in dag_tekst: dag_tal = 2
        elif 'tor' in dag_tekst: dag_tal = 3
        elif 'fre' in dag_tekst: dag_tal = 4
        
        calc_date = get_date_from_week(2026, uge, dag_tal)
        
        plan_data.append({
            "title": str(row.get("Navn", "Kunde")),
            "start": calc_date.strftime('%Y-%m-%d'),
            "end": calc_date.strftime('%Y-%m-%d'),
            "Konsulent": str(row.get("Konsulent", "Ukendt"))
        })
    
    df_plan = pd.DataFrame(plan_data)

    # --- VISNING ---
    konsulenter = df_plan['Konsulent'].unique()
    valgt = st.selectbox("Vælg konsulent:", konsulenter)

    df_visning = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Rute for {valgt}")
    calendar(events=df_visning.to_dict('records'), options={"initialView": "dayGridMonth"})
    
    st.dataframe(df_visning)
else:
    st.error("kundeliste.xlsx mangler.")

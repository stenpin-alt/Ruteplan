import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
from icalendar import Calendar, Event

st.set_page_config(layout="wide", page_title="Ruteplanlægger")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. UPLOAD & RENSNING ---
kunde_fil = st.file_uploader("Upload Kundeliste (Excel)", type=["xlsx", "xls"])

if kunde_fil:
    # Læs filen - jeg har sat skiprows til 0, da din tidligere fejl viste kolonner fra række 0
    df = pd.read_excel(kunde_fil, skiprows=0) 
    df.columns = df.columns.astype(str).str.strip()
    
    # Automatisk detektering af kolonner
    def find_kol(navn_dele):
        for col in df.columns:
            if any(n.lower() in col.lower() for n in navn_dele): return col
        return None

    k_kons = find_kol(["konsulent", "løn nr"])
    k_navn = find_kol(["navn"])
    
    if not k_kons or not k_navn:
        st.error(f"Kunne ikke finde nødvendige kolonner. Fundne: {list(df.columns)}")
        st.stop()

    # RENSNING
    df = df.dropna(subset=[k_navn]) # Fjern rækker uden navn
    df[k_kons] = df[k_kons].fillna("Ikke tildelt") 
    
    st.success(f"Fil indlæst! Bruger '{k_navn}' som navn og '{k_kons}' som konsulent.")

    # --- 2. LOGIK ---
    if st.button("Generer Kalender", type="primary"):
        plan_data = []
        start_dato = datetime(2026, 1, 5)
        
        for _, row in df.iterrows():
            kons = str(row.get(k_kons, "Ukendt"))
            
            # Håndtering af frekvens uden at crashe på NaN
            raw_frek = row.get("Besøg pr. uge")
            try:
                frek = float(str(raw_frek).replace(',', '.'))
            except:
                frek = 0.25 # Standard hvis cellen er tom
            
            antal = max(1, int(52 * frek))
            interval = 52 // antal
            
            for i in range(antal):
                dato = start_dato + timedelta(weeks=i * interval)
                plan_data.append({
                    "title": str(row.get(k_navn, "Ukendt")),
                    "start": dato.strftime('%Y-%m-%d'),
                    "Konsulent": kons
                })
        
        st.session_state['df_plan'] = pd.DataFrame(plan_data)
        st.rerun()

    # --- 3. VISNING & DOWNLOAD ---
    if 'df_plan' in st.session_state:
        df_plan = st.session_state['df_plan']
        
        # Konsulent-vælger
        valgt = st.selectbox("Vælg konsulent:", sorted(df_plan['Konsulent'].unique()))
        df_filt = df_plan[df_plan['Konsulent'] == valgt]
        
        # Vis kalender
        calendar(events=df_filt.to_dict('records'), options={"initialView": "dayGridMonth", "locale": "da"})
        
        # ICS Download
        cal = Calendar()
        for _, r in df_filt.iterrows():
            ev = Event()
            ev.add('summary', r['title'])
            ev.add('dtstart', datetime.strptime(r['start'], '%Y-%m-%d').date())
            cal.add_component(ev)
            
        st.download_button(
            label=f"📥 Download .ics plan for {valgt}",
            data=cal.to_ical(),
            file_name=f"Ruteplan_{valgt}.ics",
            mime="text/calendar"
        )

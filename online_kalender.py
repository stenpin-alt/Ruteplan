import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from streamlit_calendar import calendar

st.set_page_config(
    page_title="Lynhurtig Ruteplanlægger - Online Kalender",
    layout="wide"
)
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger (Med Online Kalender)")

# --- 1. INDSTILLINGER ---
st.header("📂 1. Upload Data & Vælg Arbejdsdage")
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    kunde_fil = st.file_uploader(
        "Upload Kundeliste (Excel)",
        type=["xlsx", "xls"]
    )
with col2:
    konsulent_fil = st.file_uploader(
        "Upload Konsulentliste (Excel - Valgfri)",
        type=["xlsx", "xls"]
    )
with col3:
    arbejdsdage_valg = st.selectbox(
        "Hvor mange dage om ugen køres der?",
        options=[
            "5 dage (Mandag - Fredag)",
            "3 dage (Mandag, Tirsdag, Onsdag)",
            "3 dage (Tirsdag - Torsdag)",
            "2 dage (Tirsdag & Torsdag)"
        ]
    )

if "5 dage" in arbejdsdage_valg:
    standard_tilladte = [0, 1, 2, 3, 4]
elif "Tirsdag - Torsdag" in arbejdsdage_valg:
    standard_tilladte = [1, 2, 3]
elif "Mandag, Tirsdag, Onsdag" in arbejdsdage_valg:
    standard_tilladte = [0, 1, 2]
else:
    standard_tilladte = [1, 3]

# STRIKT LOFT pr. dag pr. konsulent
MAX_BESOEG_PR_DAG = 7

def definer_zone_ud_fra_postnummer(pnr_val):
    try:
        pnr = int(''.join(filter(str.isdigit, str(pnr_val))))
    except:
        return "Z_UKENDT_OMRÅDE"
        
    if 1000 <= pnr <= 2999:
        return "Z_STORKØBENHAVN_NORDSJÆLLAND"
    elif 3000 <= pnr <= 3699:
        return "Z_NORDSJÆLLAND_FJORDE"
    elif 3700 <= pnr <= 3799:
        return "Z_BORNHOLM"
    elif 4000 <= pnr <= 4999:
        if pnr in [4200, 4220, 4230, 4241, 4242, 4243]: return "Z_SLAGELSE_OMRÅDE"
        if pnr in [4300, 4400, 4420, 4440, 4450, 4460, 4470, 4480, 4490]: return "Z_KALUNDBORG_OMRÅDE"
        if pnr in [4500, 4520, 4532, 4534, 4540, 4550, 4560, 4571, 4572, 4573, 4581, 4583, 4591, 4592, 4593]: return "Z_HOLBÆK_ODSHERRED"
        return "Z_MIDT_SYDSJÆLLAND_LOLLAND"
    elif 5000 <= pnr <= 5999:
        return "Z_FYN_ØERNE"
    elif 6000 <= pnr <= 6999:
        return "Z_SYD_SØNDERJYLLAND"
    elif 7000 <= pnr <= 7999:
        return "Z_MIDT_VESTJYLLAND"
    elif 8000 <= pnr <= 8999:
        return "Z_ØSTJYLLAND"
    elif 9000 <= pnr <= 9999:
        return "Z_NORDJYLLAND"
    else:
        return "Z_DANMARK_UDLAND"

def afgør_specifikke_dage(lev_dage_streng):
    s = str(lev_dage_streng).lower()
    if pd.isna(lev_dage_streng) or s == "nan" or s.strip() == "":
        return None
        
    dage = []
    if "man" in s: dage.append(0)
    if "tir" in s: dage.append(1)
    if "ons" in s: dage.append(2)
    if "tor" in s: dage.append(3)
    if "fre" in s: dage.append(4)
    
    if "-" in s or "til" in s:
        if "tirs" in s and "tors" in s:
            return [1, 2, 3]
        if "man" in s and "tors" in s:
            return [0, 1, 2, 3]
        if "ons" in s and "fre" in s:
            return [2, 3, 4]
            
    return dage if dage else None

# --- 2. LOGIK ---
if kunde_fil:
    try:
        df_kunder = pd.read_excel(kunde_fil, skiprows=2)
        df_kunder.columns = df_kunder.columns.astype(str).str.strip()
        
        k_konsulent = "Konsulent" if "Konsulent" in df_kunder.columns else df_kunder.columns[0]
        k_navn = "Navn" if "Navn" in df_kunder.columns else None
        k_by = "By" if "By" in df_kunder.columns else None
        k_frek = "Besøgs frekvens" if "Besøgs frekvens" in df_kunder.columns else None
        k_dage = "Lev. Dage 365" if "Lev. Dage 365" in df_kunder.columns else None
        k_postnr = "Postnr" if "Postnr" in df_kunder.columns else ("Postnummer" if "Postnummer" in df_kunder.columns else None)

        if not k_postnr:
            for c in df_kunder.columns:
                if "post" in c.lower() or "pnr" in c.lower(): k_postnr = c; break

        if not k_navn or not k_by or not k_postnr:
            st.error("Kunne ikke matche de nødvendige kolonner ('Navn', 'By', 'Postnr') i Excel-arket.")
        else:
            st.success("Excel-filen blev indlæst korrekt!")
            
            st.header("🗓️ 2. Generer Lynhurtig Årsplan (52 Uger)")
            if st.button("Lyn-generer 52-Ugers Plan", type="primary"):
                with st.spinner("Beregner og fordeler ruter automatisk..."):
                    basis_plan_4_uger = []
                    dag_navne = {0: "Mandag", 1: "Tirsdag", 2: "Onsdag", 3: "Torsdag", 4: "Fredag"}
                    
                    df_kunder_sorted = df_kunder.copy()
                    df_kunder_sorted['Zone_Tmp'] = df_kunder_sorted[k_postnr].apply(definer_zone_ud_fra_postnummer)
                    df_kunder_sorted = df_kunder_sorted.sort_values(by=[k_konsulent, 'Zone_Tmp', k_postnr, k_by])
                    
                    konsulent_slots = {}
                    
                    for idx, kunde in df_kunder_sorted.iterrows():
                        val_navn = kunde[k_navn]
                        val_by = kunde[k_by]
                        val_postnr = kunde[k_postnr]
                        val_konsulent = kunde[k_konsulent]
                        
                        if pd.isna(val_navn) or pd.isna(val_by) or pd.isna(val_konsulent):
                            continue
                        if "vejledning" in str(val_navn).lower() or "kunde nr" in str(val_navn).lower():
                            continue
                        
                        ansvarlig = str(val_konsulent).strip()
                        if responsibility_check := ansvarlig not in konsulent_slots:
                            konsulent_slots[ansvarlig] = {u: {d: 0 for d in range(5)} for u in range(1, 5)}
                        
                        frekvens = 0.25
                        if k_frek and not pd.isna(kunde[k_frek]):
                            try:
                                frekvens = float(str(kunde[k_frek]).replace(',', '.'))
                            except:
                                frekvens = 0.25
                        
                        ønskede_uger = []
                        if frekvens >= 1.0: ønskede_uger = [1, 2, 3, 4]
                        elif frekvens == 0.5: ønskede_uger = [1, 3]
                        else: ønskede_uger = [1]
                        
                        specifikke_dage = afgør_specifikke_dage(kunde.get(k_dage))
                        valgmuligheder_dage = specifikke_dage if specifikke_dage else standard_tilladte
                        
                        for basis_uge in ønskede_uger:
                            placeret = False
                            aktuel_uge = basis_uge
                            
                            while not placeret and aktuel_uge <= 4:
                                sorteret_dage = sorted(valgmuligheder_dage, key=lambda d: konsulent_slots[ansvarlig][aktuel_uge][d])
                                
                                for dag_valg in sorteret_dage:
                                    if konsulent_slots[ansvarlig][aktuel_uge][dag_valg] < MAX_BESOEG_PR_DAG:
                                        konsulent_slots[ansvarlig][aktuel_uge][dag_valg] += 1
                                        basis_plan_4_uger.append({
                                            "Kundenavn": val_navn,
                                            "By": val_by,
                                            "Postnr": val_postnr,
                                            "Zone": kunde['Zone_Tmp'],
                                            "Konsulent": ansvarlig,
                                            "Frekvens": frekvens,
                                            "UgeNum": aktuel_uge,
                                            "Dag": dag_navne[dag_valg]
                                        })
                                        placeret = True
                                        break
                                
                                if not placeret:
                                    aktuel_uge += 1
                                    
                        if not placeret:
                            nød_uge = basis_uge
                            sorteret_dage = sorted(valgmuligheder_dage, key=lambda d: konsulent_slots[ansvarlig][nød_uge][d])
                            nød_dag = sorteret_dage[0]
                            konsulent_slots[ansvarlig][nød_uge][nød_dag] += 1
                            basis_plan_4_uger.append({
                                "Kundenavn": val_navn,
                                "By": val_by,
                                "Postnr": val_postnr,
                                "Zone": kunde['Zone_Tmp'],
                                "Konsulent": ansvarlig,
                                "Frekvens": frekvens,
                                "UgeNum": nød_uge,
                                "Dag": dag_navne[nød_dag]
                            })
                    
                    endelig_52_plan = []
                    for element in basis_plan_4_uger:
                        start_uge = element["UgeNum"]
                        freq = element["Frekvens"]
                        
                        if freq >= 1.0: spring = 1
                        elif freq == 0.5: spring = 2
                        else: spring = 4
                        
                        for uge_tæller in range(start_uge, 53, spring):
                            kopi = element.copy()
                            kopi["UgeNum"] = uge_tæller
                            kopi["Uge"] = f"Uge {uge_tæller}"
                            endelig_52_plan.append(kopi)
                    
                    st.session_state['df_plan_fast'] = pd.DataFrame(endelig_52_plan)
                    st.success("Færdig! Årsplanen er genereret.")

            # --- 3. LIVE ONLINE KALENDER (NY SEKTION) ---
            if 'df_plan_fast' in st.session_state and not st.session_state['df_plan_fast'].empty:
                df_plan = st.session_state['df_plan_fast']
                
                st.markdown("---")
                st.header("📅 3. Online Ruteskema (Direkte i browser)")
                
                # Vælg konsulent for at filtrere kalenderen live
                unikke_konsulenter = sorted(df_plan['Konsulent'].unique())
                valgt_konsulent = st.selectbox("Vælg konsulent for at se kalender:", options=unikke_konsulenter)
                
                df_konsulent = df_plan[df_plan['Konsulent'] == valgt_konsulent]
                
                # Dato-beregninger baseret på din eksisterende logik
                idag = datetime.now()
                dage_til_man = (0 - idag.weekday()) % 7
                if dage_til_man == 0: dage_til_man = 7
                start_mandag = idag + timedelta(days=dage_til_man)
                dag_kort = {"Mandag": 0, "Tirsdag": 1, "Onsdag": 2, "Torsdag": 3, "Fredag": 4}
                
                kalender_events = []
                for idx, række in df_konsulent.iterrows():
                    try:
                        uge_num = int(str(række['Uge']).replace("Uge", "").strip()) - 1
                    except:
                        uge_num = 0
                        
                    basis_mandag = start_mandag + timedelta(weeks=uge_num)
                    ekstra_dage = dag_kort.get(str(række['Dag']).strip(), 0)
                    mødedato = basis_mandag + timedelta(days=ekstra_dage)
                    
                    dato_str = mødedato.strftime("%Y-%m-%d")
                    
                    kalender_events.append({
                        "title": f"🚚 {række['Kundenavn']}",
                        "start": dato_str,
                        "end": dato_str,
                        "allDay": True,
                        "extendedProps": {
                            "by": række['By'],
                            "zone": række['Zone'],
                            "postnr": række['Postnr'],
                            "frekvens": række['Frekvens']
                        }
                    })
                
                # Kalenderindstillinger på dansk
                calendar_options = {
                    "initialView": "dayGridMonth",
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,listWeek"
                    },
                    "locale": "da",
                    "firstDay": 1,
                    "buttonText": {
                        "today": "I dag",
                        "month": "Måned",
                        "list": "Liste"
                    }
                }
                
                custom_css = """
                    .fc-event { cursor: pointer; padding: 2px; font-size: 0.85em; }
                    .fc-header-toolbar { flex-wrap: wrap; gap: 5px; }
                """
                
                # Render selve online-kalenderen på skærmen
                state = calendar(events=kalender_events, options=calendar_options, custom_css=custom_css)
                
                # Hvis konsulenten klikker på et besøg, vis detaljer
                if state.get("eventClick"):
                    props = state["eventClick"]["event"]["extendedProps"]
                    st.info(
                        f"### 📍 Detaljer for valgt rute:\n"
                        f"**Kunde:** {state['eventClick']['event']['title'].replace('🚚 ', '')}\n\n"
                        f"🏠 **Adresse:** {props['postnr']} {props['by']}\n\n"
                        f"🗺️ **Zone:** {props['zone']} *(Frekvens: {props['frekvens']})*"
                    )
                    
                st.markdown("---")
                st.subheader("📋 Samlet tabeloversigt (Hele året)")
                df_vis = df_plan.copy()
                dag_sortering = {"Mandag": 1, "Tirsdag": 2, "Onsdag": 3, "Torsdag": 4, "Fredag": 5}
                df_vis["DagSortering"] = df_vis["Dag"].map(lambda x: dag_sortering.get(str(x), 9))
                df_vis = df_vis.sort_values(by=["Konsulent", "UgeNum", "DagSortering", "Zone", "Postnr"])
                df_vis_Clean = df_vis.drop(columns=["UgeNum", "DagSortering"]).reset_index(drop=True)
                
                st.dataframe(df_vis_Clean, use_container_width=True)

    except Exception as e:
        st.error(f"Fejl under kørsel: {e}")
else:
    st.info("Upload din kundeliste med postnumre for at starte beregningen.")
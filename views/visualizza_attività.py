import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text
from utils import functions as f

def show():
    st.title("📅 Visualizza attività")

    c1, c2, c3 = st.columns([0.6, 0.2, 0.2], vertical_alignment = 'bottom')

    with c1:
        filter_denominazione_VA = st.text_input("Denominazione attività")

    with c2:
        filter_ordine_VA = st.selectbox("Ordine", ['Decrescente', 'Crescente'])

    with c3:
        filter_solo_prenotate_VA = st.toggle('Mostra solo prenotate')

    if filter_ordine_VA == 'Decrescente':
        filter_ordine_VA = 'DESC'
    elif filter_ordine_VA == 'Crescente':
        filter_ordine_VA = 'ASC'

    query = f'''SELECT *
                FROM TBL_ATTIVITA
                WHERE CURRENT_TIMESTAMP < TIMESTAMP(Data, Ora_fine) AND
                    Denominazione LIKE '%{filter_denominazione_VA}%'
                ORDER BY Data {filter_ordine_VA}, Ora_inizio
                '''
    
    df_attività = pd.read_sql(query, st.session_state.engine)

    query = f'''SELECT *
                FROM TBL_PRENOTAZIONI
                WHERE CF_socio = '{st.session_state.CF_socio}'
                '''
    
    df_attività_prenotate = pd.read_sql(query, st.session_state.engine)

    if filter_solo_prenotate_VA:
        attività_prenotate_set = set(df_attività_prenotate['Attività'])
        df_attività = df_attività[df_attività['Denominazione'].isin(attività_prenotate_set)]

        if df_attività.empty:
            st.info("🔍 Nessuna attività prenotata trovata con i filtri selezionati.")

    query = '''SELECT Attività, COUNT(*) AS num_prenotazioni
           FROM TBL_PRENOTAZIONI
           GROUP BY Attività
        '''
    df_num_prenotazioni = pd.read_sql(query, st.session_state.engine)

    for _, a in df_attività.iterrows():
        with st.container(border = True):
            st.subheader(a['Denominazione'])

            c1, c2, c3 = st.columns([0.3, 0.4, 0.3], vertical_alignment = 'center')

            with c1:
                st.write(f"📆 {a['Data'].strftime('%d-%m-%Y')}")
                st.write(f"🕑 {(datetime.datetime.min + a['Ora_inizio']).time().strftime('%H:%M')} - {(datetime.datetime.min + a['Ora_fine']).time().strftime('%H:%M')}")

            with c2:
                st.write(f":gray[{a['Descrizione']}]")

            with c3:
                isPrenotata = False

                for _, ap in df_attività_prenotate.iterrows():
                    if ap['Attività'] == a['Denominazione']:
                        isPrenotata = True
                        break

                riga_prenotazioni = df_num_prenotazioni[df_num_prenotazioni['Attività'] == a['Denominazione']]
                num_prenotazioni = int(riga_prenotazioni['num_prenotazioni'].iloc[0]) if not riga_prenotazioni.empty else 0

                max_partecipanti = a['Max_partecipanti']

                if max_partecipanti is not None and not pd.isna(max_partecipanti):
                    max_partecipanti = int(max_partecipanti)
                    st.write(f":gray[{num_prenotazioni}/{max_partecipanti} posti occupati]")
                else:
                    st.write(f":gray[{num_prenotazioni} partecipanti]")

                if isPrenotata:
                    st.write(":red[Sei prenotato!]")

                    if st.button('Annulla prenotazione', icon = '❌', use_container_width=True, key=f"{a['Denominazione']} - annulla"):
                        query = text('''DELETE FROM TBL_PRENOTAZIONI
                                        WHERE CF_socio = :cf AND Attività = :attività''')

                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'cf': st.session_state.CF_socio,
                                'attività': a['Denominazione']
                            })

                            conn.commit()

                        st.rerun()

                    if st.button('Aggiungi al calendario', icon='📆', use_container_width=True, key=f"{a['Denominazione']} - calendar"):
                        ics_file = f.genera_ics(a)
                        st.download_button("Scarica .ics", data=ics_file, file_name=f"{a['Denominazione']}.ics")

                elif max_partecipanti is None or pd.isna(max_partecipanti) or num_prenotazioni < max_partecipanti:
                    prenota = st.button('Prenota', use_container_width=True, key=f"{a['Denominazione']} - prenota")

                    if prenota:
                        query = text('''INSERT INTO TBL_PRENOTAZIONI (CF_socio, Attività)
                                        VALUES (:cf, :attività)''')

                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'cf': st.session_state.CF_socio,
                                'attività': a['Denominazione']
                            })
                            conn.commit()

                        st.rerun()
                else:
                    st.write(":red[Posti esauriti per questa attività.]")
import streamlit as st
import pandas as pd
from sqlalchemy import text

def show():
    st.title("🛠️ Gestisci segnalazioni")

    query = f'''SELECT *
                FROM TBL_SEGNALAZIONI
                WHERE Stato = 'Aperta' OR
                    Stato = 'In lavorazione'
                ORDER BY 
                    FIELD(Priorità, 'Da impostare', 'Alta', 'Media', 'Bassa'), Data_creazione ASC;
            '''

    df_segnalazioni = pd.read_sql(query, st.session_state.engine)

    for _, s in df_segnalazioni.iterrows():
        with st.container(border = True):
            icon = ""

            if s['Priorità'] == 'Da impostare':
                icon = "#️⃣"
            elif s['Priorità'] == 'Alta':
                icon = "🔴"
            elif s['Priorità'] == 'Media':
                icon = "🟡"
            else:
                icon = "🟢"

            st.subheader(f"{icon} - {s['Titolo']}")

            c1, c2 = st.columns([0.7, 0.3])

            with c1:
                with st.container(border = True, height = 200):
                    st.write(s['Testo'])

            with c2:
                priorità = []

                if s['Priorità'] == 'Da impostare':
                    priorità = ['Da impostare', 'Alta', 'Media', 'Bassa']
                elif s['Priorità'] == 'Alta':
                    priorità = ['Alta', 'Media', 'Bassa']
                elif s['Priorità'] == 'Media':
                    priorità = ['Media', 'Alta', 'Bassa']
                else:
                    priorità = ['Bassa', 'Alta', 'Media']

                slc_priorità = st.selectbox("Imposta priorità", priorità, key = f"{s['ID_segnalazione']} - priorità")

                if slc_priorità != s['Priorità']:
                    query = text('''UPDATE TBL_SEGNALAZIONI
                                        SET Priorità = :priorità
                                        WHERE ID_segnalazione = :ID_segnalazione;
                                        ''')
                        
                    with st.session_state.engine.connect() as conn:
                        conn.execute(query, {
                            'priorità': slc_priorità,
                            'ID_segnalazione': s['ID_segnalazione']
                        })

                        conn.commit()

                    st.rerun()

                if s['Gestito_da'] == None:
                    btn_prendi_in_carico = st.button("Prendi in carico", key = f"{s['ID_segnalazione']} - presa_in_carico", use_container_width = True)

                    if btn_prendi_in_carico:
                        query = text('''UPDATE TBL_SEGNALAZIONI
                                        SET Gestito_da = :gestito_da
                                        WHERE ID_segnalazione = :ID_segnalazione;
                                        ''')
                        
                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'gestito_da': st.session_state.user,
                                'ID_segnalazione': s['ID_segnalazione']
                            })

                            conn.commit()

                        query = text('''UPDATE TBL_SEGNALAZIONI
                                        SET Stato = :stato
                                        WHERE ID_segnalazione = :ID_segnalazione;
                                        ''')
                        
                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'stato': 'In lavorazione',
                                'ID_segnalazione': s['ID_segnalazione']
                            })

                            conn.commit()

                        st.rerun()

                else:
                    st.write(f'Gestita da :red[{s["Gestito_da"]}] - :gray[{st.session_state.role}]')

                btn_imposta_come_risolta = st.button("Imposta come risolta", key = f"{s['ID_segnalazione']} - imposta_come_risolta", use_container_width = True, type = "primary")

                if btn_imposta_come_risolta:
                    query = text('''UPDATE TBL_SEGNALAZIONI
                                        SET Stato = :stato
                                        WHERE ID_segnalazione = :ID_segnalazione;
                                        ''')
                        
                    with st.session_state.engine.connect() as conn:
                        conn.execute(query, {
                            'stato': 'Risolta',
                            'ID_segnalazione': s['ID_segnalazione']
                        })

                        conn.commit()

                    st.rerun()

            st.write(f":gray[User: {s['Creato_da']}]")
            st.write(f":gray[Data creazione: {s['Data_creazione'].strftime('%d-%m-%Y')} - {s['Data_creazione'].strftime('%H:%M:%S')}]")
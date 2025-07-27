import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import text

def show():
    utenti = pd.read_sql("SELECT * FROM TBL_UTENTI", st.session_state.engine)

    st.title("🔑 Login")

    with st.form(key = "form_login", clear_on_submit = True, enter_to_submit = True):
        input_username_FL = st.text_input(label = "Username")
        input_password_FL = st.text_input(label = "Password", type = "password")

        submitted = st.form_submit_button(label = "Log in", use_container_width = True)

        if submitted:
            user_row = utenti[utenti['Username'] == input_username_FL]

            if user_row.empty:
                st.error("Utente non trovato", icon = "🚨")
            else:
                st.session_state.CF_socio = user_row.iloc[0]['CF_socio']

                query = '''SELECT CF_socio
                                FROM TBL_PARTECIPAZIONI_TEAM
                                '''
                    
                df_utenti_team = pd.read_sql(query, st.session_state.engine)

                for _, ut in df_utenti_team.iterrows():
                    if st.session_state.CF_socio == ut['CF_socio']:
                        st.session_state.inTeam = True
                        break

                # Prendi l'hash salvato nel DB
                hashed_password = user_row.iloc[0]['Password_hash'].strip()

                # Verifica la password (solo se è stata inserita)
                if input_password_FL and bcrypt.checkpw(input_password_FL.encode('utf-8'), hashed_password.encode('utf-8')):
                    st.session_state.user = input_username_FL

                    for r in pd.read_sql(f"SELECT Ruolo FROM TBL_RUOLI WHERE Username = '{input_username_FL}'", st.session_state.engine)["Ruolo"]:
                        st.session_state.role = r

                    if pd.isna(pd.read_sql(f"SELECT Ultimo_login FROM TBL_UTENTI WHERE Username = '{input_username_FL}'", st.session_state.engine)['Ultimo_login'].iloc[0]):
                        st.session_state.current_page = "Cambia credenziali"
                    else:
                        st.session_state.logged = True
                        st.session_state.current_page = "Bacheca"

                        with st.session_state.engine.begin() as conn:
                            conn.execute(
                                text("UPDATE TBL_UTENTI SET Ultimo_login = CURRENT_TIMESTAMP WHERE Username = :username"),
                                {"username": input_username_FL}
                            )

                        st.rerun()

                else:
                    st.error("Password errata", icon = "🚨")
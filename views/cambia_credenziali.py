import streamlit as st
import pandas as pd
from utils import consts as c, functions as f
import bcrypt
from sqlalchemy import text

def show():
    st.title("🔄️ Cambia credenziali")

    if st.session_state.user == "master":
        st.subheader(":red[ATTENZIONE: Continuare solo se si è sicuri di quelo che si sta facendo.]")

    with st.form("form_cambia_credenziali", enter_to_submit = True):
        input_username_CC = st.text_input(label = "Nuovo username")
        input_newPassword_CC = st.text_input(label = "Nuova password", type = "password", placeholder = "Requisiti: 8+ caratteri, maiuscola, minuscola, numero, simbolo")
        input_oldPassword_CC = st.text_input(label = "Vecchia password", type = "password")

        submitted = st.form_submit_button("Cambia credenziali")

    if submitted:
        # Recupera l'hash salvato dal database
        df = pd.read_sql(
            "SELECT Password_hash FROM TBL_UTENTI WHERE Username = %(username)s",
            st.session_state.engine,
            params = {"username": st.session_state.user}
        )

        if df.empty:
            st.error("Utente non trovato", icon = "🚨")
        else:
            err = []

            if c.policy.test(input_newPassword_CC):
                err.append("La password non rispetta i requisiti")

            if input_username_CC == '':
                err.append("Il campo username non può essere vuoto")

            query = '''SELECT Username
                       FROM TBL_UTENTI
                    '''
            
            search_username = pd.read_sql(query, st.session_state.engine)
            
            if not search_username[search_username['Username'] == input_username_CC].empty:
                err.append("Esiste già un utente con questo username")

            if err:
                for e in err:
                    st.error(e, icon = "🚨")
            else:
                st.session_state.CF_socio = input_username_CC

                saved_hash = df.iloc[0]['Password_hash']

                # Verifica che la vecchia password inserita sia corretta
                if bcrypt.checkpw(input_oldPassword_CC.encode('utf-8'), saved_hash.encode('utf-8')):
                    # Crea hash della nuova password
                    new_hashed = f.hash_password(input_newPassword_CC)

                    # Aggiorna il database: username + password
                    with st.session_state.engine.connect() as conn:
                        conn.execute(
                            text("""
                                UPDATE TBL_UTENTI
                                SET Username = :new_username,
                                    Password_hash = :new_password
                                WHERE Username = :old_username
                            """),
                            {
                                "new_username": input_username_CC,
                                "new_password": new_hashed,
                                "old_username": st.session_state.user
                            }
                        )
                        conn.commit()

                    with st.session_state.engine.connect() as conn:
                                conn.execute(
                                    text("UPDATE TBL_UTENTI SET Ultimo_login = CURRENT_TIMESTAMP WHERE Username = :username"),
                                    {"username": input_username_CC}
                                )
                                conn.commit()

                    st.session_state.user = input_username_CC
                    st.session_state.logged = True
                    st.session_state.current_page = "Bacheca"
                    st.rerun()
                else:
                    st.error("Vecchia password errata", icon = "🚨")
import streamlit as st
import datetime
from utils import consts as c, functions as f
from sqlalchemy import text

def show():
    st.title("➕ Inserisci anagrafica")
    
    with st.form(key = "form_inserisci_anagrafica", clear_on_submit = True, enter_to_submit = False):
        input_CF_IA = st.text_input(label = "Codice fiscale del socio*", max_chars = 16, placeholder = "AAAAAA00A00A000A")

        c1, c2 = st.columns(2)

        with c1:
            input_nome_IA = st.text_input(label = "Nome del socio*", max_chars = 60)

        with c2:
            input_cognome_IA = st.text_input(label = "Cognome del socio*", max_chars = 60)

        c1, c2, c3 = st.columns(3)

        with c1:
            input_dataNascita_IA = st.date_input(label = "Data di nascita del socio*", min_value = datetime.date(1000, 1, 1), max_value = datetime.date(3000, 1, 1))

        with c2:
            input_luogoNascita_IA = st.text_input(label = "Luogo di nascita del socio*", max_chars = 60)

        with c3:
            input_sesso_IA = st.selectbox(label = "Sesso del socio*", options = ["M", "F", "ND"])

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            input_indirizzo_IA = st.text_input(label = "Indirizzo*", max_chars = 100, placeholder = "No virgole   Es: strada dei pioppi 5")

        with c2:
            input_città_IA = st.text_input(label = "Città*", max_chars = 60)

        with c3:
            input_provincia_IA = st.selectbox(label = "Provincia*", options = c.province_sigle)

        with c4:
            input_CAP_IA = st.text_input(label = "CAP*", max_chars = 5, placeholder = "00000")

        c1, c2, = st.columns(2)

        with c1:
            input_cellulare_IA = st.text_input(label = "Cellulare del socio", max_chars = 13, placeholder = "+000000000000")

        with c2:
            input_email_IA = st.text_input(label = "Email del soci*", max_chars = 100)

        is_inserisci = st.form_submit_button(label = "Inserisci", use_container_width = True, icon = "➕")

    if is_inserisci:
        err = []

        for inpt in [input_nome_IA, input_cognome_IA, input_dataNascita_IA, input_luogoNascita_IA, input_indirizzo_IA, input_città_IA, input_email_IA]:
            if inpt == '':
                err.append("I campi contrassegnati con * non possono essere lasciati vuoti")
                break

        if len(input_CF_IA) != 16:
            err.append("Codice fiscale non valido")

        if len(input_CAP_IA) != 5:
            err.append("CAP non valido")

        if input_cellulare_IA == "":
            input_cellulare_IA = None
        elif len(input_cellulare_IA) != 13 or input_cellulare_IA[0] != '+':
            err.append("Cellulare non valido")

        if err:
            for e in err:
                st.error(e, icon = "🚨")
        else:
            query = text('''INSERT INTO TBL_ANAGRAFICHE (CF, Nome, Cognome, Data_nascita, Luogo_nascita, Sesso, Indirizzo, Città, Provincia, CAP, Cellulare, Email)
                    VALUES (:CF, :Nome, :Cognome, :Data_nascita, :Luogo_nascita, :Sesso, :Indirizzo, :Città, :Provincia, :CAP, :Cellulare, :Email);
                    ''')
            
            with st.session_state.engine.connect() as conn:
                conn.execute(query, {
                    "CF": input_CF_IA,
                    "Nome": input_nome_IA,
                    "Cognome": input_cognome_IA,
                    "Data_nascita": input_dataNascita_IA,
                    "Luogo_nascita": input_luogoNascita_IA,
                    "Sesso": input_sesso_IA,
                    "Indirizzo": input_indirizzo_IA,
                    "Città": input_città_IA,
                    "Provincia": input_provincia_IA,
                    "CAP": input_CAP_IA,
                    "Cellulare": input_cellulare_IA,
                    "Email": input_email_IA
                })

                conn.commit()

            st.success(f"{input_nome_IA} {input_cognome_IA} è stato correttamente inserito nel database", icon = "✅")

            hashed_password = f.hash_password(input_CF_IA)

            query1 = text("""
                INSERT INTO TBL_UTENTI (Username, CF_socio, Password_hash, Ultimo_login)
                VALUES (:username, :cf_socio, :password, :ultimo_login);
            """)

            query2 = text("""
                INSERT INTO TBL_RUOLI (Username, Ruolo)
                VALUES (:username, 'Utente standard');
            """)

            params1 = {
                "username": f"{input_nome_IA}_{input_cognome_IA}",
                "cf_socio": input_CF_IA,
                "password": hashed_password,
                "ultimo_login": None,
                "username2": f"{input_nome_IA}_{input_cognome_IA}"
            }

            params2 = {
                "username": f"{input_nome_IA}_{input_cognome_IA}",
            }

            with st.session_state.engine.connect() as conn:
                conn.execute(query1, params1)
                conn.execute(query2, params2)
                conn.commit()

            f.send_email(
                "Registrazione a SPIKKIO!",
                f"Benvenuto nella famiglia di SPIKKIO!\n\nEcco a te le tue credenziali:\n\n       👤 Username: {input_nome_IA}_{input_cognome_IA}\n      ✳️ Password: {input_CF_IA}",
                input_email_IA,
                "mattia1052004@gmail.com",
                st.secrets["EMAIL_PASSWORD"]
            )

            st.success(f"Email con le credenziali inviata", icon = "✅")

            with st.container(border = True):
                st.subheader("Si vuole tesserare il socio appena inserito?")
                c1, c2 = st.columns(2)

                with c1:
                    st.button(label = "Sì", use_container_width = True, on_click = lambda: st.session_state.update(current_page = "Tesseramento"))

                with c2:
                    st.button(label = "No", use_container_width = True, on_click = lambda: st.session_state.update(current_page = "Inserisci anagrafica"), type = "primary")
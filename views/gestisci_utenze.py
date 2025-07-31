import streamlit as st
import pandas as pd
import datetime

def show():
    st.title("⚙️ Gestisci utenze")

    if "master" in st.session_state.role:
        _anagrafiche = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE", st.session_state.engine)
    else:
        df_anagrafiche = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE WHERE Attivo = TRUE", st.session_state.engine)
        df_anagrafiche = df_anagrafiche.drop(columns = ['Attivo'])

    for _, a in df_anagrafiche.iterrows():
        with st.container(border = True):
            st.subheader(f"👤 {a['Nome']} {a['Cognome']} - :gray[{a['CF']}]")

            st.write("")

            c1, c2 = st.columns(2)

            with c1:
                st.write(f"📆 Data di nascita: :gray[{a['Data_nascita'].strftime('%d/%m/%Y')}]")
                st.write(f"📍 Luogo di nascita: :gray[{a['Luogo_nascita']}]")
                st.write(f"⚧️ Sesso: :gray[{a['Sesso']}]")

            with c2:
                st.write(f"🏠 Indirizzo: :gray[{a['Indirizzo']}, {a['CAP']}, {a['Città']}, {a['Provincia']}]")
                st.write(f"📱 Cellulare: :gray[{a['Cellulare']}]")
                st.write(f"✉️ Email: :gray[{a['Email']}]")

            with st.form(f"form_modifica_anagrafica_{a['CF']}", clear_on_submit = True):
                c1, c2, c3 = st.columns([2, 2, 3])

                with c1:
                    input_nome_GU = st.text_input("Nome", max_chars = 60)

                with c2:
                    input_cognome_GU = st.text_input("Cognome", max_chars = 60)

                with c3:
                    input_CF_GU = st.text_input('Codice fiscale', max_chars = 16, placeholder = 'AAAAAA00A00A000A')

                c1, c2 = st.columns(2)

                with c1:
                    input_dataNascita_GU = st.date_input(label = "Data di nascita", min_value = datetime.date(1000, 1, 1), max_value = datetime.date(3000, 1, 1))

                    input_luogoNascita_IA = st.text_input(label = "Luogo di nascita", max_chars = 60)

                    input_sesso_IA = st.selectbox(label = "Sesso", options = ["", "M", "F", "ND"])

                with c2:
                    pass

                submitted = st.form_submit_button("Submit", use_container_width = True)

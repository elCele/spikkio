import streamlit as st
import pandas as pd
import datetime
from utils import consts as c
from sqlalchemy import text

def show():
    st.title("🔍 Visualizza anagrafiche")

    with st.expander("Filtri", expanded = False):
        filter_CF_VS = st.text_input(label = "Codice fiscale", placeholder = "AAAAAA00A00A000A")

        c1, c2 = st.columns(2)

        with c1:
            filter_nome_VS = st.text_input(label = "Nome")

        with c2:
            filter_cognome_VS = st.text_input(label = "Cognome")

        c1, c2, c3 = st.columns(3)

        with c1:
            filter_dataNascita_VS = st.date_input(label = "Data di nascita", min_value = datetime.date(1000, 1, 1), max_value = datetime.date(3000, 1, 1), value = (datetime.date(1000, 1, 1), datetime.date(3000, 1, 1)))

        with c2:
            filter_luogoNascita_VS = st.text_input(label = "Luogo di nascita")

        with c3:
            filter_sesso_VS = st.selectbox(label = "Sesso", options = ["", "M", "F", "ND"])

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            filter_indirizzo_VS = st.text_input(label = "Indirizzo")

        with c2:
            filter_città_VS = st.text_input(label = "Città")

        with c3:
            filter_provincia_VS = st.selectbox(label = "Provincia", options = c.province_sigle)

        with c4:
            filter_CAP_VS = st.text_input(label = "CAP", placeholder = "00000")

        c1, c2, = st.columns(2)

        with c1:
            filter_cellulare_VS = st.text_input(label = "Cellulare del socio", placeholder = "+000000000000")

        with c2:
            filter_email_VS = st.text_input(label = "Email del socio")

        filters = []
        params = {}

        if filter_CF_VS:
            filters.append("CF LIKE :cf")
            params["cf"] = f"%{filter_CF_VS}%"

        if filter_nome_VS:
            filters.append("Nome LIKE :nome")
            params["nome"] = f"%{filter_nome_VS}%"

        if filter_cognome_VS:
            filters.append("Cognome LIKE :cognome")
            params["cognome"] = f"%{filter_cognome_VS}%"

        if filter_dataNascita_VS:
            filters.append("Data_nascita BETWEEN :data_nascita_from AND :data_nascita_to")
            params["data_nascita_from"] = filter_dataNascita_VS[0]
            params["data_nascita_to"] = filter_dataNascita_VS[1]

        if filter_luogoNascita_VS:
            filters.append("Luogo_nascita LIKE :luogo_nascita")
            params["luogo_nascita"] = f"%{filter_luogoNascita_VS}%"

        if filter_sesso_VS:
            filters.append("Sesso = :sesso")
            params["sesso"] = filter_sesso_VS

        if filter_indirizzo_VS:
            filters.append("Indirizzo LIKE :indirizzo")
            params["indirizzo"] = f"%{filter_indirizzo_VS}%"

        if filter_città_VS:
            filters.append("Città LIKE :città")
            params["città"] = f"%{filter_città_VS}%"

        if filter_provincia_VS:
            filters.append("Provincia = :provincia")
            params["provincia"] = filter_provincia_VS

        if filter_CAP_VS:
            filters.append("CAP LIKE :cap")
            params["cap"] = f"%{filter_CAP_VS}%"

        if filter_cellulare_VS:
            filters.append("Cellulare LIKE :cellulare")
            params["cellulare"] = f"%{filter_cellulare_VS}%"

        if filter_email_VS:
            filters.append("Email LIKE :email")
            params["email"] = f"%{filter_email_VS}%"

        base_query = "SELECT * FROM TBL_ANAGRAFICHE"

        if filters:
            if st.session_state.role == "master":
                base_query = "SELECT * FROM TBL_ANAGRAFICHE WHERE"
            else:
                base_query = "SELECT * FROM TBL_ANAGRAFICHE WHERE Attivo = TRUE AND "

            query = base_query + " AND ".join(filters)
        else:
            if st.session_state.role == "master":
                query = "SELECT * FROM TBL_ANAGRAFICHE"
            else:
                query = "SELECT * FROM TBL_ANAGRAFICHE WHERE Attivo = TRUE"

        df_anagrafiche = pd.read_sql(text(query), st.session_state.engine, params = params)

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
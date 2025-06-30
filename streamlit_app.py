import streamlit as st
import utils as u
import pandas as pd

u.initialize_var()

u.config_sidebar()

st.set_page_config(
        page_title = st.session_state.current_page,
        page_icon = "🍋",
        layout = "wide",
        initial_sidebar_state = "auto"
    )

# ------------------------ Log in page ------------------------

if st.session_state.current_page == "Log in":
    st.title("🔑 Login")

    with st.form(key = "form_login", clear_on_submit = True, enter_to_submit = True):
        input_username_FL = st.text_input(label = "Username")
        input_password_FL = st.text_input(label = "Password", type = "password")

        submitted = st.form_submit_button(label = "Submit", use_container_width = True)

        if submitted:
            if input_username_FL == st.secrets["ROOT_USERNAME"] and input_password_FL == st.secrets["ROOT_PASSWORD"]:
                st.session_state.user = "root"
                st.session_state.logged = True
                st.session_state.current_page = "Homepage"
                st.rerun()

# ------------------------ Homepage page ------------------------

if st.session_state.current_page == "Homepage":
    st.title("🍋 SPIKKIO")

# ------------------------ Inserisci anagrafica page ------------------------

if st.session_state.current_page == "Inserisci anagrafica":
    st.title("➕ Inserisci anagrafica")
    
    with st.form(key = "form_inserisci_anagrafica", clear_on_submit = True, enter_to_submit = False):
        input_cf_IA = st.text_input(label = "Codice fiscale del socio", max_chars = 16, placeholder = "AAAAAA00A00A000A")

        c1, c2 = st.columns(2)

        with c1:
            input_nome_IA = st.text_input(label = "Nome del socio", max_chars = 60)

        with c2:
            input_cognome_IA = st.text_input(label = "Cognome del socio", max_chars = 60)

        c1, c2, c3 = st.columns(3)

        with c1:
            input_dataNascita_IA = st.date_input(label = "Data di nascita del socio")

        with c2:
            input_luogoNascita_IA = st.text_input(label = "Luogo di nascita del socio", max_chars = 60)

        with c3:
            input_sesso_IA = st.selectbox(label = "Sesso del socio", options = ["M", "F", "ND"])

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            input_indirizzo_IA = st.text_input(label = "Indirizzo", max_chars = 100)

        with c2:
            input_città_IA = st.text_input(label = "Città", max_chars = 60)

        with c3:
            input_provincia_IA = st.selectbox(label = "Provincia", options = u.province_sigle)

        with c4:
            input_CAP_IA = st.text_input(label = "CAP", max_chars = 5, placeholder = "00000")

        c1, c2, = st.columns(2)

        with c1:
            input_cellulare_IA = st.text_input(label = "Cellulare del socio", max_chars = 13, placeholder = "+000000000000")

        with c2:
            input_email_IA = st.text_input(label = "Email del socio", max_chars = 100)

        submitted = st.form_submit_button(label = "Submit", use_container_width = True)

        # finire

# ------------------------ Visualizza soci page ------------------------

if st.session_state.current_page == "Visualizza soci":
    st.title("🔍 Visualizza soci")

    df = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE", st.session_state.conn)
    st.dataframe(df)

# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------



# ------------------------  ------------------------

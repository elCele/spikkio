import streamlit as st
import utils as u
import pandas as pd
import datetime
from sqlalchemy import text

u.initialize_var()

u.config_sidebar()

st.set_page_config(
        page_title = st.session_state.current_page,
        page_icon = "🍋",
        layout = "wide",
        initial_sidebar_state = "auto"
    )

# ------------------------ Log in page ------------------------
    # Pagina iniziale dove viene richiesto il log in.
    # Bisogna capire come gestire vari utenti

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
                st.session_state.role = "master"
                st.rerun()

# ------------------------ Homepage page ------------------------
    # Homepage del gestionale di spikkio.
    # Grafico con anagrafiche/tesserati
    # Numero maschi, femmine, nd

if st.session_state.current_page == "Homepage":                                                                        # to do
    st.title("🍋 SPIKKIO")

    df = pd.read_sql("SELECT Sesso FROM TBL_ANAGRAFICHE", st.session_state.engine)

    m = 0
    f = 0
    nd = 0

    for el in df['Sesso']:
        if el == 'M':
            m += 1

        if el == 'F':
            f += 1

        if el == 'ND':
            nd += 1

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Utenti maschi", m)

    with c2:
        st.metric("Utenti femmine", f)

    with c3:
        st.metric("Altro", nd)

# ------------------------ Inserisci anagrafica page ------------------------
    # Pagina dove è possibile inserire nuovi soci all'interno del database utilizzando tutti i campi
    # necessari, con tanto di controlli su ogni campo

if st.session_state.current_page == "Inserisci anagrafica":                                                            # complete
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
            input_indirizzo_IA = st.text_input(label = "Indirizzo*", max_chars = 100)

        with c2:
            input_città_IA = st.text_input(label = "Città*", max_chars = 60)

        with c3:
            input_provincia_IA = st.selectbox(label = "Provincia*", options = u.province_sigle)

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
                st.error(e, icon = "❌")
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

            with st.container(border = True):
                st.subheader("Si vuole tesserare il socio appena inserito?")
                c1, c2 = st.columns(2)

                with c1:
                    st.button(label = "Sì", use_container_width = True, on_click = lambda: st.session_state.update(current_page = "Tesseramento"))

                with c2:
                    st.button(label = "No", use_container_width = True, on_click = lambda: st.session_state.update(current_page = "Inserisci anagrafica"), type = "primary")

# ------------------------ Visualizza soci page ------------------------
    # Pagina per la visualizzazione del contenuto della tabella TBL_ANAGRAFICHE.
    # Ricerca con filtri.
    # Pulsanti per aggiornare.
    # Pulsante per scaricare .pdf

if st.session_state.current_page == "Visualizza soci":                                                                 # to do
    st.title("🔍 Visualizza soci")

    df = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE", st.session_state.engine)

    with st.expander("Filtri", expanded = False):
        with st.form(key = "form_visualizza_soci", clear_on_submit = True, enter_to_submit = False, border = False):
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
                filter_provincia_VS = st.selectbox(label = "Provincia", options = u.province_sigle)

            with c4:
                filter_CAP_VS = st.text_input(label = "CAP", placeholder = "00000")

            c1, c2, = st.columns(2)

            with c1:
                filter_cellulare_VS = st.text_input(label = "Cellulare del socio", placeholder = "+000000000000")

            with c2:
                filter_email_VS = st.text_input(label = "Email del socio")

            is_cerca = st.form_submit_button(label = "Cerca", use_container_width = True, icon = "🔍")

    if is_cerca:
        query = "SELECT * FROM TBL_ANAGRAFICHE;"
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
            query = base_query + " WHERE " + " AND ".join(filters)
        else:
            query = base_query

        df = pd.read_sql(text(query), st.session_state.engine, params = params)

    if st.session_state.user == "root":
        st.data_editor(df)
    else:
        st.dataframe(df)

# ------------------------ Tesseramento page ------------------------
    # Pagina per il tesseramento di un socio.

if st.session_state.current_page == "Tesseramento":                                                                    # to do
    st.title("🪪 Tesseramento")

# ------------------------ Inserisci tipo tessera page ------------------------

if st.session_state.current_page == "Inserisci tipo tessera":                                                          # to do
    pass

# ------------------------ Visualizza tessere page ------------------------

if st.session_state.current_page == "Visualizza tessere":                                                              # to do
    pass

# ------------------------ Inserisci tipo qualifica page ------------------------

if st.session_state.current_page == "Inserisci tipo qualifica":                                                        # to do
    pass

# ------------------------ Visualizza qualifiche page ------------------------

if st.session_state.current_page == "Visualizza qualifiche":                                                           # to do
    pass

# ------------------------ Programma riunione direttivo page ------------------------

if st.session_state.current_page == "Programma riunione direttivo":                                                    # to do
    pass

# ------------------------ Visualizza riunioni direttivo page ------------------------

if st.session_state.current_page == "Visualizza riunioni direttivo":                                                   # to do
    pass

# ------------------------ Inserisci presenze direttivo ------------------------

if st.session_state.current_page == "Inserisci presenze direttivo":                                                    # to do
    pass

# ------------------------ Programma riunioni assemblea page ------------------------

if st.session_state.current_page == "Programma riunione assemblea":                                                    # to do
    pass

# ------------------------ Visualizza riunioni assemblea page ------------------------

if st.session_state.current_page == "Visualizza riunioni assemblea":                                                   # to do
    pass

# ------------------------ Inserisci ente page ------------------------

if st.session_state.current_page == "Inserisci ente":                                                                  # to do
    pass

# ------------------------ Visualizza enti ------------------------

if st.session_state.current_page == "Visualizza enti":                                                                 # to do
    pass

# ------------------------ Inserisci affiliazione page ------------------------

if st.session_state.current_page == "Inserisci affiliazione":                                                          # to do
    pass

# ------------------------ Visualizza affiliazione page ------------------------

if st.session_state.current_page == "Visualizza affiliazione":                                                         # to do
    pass

# ------------------------ Programma attività page ------------------------

if st.session_state.current_page == "Programma attività":                                                              # to do
    pass

# ------------------------ Visualizza attività page ------------------------

if st.session_state.current_page == "Visualizza attività":                                                             # to do
    pass

# ------------------------ Gestisci prenotazioni attività page ------------------------

if st.session_state.current_page == "Gestisci prenotazioni attività":                                                  # to do
    pass

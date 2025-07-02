import streamlit as st
import utils.functions as f
import utils.consts as c
import pandas as pd
import datetime
from sqlalchemy import text
import bcrypt

f.initialize_var()

f.config_sidebar()

st.set_page_config(
        page_title = st.session_state.current_page,
        page_icon = "🍋",
        layout = "wide",
        initial_sidebar_state = "auto"
    )

# ------------------------ Log in page ------------------------
    # Pagina iniziale dove viene richiesto il log in.

if st.session_state.current_page == "Log in":
    utenti = pd.read_sql("SELECT * FROM TBL_UTENTI", st.session_state.engine)

    st.title("🔑 Login")

    with st.form(key = "form_login", clear_on_submit = True, enter_to_submit = True):
        input_username_FL = st.text_input(label = "Username")
        input_password_FL = st.text_input(label = "Password", type = "password")

        submitted = st.form_submit_button(label = "Submit", use_container_width = True)

        if submitted:
            user_row = utenti[utenti['Username'] == input_username_FL]

            if user_row.empty:
                st.error("Utente non trovato", icon = "❌")
            else:
                st.session_state.CF_socio = user_row.iloc[0]['CF_socio']

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

                        with st.session_state.engine.connect() as conn:
                            conn.execute(
                                text("UPDATE TBL_UTENTI SET Ultimo_login = CURRENT_TIMESTAMP WHERE Username = :username"),
                                {"username": input_username_FL}
                            )
                            conn.commit()

                    st.rerun()
                else:
                    st.error("Password errata", icon = "❌")
    

# ------------------------ Cambia credenziali page ------------------------
    # Pagina per l'aggiornamento delle credenziali.

if st.session_state.current_page == "Cambia credenziali":
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
            st.error("Utente non trovato", icon = "❌")
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
                    st.error(e, icon = "❌")
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
                    st.error("Vecchia password errata", icon = "❌")

# ------------------------ Bacheca page ------------------------
    # Pagina principale dove l'utente vedrà i propri messaggi in bacheca

if st.session_state.current_page == "Bacheca":                                                                         # to do
    st.title("📌 Bacheca")

    query = f'''SELECT *
                FROM TBL_COMUNICAZIONI
                WHERE Destinatario = '{st.session_state.user}';
            '''
    
    df_comunicazioni = pd.read_sql(query, st.session_state.engine)

    with st.container(border = True):
        for _, c in df_comunicazioni.iterrows():
            with st.container(border = True):
                icon = ""

                if c['Categoria'] == "Avviso":
                    icon = "🔔"
                elif c['Categoria'] == 'Evento':
                    icon = "📅"
                elif c['Categoria'] == 'Convocazione':
                    icon = "📣"
                else:
                    icon = "🟥"

                st.subheader(f"{icon} {c['Categoria']} - {c['Titolo']}")
                st.write(c['Testo'])

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

# ------------------------ Visualizza soci page ------------------------
    # Pagina per la visualizzazione del contenuto della tabella TBL_ANAGRAFICHE.
    # Ricerca con filtri.
    # Pulsanti per aggiornare.
    # Pulsante per scaricare .pdf

if st.session_state.current_page == "Visualizza soci":                                                                 # to do
    st.title("🔍 Visualizza soci")

    if "master" in st.session_state.role:
        df = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE", st.session_state.engine)
    else:
        df = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE WHERE Attivo = TRUE", st.session_state.engine)
        df = df.drop(columns = ['Attivo'])


    with st.expander("Filtri", expanded = False):
        with st.form(key = "form_visualizza_soci", clear_on_submit = True, enter_to_submit = True, border = False):
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

    if "master" in st.session_state.role:
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

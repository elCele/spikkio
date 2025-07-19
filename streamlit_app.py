import streamlit as st
import utils.functions as f
import utils.consts as c
import pandas as pd
import datetime
from sqlalchemy import text
import bcrypt

f.initialize_var_batch_1()
f.initialize_var_batch_2()

f.config_sidebar()

st.set_page_config(
        page_title = f"SPIKKIO - {st.session_state.current_page}",
        page_icon = "🍋",
        layout = "wide",
        initial_sidebar_state = "auto"
    )

# ------------------------ Log in page --------------------------------------------------------------------------------
    # Pagina iniziale dove viene richiesto il log in.

if st.session_state.current_page == "Log in":
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
    

# ------------------------ Cambia credenziali page --------------------------------------------------------------------
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

# ------------------------ Bacheca page -------------------------------------------------------------------------------
    # Pagina principale dove l'utente vedrà i propri messaggi in bacheca

if st.session_state.current_page == "Bacheca":                                                                         # to do
    st.title("📌 Bacheca")

    with st.container(border = True):
        c1, c2, c3 = st.columns([0.6, 0.2, 0.2], vertical_alignment = 'bottom')

        with c1:
            filter_titolo_B = st.text_input("Cerca comunicazioni", placeholder = "Titolo comunicazione")

        with c2:
            filter_Categoria_B = st.selectbox("Cerca categoria", ['', 'Avviso', 'Evento', 'Convocazione', 'Segnalazione', 'Altro'])

        with c3:
            ancheLette = st.toggle("Mostra comunicazioni lette")

        query = f'''SELECT *
                    FROM TBL_COMUNICAZIONI
                    WHERE Destinatario = '{st.session_state.user}' AND
                        Titolo LIKE '%{filter_titolo_B}%' AND
                        Categoria LIKE '%{filter_Categoria_B}%'
                    ORDER BY Data_pubblicazione DESC;
                '''
        
        df_comunicazioni = pd.read_sql(query, st.session_state.engine)

        st.write("")
        st.write("")

        for _, c in df_comunicazioni.iterrows():
            if not ancheLette and c['Stato'] == 'Letta':
                continue

            with st.container(border = True):
                icon = ""

                if c['Categoria'] == "Avviso":
                    icon = "🔔"
                elif c['Categoria'] == 'Evento':
                    icon = "📅"
                elif c['Categoria'] == 'Convocazione':
                    icon = "📣"
                elif c['Categoria'] == 'Segnalazione':
                    icon = "📢"
                else:
                    icon = "⭕"

                if c['Categoria'] == 'Segnalazione':
                    st.subheader(f"{icon} {c['Categoria']} - [{c['Titolo']}]", divider = "gray")
                else:
                    st.subheader(f"{icon} {c['Categoria']} - {c['Titolo']}", divider = "gray")
                
                c1, c2 = st.columns([0.75, 0.15], vertical_alignment = 'top')

                with c1:
                    st.write(f"{c['Testo']}")

                with c2:
                    if c['Stato'] == 'Non letta':
                        segna_come_letta = st.button("Segna come letta", use_container_width = True, key = f"{c['ID_comunicazione']} - read_toggle")

                        if segna_come_letta:
                            with st.session_state.engine.connect() as conn:
                                conn.execute(text('''UPDATE TBL_COMUNICAZIONI
                                                     SET Stato = 'Letta'
                                                     WHERE ID_comunicazione = :ID'''), {'ID': c['ID_comunicazione']})
                                conn.commit()

                            st.rerun()

                if c['Allegato'] is not None and not pd.isna(c['Allegato']) and len(c['Allegato']) > 0:
                    st.download_button(
                        label = "Scarica allegato",
                        data = c['Allegato'],
                        file_name = f"{c['ID_comunicazione']}_allegato.{c['Estensione_allegato']}",
                        mime = "application/octet-stream",
                        icon = "📁"
                    )

                st.write(f":gray[Data pubblicazione: {c['Data_pubblicazione'].strftime('%d-%m-%Y')} - {c['Data_pubblicazione'].strftime('%H:%M:%S')}]")

# ------------------------ Inserisci anagrafica page ------------------------------------------------------------------
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

# ------------------------ Visualizza soci page -----------------------------------------------------------------------
    # Pagina per la visualizzazione del contenuto della tabella TBL_ANAGRAFICHE.
    # Ricerca con filtri.
    # Pulsanti per aggiornare.
    # Pulsante per scaricare .pdf

if st.session_state.current_page == "Visualizza anagrafiche":                                                          # to do
    st.title("🔍 Visualizza anagrafiche")

    if "master" in st.session_state.role:
        _anagrafiche = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE", st.session_state.engine)
    else:
        df_anagrafiche = pd.read_sql("SELECT * FROM TBL_ANAGRAFICHE WHERE Attivo = TRUE", st.session_state.engine)
        df_anagrafiche = df_anagrafiche.drop(columns = ['Attivo'])


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

# ------------------------ Tesseramento page --------------------------------------------------------------------------
    # Pagina per il tesseramento di un socio.

if st.session_state.current_page == "Tesseramento socio":                                                                    # to do
    st.title("🪪 Tesseramento")

# ------------------------ Visualizza tessere page --------------------------------------------------------------------

if st.session_state.current_page == "Visualizza tessere":                                                              # to do
    st.title('🪪 Visualizza tessere')
    
    query = '''SELECT *
               FROM TBL_TESSERE TT, TBL_ANAGRAFICHE TA
               WHERE TT.CF_socio = TA.CF
               '''
    
    df_tessere = pd.read_sql(query, st.session_state.engine)

    nTessere = 0

    for _, t in df_tessere.iterrows():
        if t['CF_socio'] == st.session_state.CF_socio:
            nTessere += 1

            with st.container(border = True):
                c1, c2 = st.columns([0.4, 0.6], vertical_alignment = 'center')

                with c1:
                    st.image(f.build_tessera(t['Nome'], t['Cognome'], t['CF_socio'], t['Data_scadenza'].date(), t['Codice_tessera']))

                with c2:
                    st.subheader(f"{t['Codice_tessera']}")
                    st.write(f"🪪 Tipologia tessera: :gray[{t['Tipo']}]")
                    st.write(f"🔑 Qualifica: :gray[{t['Qualifica']}]")
                    st.write(f"📆 Data di tesseramento: :gray[{t['Data_tesseramento'].date().strftime('%d/%m/%Y')}]")
                    st.write(f"📆 Data di scadenza: :red[{t['Data_scadenza'].date().strftime('%d/%m/%Y')}]")

    if nTessere == 0:
        with st.container(height = 100, border = True):
            st.markdown(
                """
                <style>
                .centered-text {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100%; /* Occupa l'altezza del container */
                    font-size: 20px;
                    color: gray;
                    padding-top: 20px;
                }
                </style>
                <div class="centered-text">
                    Nessuna tessera trovata
                </div>
                """,
                unsafe_allow_html=True
            )

# ------------------------ Programma attività page --------------------------------------------------------------------

if st.session_state.current_page == "Crea attività":                                                              # to do
    st.title("➕ Crea attività")

    with st.form(key = "form_crea_attività", clear_on_submit = True, border = True):
        input_denominazione_CA = st.text_input("Denominazione", max_chars = 100)
        input_data_CA = st.date_input("Data", min_value = datetime.date(1000, 1, 1), max_value = datetime.date(3000, 1, 1))

        c1, c2 = st.columns(2)

        with c1:
            input_oraInizio_CA = st.time_input("Ora di inizio")

        with c2:
            input_oraFine_CA = st.time_input("Ora di fine")

        input_descrizione_CA = st.text_area("Descrizione")

        submitted = st.form_submit_button("Submit", use_container_width = True)

        if submitted:
            err = []

            if input_denominazione_CA == "":
                err.append("Il campo 'Denominazione' non può essere lasciato vuoto.")

            if input_data_CA < datetime.date.today():
                err.append("La data inserita è precedente alla data odierna.")

            if input_oraInizio_CA > input_oraFine_CA:
                err.append("L'ora d'inizio è maggiore dell'ora di fine.")

            if input_descrizione_CA == "":
                err.append("Il campo 'Descrizione' non può essere lasciato vuoto.")

            if err:
                for e in err:
                    st.error(e, icon = "🚨")
            else:
                query = text('''INSERT INTO TBL_ATTIVITA (Denominazione, Data, Ora_inizio, Ora_fine, Descrizione)
                                VALUES (:denominazione, :data, :ora_inizio, :ora_fine, :descrizione)   
                                ''')
                
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'denominazione': input_denominazione_CA,
                        'data': input_data_CA,
                        'ora_inizio': input_oraInizio_CA,
                        'ora_fine': input_oraFine_CA,
                        'descrizione': input_descrizione_CA
                    })

                    conn.commit()

                st.success("L'attività è stata creata con successo.", icon = '✅')

                for u, _ in st.session_state.users:
                    query = text('''INSERT INTO TBL_COMUNICAZIONI (Titolo, Testo, Categoria, Data_scadenza, Autore, Destinatario)
                                    VALUES (:titolo, :testo, 'Evento', :data_scadenza, 'st.session_state.user', :destinatario)
                                    ''')
                    
                    with st.session_state.engine.connect() as conn:
                        conn.execute(query, {
                            'titolo': input_denominazione_CA,
                            'testo': f"Ciao {u['Username']}!\nÈ stata programmata una nuova attività che potrebbe interessarti:\n📅 Data: {input_data_CA}\n🕒 Ora di inizio: {input_oraInizio_CA}\n🕒 Ora fine: {input_oraFine_CA}\nSe vuoi saperne di più o partecipare, trovi tutti i dettagli sul gestionale.\nA presto!\nIl team di SPIKKIO",
                            'data_scadenza': datetime.combine(input_data_CA, input_oraFine_CA),
                            'destinatario': u['Username']
                        })

                        conn.commit()

                st.success("Le comunicazioni sono state inserite con successo.", icon = '✅')

# ------------------------ Effettua segnalazioni ----------------------------------------------------------------------

if st.session_state.current_page == "Effettua segnalazioni":                                                  # to do
    st.title("📢 Effettua segnalazioni")

    with st.form("form_effettua_segnalazioni", clear_on_submit = True):
        input_titolo_ES = st.text_input("Titolo", max_chars = 200)
        input_testo_ES = st.text_area("Segnalazione", height = 200, placeholder = 'Descrivere il problema in maniera breve ma dettagliata')

        submitted = st.form_submit_button("Submit", use_container_width = True, type = 'primary')

        if submitted:
            err = []

            if input_titolo_ES == '':
                err.append("Il campo Titolo non può essere vuoto.")

            if input_testo_ES == '':
                err.append('Il campo Segnalazione non può essere vuoto.')

            if err:
                for e in err:
                    st.error(e, icon = "🚨")
            else:
                query = text('''INSERT INTO TBL_SEGNALAZIONI (Titolo, Testo, Creato_da)
                                VALUES (:titolo, :testo, :creato_da)
                                ''')
                
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'titolo': input_titolo_ES,
                        'testo': input_testo_ES,
                        'creato_da': st.session_state.user
                    })

                    conn.commit()

            st.success("La segnalazione è stata inviata correttamente", icon = "✅")

# ------------------------ Gestisci segnalazioni ----------------------------------------------------------------------

if st.session_state.current_page == "Gestisci segnalazioni":
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

# ------------------------ Crea comunicazione -------------------------------------------------------------------------

if st.session_state.current_page == "Crea comunicazione":
    st.title("📝 Crea comunicazione")

    with st.container(border = True):
        input_titolo_CC = st.text_input('Titolo della comunicazione')
        input_testo_CC = st.text_area('Testo della comunicazione')

        input_categoria_CC = st.selectbox('Categoria', ['Avviso', 'Evento', 'Convocazione'])

        c1, c2, c3 = st.columns([1.5, 4.25, 4.25], vertical_alignment = 'bottom')

        with c1:
            input_dataScadenzaEnable_CC = st.toggle('Inserisci scadenza')

        with c2:
            if input_dataScadenzaEnable_CC:
                input_dataScadenza_CC = st.date_input('Data di scadenza', min_value = "today")
            else:
                input_dataScadenza_CC = st.date_input('Data di scadenza', min_value = "today", disabled = True)

        with c3:
            if input_dataScadenzaEnable_CC:
                input_oraScadenza_CC = st.time_input('Ora di scadenza')
            else:
                input_oraScadenza_CC = st.time_input('Ora di scadenza', disabled = True)

        c1, c2 = st.columns([0.2, 0.8])

        with c1:
            input_tipoUtenti_CC = st.selectbox("Seleziona utenti", ['Utenti singoli', 'Ruoli'])

        with c2:
            query = '''SELECT CF, Nome, Cognome, TU.Username, Ruolo
                        FROM TBL_ANAGRAFICHE TA, TBL_UTENTI TU, TBL_RUOLI TR
                        WHERE TA.CF = TU.CF_socio AND
                            TU.Username = TR.Username;
                        '''
            
            df_utenti = pd.read_sql(query, st.session_state.engine)

            option_array = []

            if input_tipoUtenti_CC == 'Ruoli':
                for _, u in df_utenti.iterrows():
                    option_array.append(u['Ruolo'])

                option_array = list(dict.fromkeys(option_array))

            if input_tipoUtenti_CC == 'Utenti singoli':
                for _, u in df_utenti.iterrows():
                    option_array.append(f"{u['Nome']} {u['Cognome']} - {u['CF']}")

            input_destinatari_CC = st.multiselect("Destinatari", option_array)

        c1, c2 = st.columns([2, 1], vertical_alignment = 'center')

        with c1:
            input_allegato_CC = st.file_uploader('Allegato', accept_multiple_files = False)

        with c2:
            if input_allegato_CC == None:
                input_estensioneFile_CC = st.text_input('Estensione del file', placeholder = "Scrivere solo l'estensione, senza il punto", max_chars = 20, disabled = True)
            else:
                input_estensioneFile_CC = st.text_input('Estensione del file', placeholder = "Scrivere solo l'estensione, senza il punto", max_chars = 20)

        submitted = st.button('Submit', use_container_width = True)

        if submitted:
            err = []

            if input_titolo_CC == '':
                err.append('Il campo titolo non può rimanere vuoto.')

            if input_testo_CC == '':
                err.append('Il campo testo non può rimanere vuoto.')

            if input_dataScadenzaEnable_CC and input_oraScadenza_CC < datetime.datetime.now().time():
                err.append("L'orario scelto non è valido.")
            elif input_dataScadenzaEnable_CC:
                input_dataScadenza_CC = datetime.datetime.combine(input_dataScadenza_CC, input_oraScadenza_CC)
            else:
                input_dataScadenza_CC = None

            if not input_destinatari_CC:
                err.append('La lista dei destinatari non può essere vuota.')
            
            if input_allegato_CC == None:
                input_estensioneFile_CC = None

            if err:
                for e in err:
                    st.error(e, icon = '🚨')
            else:
                if input_tipoUtenti_CC == 'Utenti singoli':
                    CF_dest = []
                    
                    for d in input_destinatari_CC:
                        d = d.split()
                        CF_dest.append(d[-1])

                    CF_dest = '(' + ', '.join([f"'{cf}'" for cf in CF_dest]) + ')'

                    query = f'''SELECT Username
                                FROM TBL_UTENTI
                                WHERE CF_socio IN {CF_dest}
                             '''
                    
                    df_destinatari = pd.read_sql(query, st.session_state.engine)

                    for _, d in df_destinatari.iterrows():
                        query = text('''INSERT INTO TBL_COMUNICAZIONI (Titolo, Testo, Categoria, Data_scadenza, Autore, Destinatario, Allegato, Estensione_allegato)
                                        VALUES (:titolo, :testo, :categoria, :data_scadenza, :autore, :destinatario, :allegato, :estensione)
                                        ''')
                        
                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'titolo': input_titolo_CC,
                                'testo': input_testo_CC,
                                'categoria': input_categoria_CC,
                                'data_scadenza': input_dataScadenza_CC,
                                'autore': st.session_state.user,
                                'destinatario': d['Username'],
                                'allegato': input_allegato_CC,
                                'estensione': input_estensioneFile_CC
                            })

                            conn.commit()

                    st.success('Comunicazioni inserite con successo.', icon = '✅')
            
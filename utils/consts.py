import streamlit as st
from password_strength import PasswordPolicy

# ------------------------ Lista delle province italiane ------------------------

province_sigle = [
    "", "AG", "AL", "AN", "AO", "AR", "AP", "AT", "AV", "BA", "BT", "BL", "BN",
    "BG", "BI", "BO", "BZ", "BS", "BR", "CA", "CL", "CB", "CI", "CE", "CT",
    "CZ", "CH", "CO", "CS", "CR", "KR", "CN", "EN", "FM", "FE", "FI", "FG",
    "FC", "FR", "GE", "GO", "GR", "IM", "IS", "SP", "AQ", "LT", "LE", "LC",
    "LI", "LO", "LU", "MC", "MN", "MS", "MT", "VS", "ME", "MI", "MO", "MB",
    "NA", "NO", "NU", "OG", "OT", "OR", "PD", "PA", "PR", "PV", "PG", "PU",
    "PE", "PC", "PI", "PT", "PN", "PZ", "PO", "RG", "RA", "RC", "RE", "RI",
    "RN", "RM", "RO", "SA", "SS", "SV", "SI", "SR", "SO", "TA", "TE", "TR",
    "TO", "TP", "TN", "TV", "TS", "UD", "VA", "VE", "VB", "VC", "VR", "VV",
    "VI", "VT"
]

# ------------------------ Policy password ------------------------

policy = PasswordPolicy.from_names(length = 8,uppercase = 1,numbers = 1,special = 1)

# ------------------------ Gestione tipi di pagine per tutti gli utenti ------------------------
    # Pagine                               6 / 34 + ?
        # - Log in ------------------------ ✅
        # - Bacheca ----------------------- ✅
        # - Visualizza contributi --------- ❌
        # - Visualizza tessere ------------ ❌
        # - Visualizza team --------------- ❌
        # - Visualizza attività ----------- ❌
        # - Visualizza convocazioni ------- ❌
        # - Effettua segnalazioni --------- ✅
        # - Cambia credenziali ------------ ✅
        # - Visualizza team --------------- ❌
        # - Modifica team ----------------- ❌
        # - Aggiungi membri --------------- ❌
        # - Visualizza membri ------------- ❌
        # - Elimina membri ---------------- ❌
        # - Crea attività ----------------- ❌
        # - Visualizza attività ----------- ❌
        # - Elimina attività -------------- ❌
        # - Crea comunicazione ------------ ❌
        # - Crea team --------------------- ❌
        # - Modifica teams ---------------- ❌
        # - Visualizza teams -------------- ❌
        # - Disattiva team ---------------- ❌
        # - Visualizza iscrizioni --------- ❌
        # - Aggiungi ente ----------------- ❌
        # - Visualizza enti --------------- ❌
        # - Crea affiliazione ------------- ❌
        # - Visualizza affiliazioni ------- ❌
        # - Inserisci anagrafica ---------- ✅
        # - Visualizza anagrafiche -------- ✅
        # - Tesseramento socio ------------ ❌
        # - Crea tessera ------------------ ❌
        # - Visualizza tessere ------------ ❌
        # - Gestisci utenze --------------- ❌
        # - Gestisci segnalazioni --------- ❌

class Pagina:
    def __init__(self, nome, icona, in_expander):
        self.nome = nome
        self.icona = icona
        self.in_expander = in_expander

    def build(self):
        if self.in_expander:
            st.button(label = self.nome, use_container_width = True, icon = self.icona, on_click = lambda: st.session_state.update(current_page = self.nome))
        else:
            st.sidebar.button(label = self.nome, use_container_width = True, icon = self.icona, on_click = lambda: st.session_state.update(current_page = self.nome))

class Expander:
    def __init__(self, nome, icona, in_expander, pagine):
        self.nome = nome
        self.icona = icona
        self.in_expander = in_expander
        self.pagine = pagine

    def build(self):
        if self.in_expander:
            with st.expander(label = self.nome, expanded = False, icon = self.icona):
                for pagina in self.pagine:
                    pagina.build()
        else:
            with st.sidebar.expander(label = self.nome, expanded = False, icon = self.icona):
                for pagina in self.pagine:
                    pagina.build()

users = {
    "Utente standard": [
        Pagina("Bacheca", "📌", False),

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "Gestore di un team": [
        Pagina("Bacheca", "📌", False),

        Expander("Il mio team", "🤝", False, [
            Pagina("Visualizza team", "🔍", True),
            Pagina("Modifica team", "🔧", True),

            Expander("Membri", "👥", True, [
                Pagina("Aggiungi membri", "➕", True),
                Pagina("Visualizza membri", "🔍", True),
                Pagina("Elimina membri", "➖", True)
            ]),

            Expander("Attività", "📅", True, [
                Pagina("Crea attività", "➕", True),
                Pagina("Visualizza attività", "🔍", True),
                Pagina("Elimina attività", "➖", True)
            ]),
        ]),

        Pagina("Crea comunicazione", "📝", False),

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "Gestore dei team": [
        Pagina("Bacheca", "📌", False),

        Expander("Teams", "👥", False, [
            Pagina("Crea team", "➕", True),
            Pagina("Modifica teams", "🔧", True),
            Pagina("Visualizza teams", "🔍", True),
            Pagina("Disattiva team", "➖", True)
        ]),

        Pagina("Crea comunicazione", "📝", False),

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "Gestore delle attività": [
        Pagina("Bacheca", "📌", False),

        Expander("Attività", "📅", False, [
            Pagina("Crea attività", "➕", True),
            Pagina("Visualizza attività", "🔍", True),
            Pagina("Elimina attività", "➖", True),
            Pagina("Visualizza iscrizioni", "📋", True)
        ]),

        Expander("Enti", "🏛️", False, [
            Expander("Anagrafiche", "🗂️", True, [
                Pagina("Aggiungi ente", "➕", True),
                Pagina("Visualizza enti", "🔍", True)
            ]),

            Expander("Affiliazioni", "🔗", True, [
                Pagina("Crea affiliazione", "➕", True),
                Pagina("Visualizza affiliazioni", "🔍", True)
            ])
        ]),

        Pagina("Crea comunicazione", "📝", False),

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "Gestore dei tesseramenti": [
        Pagina("Bacheca", "📌", False),

        Expander("Anagrafiche", "🗂️", True, [
            Pagina("Inserisci anagrafica", "➕", True),
            Pagina("Visualizza anagrafiche", "🔍", True)
        ]),

        Expander("Tessere", "🔗", True, [
            Pagina("Tesseramento socio", "🪪", True),
            Pagina("Crea tessera", "➕", True),
            Pagina("Visualizza tessere", "🔍", True)
        ]),

        Pagina("Crea comunicazione", "📝", False),

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "Gestore della contabilità": [

    ],

    "Amministratore della contabilità": [

    ],

    "Gestore completo": [
        Pagina("Bacheca", "📌", False),

        Expander("Anagrafiche", "🗂️", False, [
            Pagina("Inserisci anagrafica", "➕", True),
            Pagina("Visualizza anagrafiche", "🔍", True),
            Pagina("Gestisci utenze", "⚙️", True)
        ]),

        Expander("Tessere", "🔗", False, [
            Pagina("Crea tessera", "➕", True),
            Pagina("Visualizza tessere", "🔍", True)
        ]),

        Expander("Teams", "👥", False, [
            Pagina("Crea team", "➕", True),
            Pagina("Modifica teams", "🔧", True),
            Pagina("Visualizza teams", "🔍", True),
            Pagina("Disattiva team", "➖", True)
        ]),

        Expander("Attività", "📅", False, [
            Pagina("Crea attività", "➕", True),
            Pagina("Visualizza attività", "🔍", True),
            Pagina("Elimina attività", "➖", True),
            Pagina("Visualizza iscrizioni", "📋", True)
        ]),

        Expander("Enti", "🏛️", False, [
            Expander("Anagrafiche", "🗂️", True, [
                Pagina("Aggiungi ente", "➕", True),
                Pagina("Visualizza enti", "🔍", True)
            ]),

            Expander("Affiliazioni", "🔗", True, [
                Pagina("Crea affiliazione", "➕", True),
                Pagina("Visualizza affiliazioni", "🔍", True)
            ])
        ]),

        Pagina("Crea comunicazione", "📝", False),
        Pagina("Gestisci segnalazioni", "🛠️", False),

        # aggiungere il resto

        Expander("Dati socio", "🗂️", False, [
            Pagina("Visualizza contributi", "📊", True),
            Pagina("Visualizza tessere", "🪪", True),
            Pagina("Visualizza team", "👥", True),      # mostrare solo se appartiene ad un team
            Pagina("Visualizza attività", "📅", True),
            Pagina("Visualizza convocazioni", "📣", True)
        ]),

        Expander("Profilo", "👤", False, [
            Pagina("Effettua segnalazioni", "📢", True),
            Pagina("Visualizza segnalazioni", "🔍", True),
            Pagina("Cambia credenziali", "🔄️", True)
        ])
    ],

    "master": [
        Pagina("Inserisci anagrafica", "➕", False),
        Pagina("Visualizza anagrafiche", "🔍", False)
    ]
}

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model


    def fillDDClub(self, dd_club: ft.Dropdown):

        clubs = self._model.getClub()
        dd_club.options.clear()

        for c in clubs:
            dd_club.options.append(ft.dropdown.Option(key=c.club_id, text=c.name))


    def fillDDCampionato(self, dd_campionato: ft.Dropdown):
        competizioni = self._model.getCompetizioni()
        dd_campionato.options.clear()
        for comp in competizioni:
            dd_campionato.options.append(ft.dropdown.Option(key=comp.competition_id, text=comp.name))


    def fillDDRuolo(self, dd_ruolo: ft.Dropdown):
        ruoli = self._model.getRuolo()
        dd_ruolo.options.clear()
        for r in ruoli:
            dd_ruolo.options.append(ft.dropdown.Option(key=r, text=r))


    def fillDDSottoRuolo(self, dd_sotto_ruolo: ft.Dropdown):
        # Vuoto alla creazione della tab: le opzioni dipendono dal ruolo
        # scelto e vengono ripopolate da handleRuoloChange.
        pass


    def handleRuoloChange(self, e):

        self._view.dd_sotto_ruolo_sottovalutati.options.clear()
        self._view.dd_sotto_ruolo_sottovalutati.value = None

        ruolo = self._view.dd_ruolo_sottovalutati.value or None
        for sr in self._model.getSottoRuoli(ruolo):
            self._view.dd_sotto_ruolo_sottovalutati.options.append(ft.dropdown.Option(key=sr, text=sr))

        self._view.update_page()


    def fillDDGiocatore(self, dd_giocatore: ft.Dropdown):
        # Vuoto alla creazione della tab: il club non è ancora noto (dipende
        # da cosa l'utente sceglie nella tab 'Analisi Rosa'). Le opzioni
        # vengono ripopolate da handleClubChange quando l'utente sceglie
        # (o cambia) il club in tab 1, non qui.
        pass


    def handleClubChange(self, e):

        self._view.dd_giocatore.options.clear()
        self._view.dd_giocatore.value = None

        club_id = self._view.dd_club.value
        if club_id:
            giocatori = self._model.getGiocatoriClub(int(club_id))
            for g in giocatori:
                self._view.dd_giocatore.options.append(
                    ft.dropdown.Option(key=g["player_id"], text=g["name"])
                )

        self._view.update_page()

        # ---------------- Tab 1: Analisi Rosa ----------------


    def handleAnalizzaRosa(self, e):
        club_id = self._view.dd_club.value
        if not club_id:
            self._view.create_alert("Seleziona un club prima di analizzare la rosa.", color="red")
            return


        club_name = club_id
        for opzione in self._view.dd_club.options:
            if opzione.key == club_id:
                club_name = opzione.text
                break

        report = self._model.analizzaRosa(int(club_id), club_name)
        if report is None:
            self._view.create_alert("Nessun giocatore trovato per questo club.", color="red")
            return

        self._view.mostra_analisi_rosa(report)

        # ---------------- Tab 2: Obiettivi Campagna ----------------


    def handleImpostaObiettivi(self, e):

        try:
            budget = float(self._view.tf_budget.value)
        except (TypeError, ValueError):
            self._view.create_alert("Inserisci un budget valido (numero).", color="red")
            return
        if budget <= 0:
            self._view.create_alert("Il budget deve essere maggiore di zero.", color="red")
            return


        mappa_ruoli = {
            self._view.cb_ruolo_portiere: "Goalkeeper",
            self._view.cb_ruolo_difensore: "Defender",
            self._view.cb_ruolo_centrocampista: "Midfield",
            self._view.cb_ruolo_attaccante: "Attack",
        }
        ruoli = []
        for checkbox, valore in mappa_ruoli.items():
            if checkbox.value:
                ruoli.append(valore)

        try:
            eta_min = self._parse_intero_opzionale(self._view.tf_eta_min.value)
            eta_max = self._parse_intero_opzionale(self._view.tf_eta_max.value)
        except ValueError:
            self._view.create_alert("L'età deve essere un numero intero.", color="red")
            return

        if (eta_min is not None and eta_min < 0) or (eta_max is not None and eta_max < 0):
            self._view.create_alert("L'età non può essere negativa.", color="red")
            return
        if eta_min is not None and eta_max is not None and eta_min > eta_max:
            self._view.create_alert("L'età minima non può essere maggiore dell'età massima.", color="red")
            return

        campionato_provenienza = self._view.dd_campionato_provenienza.value  # None se non selezionato

        obiettivi = self._model.impostaObiettivi(budget, ruoli, eta_min, eta_max, campionato_provenienza)
        self._aggiorna_dd_ruolo_colpo_mercato(obiettivi.ruoli)
        self._view.create_alert("Obiettivi campagna salvati:\n" + str(obiettivi), color="green")


    def _aggiorna_dd_ruolo_colpo_mercato(self, ruoli):

        self._view.dd_ruolo_colpo_mercato.options.clear()
        self._view.dd_ruolo_colpo_mercato.value = None

        ruoli_da_mostrare = ruoli if ruoli else self._model.getRuolo()
        for r in ruoli_da_mostrare:
            self._view.dd_ruolo_colpo_mercato.options.append(ft.dropdown.Option(key=r, text=r))

        self._view.update_page()


    @staticmethod
    def _parse_intero_opzionale(testo):

        if testo is None or testo.strip() == "":
            return None
        return int(testo)


    # ---------------- Tab 3: Giocatori Sottovalutati ----------------

    def handleCercaSottovalutati(self, e):

        obiettivi = self._model.getObiettivi()
        if obiettivi is None:
            self._view.create_alert(
                "Imposta prima gli Obiettivi Campagna (tab 'Obiettivi Campagna').", color="red"
            )
            return

        ruolo = self._view.dd_ruolo_sottovalutati.value or None
        sotto_ruolo = self._view.dd_sotto_ruolo_sottovalutati.value or None


        try:
            prezzo_min = self._parse_numero_opzionale(self._view.tf_prezzo_min.value)
            prezzo_max = self._parse_numero_opzionale(self._view.tf_prezzo_max.value)
        except ValueError:
            self._view.create_alert("Il prezzo deve essere un numero.", color="red")
            return

        if (prezzo_min is not None and prezzo_min < 0) or (prezzo_max is not None and prezzo_max < 0):
            self._view.create_alert("Il prezzo non può essere negativo.", color="red")
            return
        if prezzo_min is not None and prezzo_max is not None and prezzo_min > prezzo_max:
            self._view.create_alert("Il prezzo minimo non può essere maggiore del prezzo massimo.", color="red")
            return
        if prezzo_min is not None and prezzo_min >= obiettivi.budget:
            self._view.create_alert(
                f"Hai selezionato un prezzo fuori budget: il prezzo minimo deve essere "
                f"inferiore al budget della campagna ({obiettivi.budget:,.0f} €).",
                color="red",
            )
            return
        if prezzo_max is not None and prezzo_max >= obiettivi.budget:
            self._view.create_alert(
                f"Hai selezionato un prezzo fuori budget: il prezzo massimo deve essere "
                f"inferiore al budget della campagna ({obiettivi.budget:,.0f} €).",
                color="red",
            )
            return

        ordina_per = self._view.dd_ordina_sottovalutati.value or "rapporto"

        risultati = self._model.cercaSottovalutati(
            ruolo=ruolo, sotto_ruolo=sotto_ruolo, prezzo_min=prezzo_min, prezzo_max=prezzo_max,
            ordina_per=ordina_per
        )

        if not risultati:
            self._view.create_alert("Nessun giocatore trovato con questi filtri.", color="red")
            return

        self._view.mostra_sottovalutati(risultati)


    @staticmethod
    def _parse_numero_opzionale(testo):

        if testo is None or testo.strip() == "":
            return None
        return float(testo)


    # ---------------- Tab 4: Sostituti Simili ----------------

    def handleTrovaSostituti(self, e):
        player_id = self._view.dd_giocatore.value
        if not player_id:
            self._view.create_alert("Seleziona un giocatore da sostituire.", color="red")
            return

        club_id = self._view.dd_club.value
        if not club_id:
            self._view.create_alert(
                "Seleziona prima un club nella tab 'Analisi Rosa'.", color="red"
            )
            return

        try:
            valore_max = self._parse_numero_opzionale(self._view.tf_valore_max_sostituto.value)
        except ValueError:
            self._view.create_alert("Il valore massimo deve essere un numero.", color="red")
            return
        if valore_max is not None and valore_max < 0:
            self._view.create_alert("Il valore massimo non può essere negativo.", color="red")
            return

        soglia_similarita = self._view.sl_soglia_similarita.value

        risultati = self._model.trovaSostituti(
            int(player_id), int(club_id), valore_max=valore_max, soglia_similarita=soglia_similarita
        )
        if risultati is None:
            self._view.create_alert(
                "Statistiche di rendimento non disponibili per questo giocatore.", color="red"
            )
            return
        if not risultati:
            self._view.create_alert("Nessun sostituto trovato con questi filtri.", color="red")
            return

        self._view.mostra_sostituti(risultati)


    # ---------------- Tab 5: Piano di Mercato ----------------

    def _leggi_input_piano(self):

        obiettivi = self._model.getObiettivi()
        if obiettivi is None:
            self._view.create_alert(
                "Imposta prima gli Obiettivi Campagna (tab 'Obiettivi Campagna').", color="red"
            )
            return None

        try:
            max_acquisti = self._parse_intero_opzionale(self._view.tf_max_acquisti.value)
        except ValueError:
            self._view.create_alert("Il numero massimo di acquisti deve essere un intero.", color="red")
            return None
        if max_acquisti is None or max_acquisti <= 0:
            self._view.create_alert("Inserisci un numero massimo di acquisti maggiore di zero.", color="red")
            return None


        club_id = self._view.dd_club.value
        club_id_escluso = int(club_id) if club_id else None


        ruolo_colpo_mercato = self._view.dd_ruolo_colpo_mercato.value or None


        return max_acquisti, club_id_escluso, ruolo_colpo_mercato


    def handleGeneraPiano(self, e):
        input_validato = self._leggi_input_piano()
        if input_validato is None:
            return
        max_acquisti, club_id_escluso, ruolo_colpo_mercato = input_validato

        piano = self._model.generaPianoMercato(
            max_acquisti, club_id_escluso=club_id_escluso,
            ruolo_colpo_mercato=ruolo_colpo_mercato,
        )
        if not piano.giocatori:
            self._view.create_alert("Nessun piano di mercato trovato con questi vincoli.", color="red")
            return

        self._view.mostra_piano_mercato(piano)


    def handleConfrontaScenari(self, e):
        input_validato = self._leggi_input_piano()
        if input_validato is None:
            return
        max_acquisti, club_id_escluso, ruolo_colpo_mercato = input_validato

        risultato = self._model.confrontaScenari(
            max_acquisti, club_id_escluso=club_id_escluso,
            ruolo_colpo_mercato=ruolo_colpo_mercato,
        )
        if not risultato.simulazioni:
            self._view.create_alert(
                "Nessun piano di mercato su cui simulare con questi vincoli.", color="red"
            )
            return

        self._view.mostra_confronto_scenari(risultato)

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------------- Riempimento dropdown ----------------

    def fillDDClub(self, dd_club: ft.Dropdown):
        # TODO: caricare l'elenco dei club dal model/DAO
        pass

    def fillDDCampionato(self, dd_campionato: ft.Dropdown):
        # TODO: caricare l'elenco dei campionati dal model/DAO
        pass

    def fillDDRuolo(self, dd_ruolo: ft.Dropdown):
        # TODO: caricare l'elenco dei ruoli dal model/DAO
        pass

    def fillDDGiocatore(self, dd_giocatore: ft.Dropdown):
        # TODO: caricare l'elenco dei giocatori dal model/DAO
        pass

    # ---------------- Tab 1: Analisi Rosa ----------------

    def handleAnalizzaRosa(self, e):
        # TODO: analizzare la rosa del club selezionato (valore, struttura d'età,
        #  copertura ruoli, contratti in scadenza, punti deboli)
        pass

    # ---------------- Tab 2: Obiettivi Campagna ----------------

    def handleImpostaObiettivi(self, e):
        # TODO: impostare budget e obiettivi della campagna (ruoli, età, campionato)
        pass

    # ---------------- Tab 3: Giocatori Sottovalutati ----------------

    def handleCercaSottovalutati(self, e):
        # TODO: calcolare la classifica dei giocatori sottovalutati filtrata per ruolo e fascia di prezzo
        pass

    # ---------------- Tab 4: Sostituti Simili ----------------

    def handleTrovaSostituti(self, e):
        # TODO: interrogare il grafo di similarità per trovare i sostituti più simili a costo inferiore
        pass

    # ---------------- Tab 5: Piano di Mercato ----------------

    def handleGeneraPiano(self, e):
        # TODO: calcolare il piano di mercato ottimale (acquisti e cessioni) sotto vincolo di budget
        pass

    def handleConfrontaScenari(self, e):
        # TODO: confrontare più scenari (miglioramento atteso, spesa, rischio)
        pass

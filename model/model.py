
import math
import random
from datetime import date, timedelta
from statistics import mean, stdev
from collections import Counter

import networkx as nx

from database.DAO import DAO
from model.analisi_rosa import AnalisiRosa
from model.obiettivi_campagna import ObiettiviCampagna
from model.giocatore_sottovalutato import GiocatoreSottovalutato
from model.sostituto_simile import SostitutoSimile
from model.piano_mercato import PianoMercato
from model.risultato_montecarlo import RisultatoMontecarlo

# Un contratto è considerato "in scadenza" se
GIORNI_ORIZZONTE_SCADENZA = 365

# Ampiezza (in anni) della finestra
ANNI_FINESTRA_MERCATO = 3

# Metriche di Player normalizzate di default nello scoring
METRICHE_SCORING_DEFAULT = ["gol_90", "assist_90", "presenze"]

# Pesi per la combinazione degli z-score nell'indice di rendimento

PESI_INDICE_RENDIMENTO = {
    "Attack":     {"gol_90": 0.5, "assist_90": 0.25, "presenze": 0.25},
    "Midfield":   {"gol_90": 0.2, "assist_90": 0.4,  "presenze": 0.4},
    "Defender":   {"gol_90": 0.1, "assist_90": 0.2,  "presenze": 0.7},
    "Goalkeeper": {"gol_90": 0.0, "assist_90": 0.0,  "presenze": 1.0},
}
# Fallback per ruoli non mappati sopra: peso uniforme tra le metriche
PESI_UNIFORME = {m: 1 / len(METRICHE_SCORING_DEFAULT) for m in METRICHE_SCORING_DEFAULT}

# Minutaggio minimo per entrare nella classifica sottovalutati
MINUTI_MINIMI_SCORING = 900

# Sotto SOGLIA_MINIMA_GRUPPO_SOTTORUOLO giocatori nello stesso sotto-ruolo
# (es. 'Centre-Back'), lo z-score si ripiega sul gruppo più ampio per
# ruolo generico (position)
SOGLIA_MINIMA_GRUPPO_SOTTORUOLO = 3


GRANULARITA_ZAINO_EUR = 500_000

# Tetto massimo di spesa per il giocatore del "colpo di mercato" (tab 5)
LIMITE_PERCENTUALE_COLPO_MERCATO = 0.75

# Tetto massimo di spesa per ciascun acquisto del RESTO del piano (dopo
# l'eventuale colpo di mercato)
LIMITE_PERCENTUALE_RESTO_PIANO = 0.6

# Prima di risolvere lo zaino, il pool di candidati viene troncato ai
# migliori N per rapporto rendimento/valore
MAX_CANDIDATI_ZAINO = 150

# Numero di simulazioni della distribuzione Montecarlo del rendimento
N_SIMULAZIONI_MONTECARLO = 1000

# Rumore gaussiano applicato
SIGMA_MONTECARLO_RELATIVA = 0.2
SIGMA_MONTECARLO_MINIMA = 0.1

# Criteri di ordinamento disponibili nella tab "Giocatori Sottovalutati".

CRITERI_ORDINAMENTO_SOTTOVALUTATI = {
    "rapporto":  lambda r: r.rapporto_per_milione,
    "indice":    lambda r: r.indice_rendimento,
    "valore":    lambda r: r.player.market_value_in_eur or 0,
    "contratto": lambda r: r.anni_contratto_residuo if r.anni_contratto_residuo is not None else float("-inf"),
}

class Model:
    def __init__(self):
        # Obiettivi della campagna acquisti impostati dall'utente nella
        # tab 2; None finché l'utente non ha ancora premuto il bottone.
        self._obiettivi_correnti = None

        self._grafo_similarita = nx.Graph()



    def getClub(self):
        return DAO.get_club()

    def impostaObiettivi(self, budget, ruoli, eta_min, eta_max, campionato_provenienza):

        self._obiettivi_correnti = ObiettiviCampagna(
            budget=budget,
            ruoli=ruoli,
            eta_min=eta_min,
            eta_max=eta_max,
            campionato_provenienza=campionato_provenienza,
        )
        return self._obiettivi_correnti

    def getObiettivi(self):

        return self._obiettivi_correnti

    def analizzaRosa(self, club_id, club_name):

        giocatori = DAO.get_giocatori_club(club_id)
        if not giocatori:
            return None

        oggi = date.today()

        numero_giocatori = len(giocatori)
        valore_totale = sum(g["market_value_in_eur"] or 0 for g in giocatori)

        eta_list = []
        for g in giocatori:
            eta = self._calcola_eta(g["date_of_birth"], oggi)
            if eta is not None:
                eta_list.append(eta)
        eta_media = (sum(eta_list) / len(eta_list)) if eta_list else None

        distribuzione_ruoli = dict(Counter(
            g["position"] for g in giocatori if g["position"]
        ))

        soglia_scadenza = oggi + timedelta(days=GIORNI_ORIZZONTE_SCADENZA)
        contratti_in_scadenza = []
        for g in giocatori:
            scadenza = self._a_data(g["contract_expiration_date"])
            if scadenza and oggi <= scadenza <= soglia_scadenza:
                contratti_in_scadenza.append((g["name"], scadenza))
        contratti_in_scadenza.sort(key=lambda t: t[1])


        distribuzione_nazionalita = dict(Counter(
            g["country_of_citizenship"] for g in giocatori if g["country_of_citizenship"]
        ))
        percentuale_stranieri = self._calcola_percentuale_stranieri(distribuzione_nazionalita, numero_giocatori)

        distribuzione_piede = dict(Counter(
            g["foot"] for g in giocatori if g["foot"]
        ))


        concentrazione_valore_top5 = self._calcola_concentrazione_top5(giocatori, valore_totale)


        minutaggio_medio = quota_rosa_utilizzata = eta_media_pesata_minuti = None
        contributo_reparto = {}

        competizione = DAO.get_competizione_club(club_id)
        if competizione and competizione.get("domestic_competition_id") and competizione.get("ultima_stagione") is not None:
            rendimento_club = DAO.get_rendimento_club(
                club_id, competizione["domestic_competition_id"], competizione["ultima_stagione"]
            )
            id_rosa_attuale = {g["player_id"] for g in giocatori}

            rendimento_rosa = [r for r in rendimento_club if r["player_id"] in id_rosa_attuale]

            if rendimento_rosa:
                minutaggio_medio, quota_rosa_utilizzata = self._calcola_utilizzo(rendimento_rosa, numero_giocatori)
                eta_media_pesata_minuti = self._calcola_eta_pesata_minuti(rendimento_rosa, oggi)
                contributo_reparto = self._calcola_contributo_reparto(rendimento_rosa)


        eta_media_acquisti = None
        movimenti = DAO.get_movimenti_mercato(club_id, ANNI_FINESTRA_MERCATO)
        if movimenti:
            eta_media_acquisti = self._calcola_eta_media_acquisti(movimenti, club_id, oggi)

        return AnalisiRosa(
            club_id=club_id,
            club_name=club_name,
            numero_giocatori=numero_giocatori,
            valore_totale=valore_totale,
            eta_media=eta_media,
            distribuzione_ruoli=distribuzione_ruoli,
            contratti_in_scadenza=contratti_in_scadenza,
            distribuzione_nazionalita=distribuzione_nazionalita,
            percentuale_stranieri=percentuale_stranieri,
            distribuzione_piede=distribuzione_piede,
            concentrazione_valore_top5=concentrazione_valore_top5,
            minutaggio_medio=minutaggio_medio,
            quota_rosa_utilizzata=quota_rosa_utilizzata,
            eta_media_pesata_minuti=eta_media_pesata_minuti,
            contributo_reparto=contributo_reparto,
            anni_finestra_mercato=ANNI_FINESTRA_MERCATO,
            eta_media_acquisti=eta_media_acquisti,
        )

    @staticmethod
    def _a_data(valore):

        if valore is None:
            return None
        return valore.date() if hasattr(valore, "date") else valore

    @classmethod
    def _calcola_eta(cls, data_nascita, oggi):
        nascita = cls._a_data(data_nascita)
        if nascita is None:
            return None
        return oggi.year - nascita.year - ((oggi.month, oggi.day) < (nascita.month, nascita.day))

    @classmethod
    def _anni_a_scadenza(cls, contract_expiration_date, oggi):

        scadenza = cls._a_data(contract_expiration_date)
        if scadenza is None:
            return None
        return round((scadenza - oggi).days / 365.25, 1)

    @classmethod
    def _eta_nel_range(cls, data_nascita, oggi, eta_min, eta_max):

        eta = cls._calcola_eta(data_nascita, oggi)
        if eta is None:
            return False
        if eta_min is not None and eta < eta_min:
            return False
        if eta_max is not None and eta > eta_max:
            return False
        return True

    @staticmethod
    def _calcola_percentuale_stranieri(distribuzione_nazionalita, numero_giocatori):

        if not distribuzione_nazionalita or not numero_giocatori:
            return None
        nazionalita_principale = max(distribuzione_nazionalita, key=distribuzione_nazionalita.get)
        giocatori_locali = distribuzione_nazionalita[nazionalita_principale]
        return round((numero_giocatori - giocatori_locali) / numero_giocatori * 100, 1)

    @staticmethod
    def _calcola_concentrazione_top5(giocatori, valore_totale):
        if not valore_totale:
            return None
        valori = sorted((g["market_value_in_eur"] or 0 for g in giocatori), reverse=True)
        top5 = sum(valori[:5])
        return round(top5 / valore_totale * 100, 1)

    @staticmethod
    def _calcola_utilizzo(rendimento_rosa, numero_giocatori):

        minuti_giocatori_attivi = [r["minuti_totali"] for r in rendimento_rosa if r["minuti_totali"] > 0]
        minutaggio_medio = (sum(minuti_giocatori_attivi) / len(minuti_giocatori_attivi)) \
            if minuti_giocatori_attivi else None
        quota_rosa_utilizzata = (len(minuti_giocatori_attivi) / numero_giocatori * 100) \
            if numero_giocatori else None
        return minutaggio_medio, quota_rosa_utilizzata

    @classmethod
    def _calcola_eta_pesata_minuti(cls, rendimento_rosa, oggi):

        somma_pesata = 0
        somma_pesi = 0
        for r in rendimento_rosa:
            eta = cls._calcola_eta(r["date_of_birth"], oggi)
            minuti = r["minuti_totali"]
            if eta is not None and minuti > 0:
                somma_pesata += eta * minuti
                somma_pesi += minuti
        return (somma_pesata / somma_pesi) if somma_pesi > 0 else None

    @staticmethod
    def _calcola_contributo_reparto(rendimento_rosa):

        contributo = {}
        for r in rendimento_rosa:
            reparto = r["position"]
            if not reparto:
                continue
            gol, assist = contributo.get(reparto, (0, 0))
            contributo[reparto] = (gol + (r["gol"] or 0), assist + (r["assist"] or 0))
        return contributo

    @classmethod
    def _calcola_eta_media_acquisti(cls, movimenti, club_id, oggi):
        eta_list = []
        for m in movimenti:
            if m["to_club_id"] == club_id:
                data_trasferimento = cls._a_data(m["transfer_date"])
                eta = cls._calcola_eta(m["date_of_birth"], data_trasferimento or oggi)
                if eta is not None:
                    eta_list.append(eta)
        return (sum(eta_list) / len(eta_list)) if eta_list else None



    @staticmethod
    def calcola_z_score(giocatori, metrica):

        if len(giocatori) < 2:
            # con un solo giocatore nel gruppo la deviazione standard
            # non è calcolabile: non c'è nulla con cui confrontarlo
            return {g.player_id: 0.0 for g in giocatori}

        valori = [getattr(g, metrica) for g in giocatori]
        media = mean(valori)
        dev_std = stdev(valori)

        if dev_std == 0:
            # tutti i giocatori del gruppo hanno lo stesso valore:
            # nessuno si distingue dagli altri, z-score neutro per tutti
            return {g.player_id: 0.0 for g in giocatori}

        return {
            g.player_id: (getattr(g, metrica) - media) / dev_std
            for g in giocatori
        }

    @classmethod
    def normalizza_per_ruolo(cls, giocatori, metriche=None):

        if metriche is None:
            metriche = METRICHE_SCORING_DEFAULT

        gruppi_per_ruolo = {}
        gruppi_per_sotto_ruolo = {}
        for g in giocatori:
            gruppi_per_ruolo.setdefault(g.position, []).append(g)
            if g.sub_position:
                gruppi_per_sotto_ruolo.setdefault((g.position, g.sub_position), []).append(g)


        z_per_ruolo = {
            ruolo: {metrica: cls.calcola_z_score(gruppo, metrica) for metrica in metriche}
            for ruolo, gruppo in gruppi_per_ruolo.items()
        }


        z_per_sotto_ruolo = {}
        for chiave, gruppo in gruppi_per_sotto_ruolo.items():
            if len(gruppo) < SOGLIA_MINIMA_GRUPPO_SOTTORUOLO:
                continue
            z_per_sotto_ruolo[chiave] = {
                metrica: cls.calcola_z_score(gruppo, metrica) for metrica in metriche
            }

        risultato = {}
        for g in giocatori:
            chiave_sotto_ruolo = (g.position, g.sub_position) if g.sub_position else None
            if chiave_sotto_ruolo is not None and chiave_sotto_ruolo in z_per_sotto_ruolo:
                z_metriche = z_per_sotto_ruolo[chiave_sotto_ruolo]
            else:
                z_metriche = z_per_ruolo[g.position]
            risultato[g.player_id] = {
                metrica: round(z_metriche[metrica][g.player_id], 3)
                for metrica in metriche
            }

        return risultato

    @classmethod
    def calcola_indice_rendimento(cls, giocatori):

        z_per_giocatore = cls.normalizza_per_ruolo(giocatori)

        indici = {}
        for g in giocatori:
            pesi = PESI_INDICE_RENDIMENTO.get(g.position, PESI_UNIFORME)
            z = z_per_giocatore[g.player_id]
            indici[g.player_id] = sum(z.get(metrica, 0.0) * peso for metrica, peso in pesi.items())
        return indici

    def cercaSottovalutati(self, ruolo=None, sotto_ruolo=None, prezzo_min=None, prezzo_max=None, ordina_per="rapporto"):

        obiettivi = self.getObiettivi()
        if obiettivi is None:
            return None

        oggi = date.today()

        if obiettivi.campionato_provenienza:
            competizioni_id = [obiettivi.campionato_provenienza]
        else:
            # nessun campionato scelto: si cerca sui soli campionati
            # domestici (non le coppe: un top player gioca sia in
            # campionato che in Champions League, e includendo anche le
            # coppe finirebbe conteggiato più volte nella stessa ricerca)
            competizioni_id = [c.competition_id for c in DAO.get_campionati_domestici()]

        giocatori = []
        for competition_id in competizioni_id:
            ultima_stagione = DAO.get_ultima_stagione(competition_id)
            if ultima_stagione is None:
                continue
            giocatori.extend(DAO.get_rendimento_giocatori(
                competition_id, ultima_stagione, ruolo=ruolo, sotto_ruolo=sotto_ruolo,
                minuti_minimi=MINUTI_MINIMI_SCORING
            ))


        migliore_per_player_id = {}
        for g in giocatori:
            attuale = migliore_per_player_id.get(g.player_id)
            if attuale is None or g.minuti_totali > attuale.minuti_totali:
                migliore_per_player_id[g.player_id] = g
        giocatori = list(migliore_per_player_id.values())

        if not giocatori:
            return []

        if obiettivi.eta_min is not None or obiettivi.eta_max is not None:
            giocatori = [
                g for g in giocatori
                if self._eta_nel_range(g.date_of_birth, oggi, obiettivi.eta_min, obiettivi.eta_max)
            ]
            if not giocatori:
                return []

        indici = self.calcola_indice_rendimento(giocatori)

        risultati = []
        for g in giocatori:
            valore = g.market_value_in_eur
            if not valore or valore <= 0:
                continue
            if prezzo_min is not None and valore < prezzo_min:
                continue
            if prezzo_max is not None and valore > prezzo_max:
                continue

            indice = indici[g.player_id]
            rapporto = indice / (valore / 1_000_000)
            risultati.append(GiocatoreSottovalutato(
                player=g,
                indice_rendimento=round(indice, 3),
                rapporto_per_milione=round(rapporto, 3),
                anni_contratto_residuo=self._anni_a_scadenza(g.contract_expiration_date, oggi),
            ))

        chiave_ordinamento = CRITERI_ORDINAMENTO_SOTTOVALUTATI.get(
            ordina_per, CRITERI_ORDINAMENTO_SOTTOVALUTATI["rapporto"]
        )
        risultati.sort(key=chiave_ordinamento, reverse=True)
        return risultati

    def get_rendimento_giocatori(self, competition_id, season, ruolo=None, sotto_ruolo=None, minuti_minimi=900):
        return DAO.get_rendimento_giocatori(
            competition_id, season, ruolo=ruolo, sotto_ruolo=sotto_ruolo, minuti_minimi=minuti_minimi
        )

    def getCompetizioni(self):
        return DAO.get_competizioni()

    def getRuolo(self):
        return DAO.get_ruoli()

    def getSottoRuoli(self, ruolo=None):
        return DAO.get_sotto_ruoli(ruolo)

    def getGiocatoriClub(self, club_id):
        return DAO.get_giocatori_club(club_id)



    def trovaSostituti(self, player_id, club_id_target, valore_max=None, soglia_similarita=0.0):

        giocatori_club = DAO.get_giocatori_club(club_id_target)
        scheda_target = next((g for g in giocatori_club if g["player_id"] == player_id), None)
        if scheda_target is None:
            return None
        ruolo = scheda_target["position"]
        # sotto-ruolo del target: se non noto nel dataset, il filtro non
        # si applica e il pool di candidati resta l'intero ruolo generico
        sotto_ruolo = scheda_target["sub_position"] or None

        candidati = []
        for competizione in DAO.get_campionati_domestici():
            ultima_stagione = DAO.get_ultima_stagione(competizione.competition_id)
            if ultima_stagione is None:
                continue
            candidati.extend(DAO.get_rendimento_giocatori(
                competizione.competition_id, ultima_stagione, ruolo=ruolo, sotto_ruolo=sotto_ruolo,
                minuti_minimi=MINUTI_MINIMI_SCORING
            ))


        migliore_per_player_id = {}
        for g in candidati:
            attuale = migliore_per_player_id.get(g.player_id)
            if attuale is None or g.minuti_totali > attuale.minuti_totali:
                migliore_per_player_id[g.player_id] = g
        candidati = list(migliore_per_player_id.values())

        target = migliore_per_player_id.get(player_id)
        if target is None:
            return None

        z_per_giocatore = self.normalizza_per_ruolo(candidati)
        z_target = z_per_giocatore[target.player_id]

        indici = self.calcola_indice_rendimento(candidati)


        self._grafo_similarita.clear()
        self._grafo_similarita.add_node(target.player_id)
        for g in candidati:
            if g.player_id == target.player_id:
                continue
            if g.current_club_id == club_id_target:
                continue
            z_g = z_per_giocatore[g.player_id]
            distanza = math.sqrt(sum(
                (z_target[metrica] - z_g[metrica]) ** 2 for metrica in METRICHE_SCORING_DEFAULT
            ))
            similarita = 1 / (1 + distanza)
            self._grafo_similarita.add_edge(target.player_id, g.player_id, weight=similarita)

        candidati_per_id = {g.player_id: g for g in candidati}

        risultati = []
        for vicino, dati in self._grafo_similarita.adj[target.player_id].items():
            similarita = dati["weight"]
            if similarita < soglia_similarita:
                continue
            g = candidati_per_id[vicino]
            if valore_max is not None and g.market_value_in_eur and g.market_value_in_eur > valore_max:
                continue
            differenza_valore = None
            if g.market_value_in_eur is not None and target.market_value_in_eur is not None:
                differenza_valore = g.market_value_in_eur - target.market_value_in_eur

            indice = round(indici[g.player_id], 3)
            rapporto = None
            if g.market_value_in_eur and g.market_value_in_eur > 0:
                rapporto = round(indice / (g.market_value_in_eur / 1_000_000), 3)

            risultati.append(SostitutoSimile(
                player=g, similarita=round(similarita, 3), differenza_valore=differenza_valore,
                indice_rendimento=indice, rapporto_per_milione=rapporto,
            ))


        risultati.sort(key=lambda r: (r.similarita, r.indice_rendimento), reverse=True)
        return risultati



    def generaPianoMercato(self, max_acquisti, club_id_escluso=None, ruolo_colpo_mercato=None):

        obiettivi = self.getObiettivi()
        if obiettivi is None:
            return None

        oggi = date.today()

        if obiettivi.campionato_provenienza:
            competizioni_id = [obiettivi.campionato_provenienza]
        else:
            competizioni_id = [c.competition_id for c in DAO.get_campionati_domestici()]


        ruoli_da_cercare = list(obiettivi.ruoli) if obiettivi.ruoli else [None]


        if ruolo_colpo_mercato and obiettivi.ruoli and ruolo_colpo_mercato not in ruoli_da_cercare:
            ruoli_da_cercare.append(ruolo_colpo_mercato)

        candidati = []
        for competition_id in competizioni_id:
            ultima_stagione = DAO.get_ultima_stagione(competition_id)
            if ultima_stagione is None:
                continue
            for ruolo in ruoli_da_cercare:
                candidati.extend(DAO.get_rendimento_giocatori(
                    competition_id, ultima_stagione, ruolo=ruolo, minuti_minimi=MINUTI_MINIMI_SCORING
                ))


        migliore_per_player_id = {}
        for g in candidati:
            attuale = migliore_per_player_id.get(g.player_id)
            if attuale is None or g.minuti_totali > attuale.minuti_totali:
                migliore_per_player_id[g.player_id] = g
        candidati = list(migliore_per_player_id.values())

        if club_id_escluso is not None:
            candidati = [g for g in candidati if g.current_club_id != club_id_escluso]

        if obiettivi.eta_min is not None or obiettivi.eta_max is not None:
            candidati = [
                g for g in candidati
                if self._eta_nel_range(g.date_of_birth, oggi, obiettivi.eta_min, obiettivi.eta_max)
            ]


        candidati = [
            g for g in candidati
            if g.market_value_in_eur and 0 < g.market_value_in_eur <= obiettivi.budget
        ]

        if not candidati:
            return PianoMercato(giocatori=[], budget=obiettivi.budget, spesa_totale=0.0, indice_totale=0.0)

        indici = self.calcola_indice_rendimento(candidati)


        giocatori_colpo = []
        budget_residuo = obiettivi.budget
        max_acquisti_residuo = max_acquisti
        ruoli_gia_coperti_da_colpo = set()

        if ruolo_colpo_mercato and max_acquisti_residuo > 0:

            limite_per_giocatore = obiettivi.budget
            if len(obiettivi.ruoli) >= 2:
                limite_per_giocatore = obiettivi.budget * LIMITE_PERCENTUALE_COLPO_MERCATO

            candidati_ruolo_colpo = sorted(
                (g for g in candidati if g.position == ruolo_colpo_mercato),
                key=lambda g: g.market_value_in_eur, reverse=True,
            )
            # il primo della lista (il più costoso) entro entrambi i tetti
            colpo = next(
                (g for g in candidati_ruolo_colpo
                 if g.market_value_in_eur <= budget_residuo and g.market_value_in_eur <= limite_per_giocatore),
                None,
            )
            if colpo is not None:
                giocatori_colpo.append(colpo)
                budget_residuo -= colpo.market_value_in_eur
                max_acquisti_residuo -= 1
                ruoli_gia_coperti_da_colpo.add(colpo.position)


                candidati = [g for g in candidati if g.player_id != colpo.player_id]


        if obiettivi.ruoli:
            candidati = [g for g in candidati if g.position in obiettivi.ruoli]


        candidati = [g for g in candidati if g.market_value_in_eur <= budget_residuo]


        if max_acquisti_residuo >= 2:
            limite_resto_piano = budget_residuo * LIMITE_PERCENTUALE_RESTO_PIANO
            candidati = [g for g in candidati if g.market_value_in_eur <= limite_resto_piano]


        ruoli_presenti = sorted(set(g.position for g in candidati))
        quota_per_ruolo = max(2, MAX_CANDIDATI_ZAINO // max(1, len(ruoli_presenti)))
        meta_quota = max(1, quota_per_ruolo // 2)

        id_visti = set()
        candidati_troncati = []
        for ruolo in ruoli_presenti:
            gruppo = [g for g in candidati if g.position == ruolo]
            per_valore = sorted(gruppo, key=lambda g: g.market_value_in_eur, reverse=True)[:meta_quota]
            per_rapporto = sorted(
                gruppo, key=lambda g: indici[g.player_id] / (g.market_value_in_eur / 1_000_000), reverse=True
            )[:meta_quota]
            for g in per_valore + per_rapporto:
                if g.player_id not in id_visti:
                    id_visti.add(g.player_id)
                    candidati_troncati.append(g)
        candidati = candidati_troncati


        valore_medio_club_acquirente = (
            DAO.get_valore_medio_rosa_club(club_id_escluso) if club_id_escluso is not None else None
        )
        cache_valore_medio_club = {}

        def valore_medio_club(club_id):
            if club_id not in cache_valore_medio_club:
                cache_valore_medio_club[club_id] = DAO.get_valore_medio_rosa_club(club_id)
            return cache_valore_medio_club[club_id]


        capacita = max(0, int(budget_residuo // GRANULARITA_ZAINO_EUR))
        pesi = [max(1, int(-(-g.market_value_in_eur // GRANULARITA_ZAINO_EUR))) for g in candidati]


        valori = []
        for g, peso in zip(candidati, pesi):
            indice = indici[g.player_id]
            rapporto = indice / (g.market_value_in_eur / 1_000_000)
            fattore_affinita = self._fattore_affinita_club(
                valore_medio_club(g.current_club_id), valore_medio_club_acquirente
            )
            valori.append((peso, rapporto * fattore_affinita, indice * fattore_affinita))


        copertura = None
        maschera_richiesta = 0
        if len(obiettivi.ruoli) >= 2:
            ruoli_da_coprire = [r for r in obiettivi.ruoli if r not in ruoli_gia_coperti_da_colpo]
            ruolo_a_bit = {ruolo: 1 << idx for idx, ruolo in enumerate(ruoli_da_coprire)}
            maschera_richiesta = (1 << len(ruoli_da_coprire)) - 1  # 0 se ruoli_da_coprire è vuota
            copertura = [ruolo_a_bit.get(g.position, 0) for g in candidati]

        indici_scelti = self._risolvi_piano_con_fallback(
            pesi, valori, capacita, max_acquisti_residuo, copertura, maschera_richiesta
        )
        giocatori_scelti = giocatori_colpo + [candidati[i] for i in indici_scelti]

        risultati = []
        spesa_totale = 0.0
        indice_totale = 0.0
        for g in giocatori_scelti:
            indice = round(indici[g.player_id], 3)
            rapporto = round(indice / (g.market_value_in_eur / 1_000_000), 3)
            risultati.append(GiocatoreSottovalutato(
                player=g, indice_rendimento=indice, rapporto_per_milione=rapporto,
                anni_contratto_residuo=self._anni_a_scadenza(g.contract_expiration_date, oggi),
            ))
            spesa_totale += g.market_value_in_eur
            indice_totale += indice

        return PianoMercato(
            giocatori=risultati, budget=obiettivi.budget,
            spesa_totale=spesa_totale, indice_totale=round(indice_totale, 3),
        )

    def _risolvi_piano_con_fallback(self, pesi, valori, capacita, max_acquisti, copertura, maschera_richiesta):

        valore, indici_scelti = self._risolvi_zaino_ricorsivo(
            pesi, valori, capacita, max_acquisti, valore_zero=(0.0, 0.0, 0.0),
            copertura=copertura, maschera_richiesta=maschera_richiesta,
        )
        if valore is None:
            _, indici_scelti = self._risolvi_zaino_ricorsivo(
                pesi, valori, capacita, max_acquisti, valore_zero=(0.0, 0.0, 0.0)
            )
        return indici_scelti

    @staticmethod
    def _fattore_affinita_club(valore_medio_club_provenienza, valore_medio_club_acquirente):

        if not valore_medio_club_provenienza or not valore_medio_club_acquirente:
            return 1.0
        return min(valore_medio_club_provenienza, valore_medio_club_acquirente) / \
            max(valore_medio_club_provenienza, valore_medio_club_acquirente)

    @staticmethod
    def _risolvi_zaino_ricorsivo(pesi, valori, capacita, max_oggetti, valore_zero=0.0,
                                  copertura=None, maschera_richiesta=0):

        n = len(pesi)
        memo = {}
        ha_vincolo_copertura = maschera_richiesta != 0

        def somma(a, b):
            if isinstance(a, tuple):
                return tuple(x + y for x, y in zip(a, b))
            return a + b

        def ricorsione(i, capacita_residua, oggetti_residui, ruoli_mancanti):

            if i == 0 or capacita_residua <= 0 or oggetti_residui <= 0:
                if ruoli_mancanti == 0:
                    return valore_zero, []
                return None, []

            chiave = (i, capacita_residua, oggetti_residui, ruoli_mancanti)
            if chiave in memo:
                return memo[chiave]


            valore_no, scelta_no = ricorsione(i - 1, capacita_residua, oggetti_residui, ruoli_mancanti)


            valore_si, scelta_si = None, []
            if pesi[i - 1] <= capacita_residua:
                nuovi_ruoli_mancanti = (ruoli_mancanti & ~copertura[i - 1]) if ha_vincolo_copertura else 0
                valore_parziale, scelta_parziale = ricorsione(
                    i - 1, capacita_residua - pesi[i - 1], oggetti_residui - 1, nuovi_ruoli_mancanti
                )
                if valore_parziale is not None:
                    valore_si = somma(valore_parziale, valori[i - 1])
                    scelta_si = scelta_parziale + [i - 1]

            if valore_si is not None and (valore_no is None or valore_si > valore_no):
                risultato = (valore_si, scelta_si)
            else:
                risultato = (valore_no, scelta_no)
            memo[chiave] = risultato
            return risultato

        return ricorsione(n, capacita, max_oggetti, maschera_richiesta)

    def confrontaScenari(self, max_acquisti, club_id_escluso=None,
                          ruolo_colpo_mercato=None, n_simulazioni=N_SIMULAZIONI_MONTECARLO):

        piano = self.generaPianoMercato(
            max_acquisti, club_id_escluso=club_id_escluso, ruolo_colpo_mercato=ruolo_colpo_mercato,
        )
        if piano is None:
            return None

        if not piano.giocatori:
            return RisultatoMontecarlo(piano=piano, simulazioni=[], media=0.0, deviazione_standard=0.0)

        simulazioni = []
        for _ in range(n_simulazioni):
            totale_simulato = 0.0
            for gs in piano.giocatori:
                sigma = max(abs(gs.indice_rendimento) * SIGMA_MONTECARLO_RELATIVA, SIGMA_MONTECARLO_MINIMA)
                totale_simulato += random.gauss(gs.indice_rendimento, sigma)
            simulazioni.append(round(totale_simulato, 3))

        media = round(mean(simulazioni), 3)
        deviazione = round(stdev(simulazioni), 3) if len(simulazioni) >= 2 else 0.0

        return RisultatoMontecarlo(
            piano=piano, simulazioni=simulazioni, media=media, deviazione_standard=deviazione,
        )
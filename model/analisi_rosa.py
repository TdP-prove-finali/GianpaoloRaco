from dataclasses import dataclass, field


@dataclass
class AnalisiRosa:
    """Fotografia della rosa di un club: valore, struttura d'età,
    copertura dei ruoli, contratti in scadenza e alcuni indicatori
    aggiuntivi (nazionalità, piede, concentrazione del valore,
    utilizzo in campo, mercato recente). Prodotta dal Model a partire
    dai dati grezzi restituiti dal DAO."""

    club_id: int
    club_name: str
    numero_giocatori: int
    valore_totale: float
    eta_media: float           # None se nessuna data di nascita disponibile
    distribuzione_ruoli: dict  # {'Goalkeeper': 3, 'Defender': 8, ...}
    contratti_in_scadenza: list  # lista di tuple (nome, data_scadenza), ordinata per data

    # ---- Composizione della rosa ----
    distribuzione_nazionalita: dict = field(default_factory=dict)  # {'Italy': 15, 'Brazil': 4, ...}
    percentuale_stranieri: float = None  # % giocatori con nazionalità diversa dalla più frequente in rosa
    distribuzione_piede: dict = field(default_factory=dict)        # {'right': 20, 'left': 8, ...}

    # ---- Concentrazione economica ----
    concentrazione_valore_top5: float = None  # % del valore totale rosa nei 5 giocatori più costosi

    # ---- Utilizzo in campo (richiede dati di rendimento; None se non disponibili) ----
    minutaggio_medio: float = None        # minuti medi tra chi ha giocato almeno una partita
    quota_rosa_utilizzata: float = None   # % giocatori in rosa con almeno una presenza in stagione
    eta_media_pesata_minuti: float = None  # età media pesata per minuti giocati
    contributo_reparto: dict = field(default_factory=dict)  # {'Attack': (32, 18), ...} -> (gol, assist)

    # ---- Mercato recente (None se nessun movimento nella finestra considerata) ----
    anni_finestra_mercato: int = 3
    eta_media_acquisti: float = None  # età media dei giocatori acquistati, ultimi N anni

    def __str__(self):
        righe = [
            f"Club: {self.club_name}",
            f"Giocatori in rosa: {self.numero_giocatori}",
            f"Valore totale rosa: {self.valore_totale:,.0f} €",
            f"Età media: {self.eta_media:.1f} anni" if self.eta_media is not None else "Età media: n/d",
            "Distribuzione ruoli: " + ", ".join(
                f"{ruolo}={numero}" for ruolo, numero in self.distribuzione_ruoli.items()
            ),
        ]

        if self.contratti_in_scadenza:
            righe.append("Contratti in scadenza entro 12 mesi:")
            for nome, scadenza in self.contratti_in_scadenza:
                righe.append(f"  - {nome} (scadenza {scadenza})")
        else:
            righe.append("Nessun contratto in scadenza entro 12 mesi")

        if self.distribuzione_nazionalita:
            top_nazionalita = sorted(self.distribuzione_nazionalita.items(), key=lambda x: -x[1])[:5]
            righe.append("Nazionalità principali: " + ", ".join(f"{n}={c}" for n, c in top_nazionalita))
        if self.percentuale_stranieri is not None:
            righe.append(f"Giocatori stranieri: {self.percentuale_stranieri:.0f}%")

        if self.distribuzione_piede:
            righe.append("Piede preferito: " + ", ".join(
                f"{piede}={numero}" for piede, numero in self.distribuzione_piede.items()
            ))

        if self.concentrazione_valore_top5 is not None:
            righe.append(f"Concentrazione valore nei 5 più costosi: {self.concentrazione_valore_top5:.0f}%")

        if self.minutaggio_medio is not None:
            righe.append(f"Minutaggio medio (tra chi ha giocato): {self.minutaggio_medio:.0f}'")
        if self.quota_rosa_utilizzata is not None:
            righe.append(f"Quota rosa realmente utilizzata: {self.quota_rosa_utilizzata:.0f}%")
        if self.eta_media_pesata_minuti is not None:
            righe.append(f"Età media pesata sui minuti giocati: {self.eta_media_pesata_minuti:.1f} anni")
        if self.contributo_reparto:
            righe.append("Contributo offensivo per reparto: " + ", ".join(
                f"{reparto}=({gol} + {assist})"
                for reparto, (gol, assist) in self.contributo_reparto.items()
            ))

        if self.eta_media_acquisti is not None:
            righe.append(
                f"Età media degli acquisti (ultimi {self.anni_finestra_mercato} anni): "
                f"{self.eta_media_acquisti:.1f} anni"
            )

        return "\n".join(righe)

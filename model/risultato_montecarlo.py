from dataclasses import dataclass, field


@dataclass
class RisultatoMontecarlo:


    piano: object
    simulazioni: list = field(default_factory=list)
    media: float = 0.0
    deviazione_standard: float = 0.0

    def __str__(self):

        p = self.piano
        righe = [
            "IL PIANO",
            f"{p.numero_acquisti} acquisti, per una spesa di {p.spesa_totale:,.0f} € "
            f"su un budget di {p.budget:,.0f} €.",
            f"Punteggio di rendimento atteso: {p.indice_totale:.2f} - un numero che riassume "
            f"quanto rendono, sulla carta, i giocatori scelti (più alto è meglio, ma è un "
            f"punteggio relativo per confrontare piani diversi, non un'unità di misura assoluta).",
        ]

        if not self.simulazioni:
            righe.append("")
            righe.append("Nessuna simulazione disponibile: il piano non contiene giocatori.")
            return "\n".join(righe)

        fascia_bassa = self.media - self.deviazione_standard
        fascia_alta = self.media + self.deviazione_standard
        minimo, massimo = min(self.simulazioni), max(self.simulazioni)

        righe.append("")
        righe.append("RISULTATO DELLE SIMULAZIONI")
        righe.append(f"Punteggio medio ottenuto: {self.media:.2f}.")
        righe.append(
            f"In genere il rendimento di questa squadra oscilla tra {fascia_bassa:.2f} e "
            f"{fascia_alta:.2f}: fuori da questo intervallo è meno probabile, ma può succedere."
        )
        righe.append(
            f"Scenario peggiore incontrato: {minimo:.2f}. Scenario migliore incontrato: {massimo:.2f}."
        )


        if abs(self.media) > 1e-9:
            variabilita = abs(self.deviazione_standard / self.media)
        else:
            variabilita = float("inf") if self.deviazione_standard > 0 else 0.0

        if variabilita < 0.15:
            livello = "BASSO"
            consiglio = "il punteggio resta abbastanza stabile da uno scenario all'altro: puoi fidarti ragionevolmente della previsione."
        elif variabilita < 0.35:
            livello = "MEDIO"
            consiglio = "il punteggio può oscillare in modo sensibile: consideralo un'indicazione di massima, non un valore garantito."
        else:
            livello = "ALTO"
            consiglio = "il punteggio è molto incerto: il rendimento reale potrebbe discostarsi parecchio da quello previsto."

        righe.append("")
        righe.append(f"LIVELLO DI RISCHIO: {livello}")
        righe.append(consiglio.capitalize())

        return "\n".join(righe)

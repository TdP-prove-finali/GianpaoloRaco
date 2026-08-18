from dataclasses import dataclass, field


@dataclass
class PianoMercato:


    giocatori: list = field(default_factory=list)  # lista di GiocatoreSottovalutato
    budget: float = 0.0
    spesa_totale: float = 0.0
    indice_totale: float = 0.0

    @property
    def budget_residuo(self):
        return self.budget - self.spesa_totale

    @property
    def numero_acquisti(self):
        return len(self.giocatori)

    def __str__(self):
        righe = [
            f"Piano di mercato: {self.numero_acquisti} acquisti",
            f"Spesa totale: {self.spesa_totale:,.0f} € "
            f"(budget: {self.budget:,.0f} €, residuo {self.budget_residuo:,.0f} €)",
            f"Indice di rendimento complessivo: {self.indice_totale:.2f}",
        ]
        if self.giocatori:
            righe.append("Giocatori:")
            for gs in self.giocatori:
                righe.append(f"  - {gs}")
        else:
            righe.append("Nessun giocatore selezionato")
        return "\n".join(righe)

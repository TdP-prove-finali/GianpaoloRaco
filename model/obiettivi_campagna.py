from dataclasses import dataclass, field


@dataclass
class ObiettiviCampagna:


    budget: float
    ruoli: list = field(default_factory=list)
    eta_min: int = None
    eta_max: int = None
    campionato_provenienza: str = None

    def __str__(self):
        righe = [f"Budget: {self.budget:,.0f} €"]
        righe.append("Ruoli da rafforzare: " + (", ".join(self.ruoli) if self.ruoli else "nessun vincolo"))

        if self.eta_min is not None or self.eta_max is not None:
            minimo = self.eta_min if self.eta_min is not None else "-"
            massimo = self.eta_max if self.eta_max is not None else "-"
            righe.append(f"Età: {minimo} - {massimo}")
        else:
            righe.append("Età: nessun vincolo")

        righe.append(f"Campionato di provenienza: {self.campionato_provenienza or 'qualsiasi'}")
        return "\n".join(righe)

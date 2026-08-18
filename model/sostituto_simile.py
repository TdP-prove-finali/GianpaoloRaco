from dataclasses import dataclass


@dataclass
class SostitutoSimile:


    player: object
    similarita: float
    differenza_valore: float = None
    indice_rendimento: float = None
    rapporto_per_milione: float = None

    def __str__(self):
        p = self.player
        valore_milioni = (p.market_value_in_eur or 0) / 1_000_000
        club = p.current_club_name or "club sconosciuto"

        if self.differenza_valore is None:
            nota_valore = ""
        elif self.differenza_valore < 0:
            nota_valore = f" (risparmio {abs(self.differenza_valore) / 1_000_000:.1f}M €)"
        else:
            nota_valore = f" (costa {self.differenza_valore / 1_000_000:.1f}M € in più)"

        nota_rendimento = f" - indice rendimento {self.indice_rendimento:.2f}" if self.indice_rendimento is not None else ""
        nota_rapporto = f" - rapporto {self.rapporto_per_milione:.2f} per milione" if self.rapporto_per_milione is not None else ""

        return (
            f"{p.name} ({p.position}) - {club} - valore {valore_milioni:.1f}M €{nota_valore} - "
            f"similarità {self.similarita:.2f}{nota_rendimento}{nota_rapporto}"
        )

from dataclasses import dataclass

from model.formattazione import descrivi_indice_rendimento, descrivi_rapporto_qualita_prezzo


@dataclass
class GiocatoreSottovalutato:


    player: object
    indice_rendimento: float
    rapporto_per_milione: float
    anni_contratto_residuo: float = None

    def __str__(self):
        p = self.player
        valore_milioni = (p.market_value_in_eur or 0) / 1_000_000
        club = p.current_club_name or "club sconosciuto"

        if self.anni_contratto_residuo is None:
            contratto = "scadenza contratto non nota"
        elif self.anni_contratto_residuo <= 0:
            contratto = "contratto già scaduto/in scadenza"
        else:
            contratto = f"contratto ancora per {self.anni_contratto_residuo:.1f} anni"

        descrizione_rendimento = descrivi_indice_rendimento(self.indice_rendimento)
        descrizione_rapporto = descrivi_rapporto_qualita_prezzo(self.rapporto_per_milione)

        return (
            f"{p.name} ({p.position}) - {club} - valore {valore_milioni:.1f}M € - {contratto} - "
            f"{descrizione_rendimento} (indice {self.indice_rendimento:.2f}) - "
            f"{descrizione_rapporto} ({self.rapporto_per_milione:.2f} per milione speso)"
        )

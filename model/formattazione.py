


def descrivi_indice_rendimento(indice):

    if indice >= 1.0:
        return "rendimento eccellente per il ruolo"
    if indice >= 0.3:
        return "rendimento sopra la media del ruolo"
    if indice > -0.3:
        return "rendimento nella media del ruolo"
    if indice > -1.0:
        return "rendimento sotto la media del ruolo"
    return "rendimento scarso per il ruolo"


def descrivi_rapporto_qualita_prezzo(rapporto):

    if rapporto >= 1.0:
        return "ottimo rapporto qualità-prezzo"
    if rapporto >= 0.3:
        return "buon rapporto qualità-prezzo"
    if rapporto > -0.3:
        return "rapporto qualità-prezzo nella media"
    return "rapporto qualità-prezzo debole (costa più di quanto rende)"

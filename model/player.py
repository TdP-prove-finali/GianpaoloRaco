class Player:


    def __init__(self, player_id, name, position, sub_position, date_of_birth,
                 current_club_id, current_club_name, market_value_in_eur,
                 highest_market_value_in_eur, presenze, minuti_totali,
                 gol, assist, gialli, rossi, contract_expiration_date=None):
        self.player_id = player_id
        self.name = name
        self.position = position
        self.sub_position = sub_position
        self.date_of_birth = date_of_birth
        self.current_club_id = current_club_id
        self.current_club_name = current_club_name
        self.market_value_in_eur = market_value_in_eur
        self.highest_market_value_in_eur = highest_market_value_in_eur
        self.contract_expiration_date = contract_expiration_date


        self.presenze = int(presenze) if presenze is not None else 0
        self.minuti_totali = int(minuti_totali) if minuti_totali is not None else 0
        self.gol = int(gol) if gol is not None else 0
        self.assist = int(assist) if assist is not None else 0
        self.gialli = int(gialli) if gialli is not None else 0
        self.rossi = int(rossi) if rossi is not None else 0


        novanta = (self.minuti_totali / 90) if self.minuti_totali else 0
        self.gol_90 = round(self.gol / novanta, 3) if novanta > 0 else 0.0
        self.assist_90 = round(self.assist / novanta, 3) if novanta > 0 else 0.0


    def __hash__(self):
        return hash(self.player_id)

    def __eq__(self, other):
        return self.player_id == other.player_id

    def __str__(self):
        return (f"{self.name} ({self.position}, {self.sub_position}) - "
                f"{self.presenze} presenze, {self.minuti_totali}', "
                f"{self.gol} gol, {self.assist} assist "
                f"(gol/90={self.gol_90}, assist/90={self.assist_90}) - "
                f"valore={self.market_value_in_eur} €")

    def __repr__(self):
        return self.__str__()

from database.DB_connect import DBConnect
from model.club import Club
from model.competizione import Competizione
from model.player import Player

class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_rendimento_giocatori(competition_id, season, ruolo=None, sotto_ruolo=None, minuti_minimi=900):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT p.player_id,
                       p.name,
                       p.position,
                       p.sub_position,
                       p.date_of_birth,
                       p.current_club_id,
                       p.current_club_name,
                       p.market_value_in_eur,
                       p.highest_market_value_in_eur,
                       p.contract_expiration_date,
                       COUNT(a.appearance_id)      AS presenze,
                       COALESCE(SUM(a.minutes_played), 0) AS minuti_totali,
                       COALESCE(SUM(a.goals), 0)          AS gol,
                       COALESCE(SUM(a.assists), 0)        AS assist,
                       COALESCE(SUM(a.yellow_cards), 0)   AS gialli,
                       COALESCE(SUM(a.red_cards), 0)      AS rossi
                FROM players p
                JOIN appearances a ON a.player_id = p.player_id
                JOIN games g       ON g.game_id = a.game_id
                WHERE g.competition_id = %s
                  AND g.season = %s
                  {filtro_ruolo}
                  {filtro_sotto_ruolo}
                GROUP BY p.player_id, p.name, p.position, p.sub_position, p.date_of_birth,
                         p.current_club_id, p.current_club_name,
                         p.market_value_in_eur, p.highest_market_value_in_eur,
                         p.contract_expiration_date
                HAVING minuti_totali >= %s
                ORDER BY minuti_totali DESC
            """

        params = [competition_id, season]
        filtro_ruolo = ""
        if ruolo:
            filtro_ruolo = "AND p.position = %s"
            params.append(ruolo)
        filtro_sotto_ruolo = ""
        if sotto_ruolo:
            filtro_sotto_ruolo = "AND p.sub_position = %s"
            params.append(sotto_ruolo)
        query = query.format(filtro_ruolo=filtro_ruolo, filtro_sotto_ruolo=filtro_sotto_ruolo)
        params.append(minuti_minimi)

        cursor.execute(query, tuple(params))

        risultato = []
        for row in cursor:
            risultato.append(Player(
                player_id=row["player_id"],
                name=row["name"],
                position=row["position"],
                sub_position=row["sub_position"],
                date_of_birth=row["date_of_birth"],
                current_club_id=row["current_club_id"],
                current_club_name=row["current_club_name"],
                market_value_in_eur=row["market_value_in_eur"],
                highest_market_value_in_eur=row["highest_market_value_in_eur"],
                contract_expiration_date=row["contract_expiration_date"],
                presenze=row["presenze"],
                minuti_totali=row["minuti_totali"],
                gol=row["gol"],
                assist=row["assist"],
                gialli=row["gialli"],
                rossi=row["rossi"],
            ))

        cursor.close()
        conn.close()
        return risultato

    @staticmethod
    def get_giocatori_club(club_id):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT DISTINCT player_id,
                       name,
                       position,
                       sub_position,
                       date_of_birth,
                       country_of_citizenship,
                       foot,
                       market_value_in_eur,
                       contract_expiration_date,
                       last_season
                FROM players
                WHERE current_club_id = %s
                  AND last_season = (SELECT MAX(last_season) FROM players)
            """
        cursor.execute(query, (club_id,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_competizione_club(club_id):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT c.domestic_competition_id,
                       (SELECT MAX(g.season) FROM games g
                        WHERE g.competition_id = c.domestic_competition_id) AS ultima_stagione
                FROM clubs c
                WHERE c.club_id = %s
            """
        cursor.execute(query, (club_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_rendimento_club(club_id, competition_id, season):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT a.player_id,
                       p.position,
                       p.date_of_birth,
                       COALESCE(SUM(a.minutes_played), 0) AS minuti_totali,
                       COALESCE(SUM(a.goals), 0)          AS gol,
                       COALESCE(SUM(a.assists), 0)        AS assist
                FROM appearances a
                JOIN games g   ON g.game_id = a.game_id
                JOIN players p ON p.player_id = a.player_id
                WHERE a.player_club_id = %s
                  AND g.competition_id = %s
                  AND g.season = %s
                GROUP BY a.player_id, p.position, p.date_of_birth
            """
        cursor.execute(query, (club_id, competition_id, season))
        result = cursor.fetchall()

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_movimenti_mercato(club_id, anni=3):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT t.player_id,
                       p.date_of_birth,
                       t.transfer_date,
                       t.from_club_id,
                       t.to_club_id,
                       t.transfer_fee
                FROM transfers t
                JOIN players p ON p.player_id = t.player_id
                WHERE (t.to_club_id = %s OR t.from_club_id = %s)
                  AND t.transfer_date >= DATE_SUB(CURDATE(), INTERVAL %s YEAR)
                  AND t.transfer_date <= CURDATE()
            """
        cursor.execute(query, (club_id, club_id, anni))
        result = cursor.fetchall()

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_ultima_stagione(competition_id):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT MAX(season) AS ultima_stagione FROM games WHERE competition_id = %s"
        cursor.execute(query, (competition_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        return row["ultima_stagione"] if row else None

    @staticmethod
    def get_club():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """ select distinct c.club_id , c.name
                        from clubs c
                        order by c.name """

        cursor.execute(query)

        for row in cursor:
            result.append(Club(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_competizioni():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """ select distinct c.competition_id , c.name 
                        from competitions c 
    """

        cursor.execute(query)

        for row in cursor:
            result.append(Competizione(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_campionati_domestici():

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT DISTINCT competition_id, name
                FROM competitions
                WHERE type = 'domestic_league'
            """
        cursor.execute(query)

        result = [Competizione(**row) for row in cursor]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_sotto_ruoli(ruolo=None):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        if ruolo:
            query = """ select distinct p.sub_position
                            from players p
                            where p.position = %s and p.sub_position is not null """
            cursor.execute(query, (ruolo,))
        else:
            query = """ select distinct p.sub_position
                            from players p
                            where p.sub_position is not null """
            cursor.execute(query)

        result = [row["sub_position"] for row in cursor]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_valore_medio_rosa_club(club_id):

        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT AVG(market_value_in_eur) AS valore_medio
                FROM players
                WHERE current_club_id = %s
                  AND last_season = (SELECT MAX(last_season) FROM players)
                  AND market_value_in_eur IS NOT NULL
            """
        cursor.execute(query, (club_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        return float(row["valore_medio"]) if row and row["valore_medio"] is not None else None

    @staticmethod
    def get_ruoli():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """ select distinct p.`position` 
                        from players p 

            """

        cursor.execute(query)

        for row in cursor:
            result.append((row["position"]))

        cursor.close()
        conn.close()
        return result


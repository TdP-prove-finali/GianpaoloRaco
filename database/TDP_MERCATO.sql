-- TDP_MERCATO.appearances definition

CREATE TABLE `appearances` (
  `appearance_id` varchar(30) NOT NULL,
  `game_id` int DEFAULT NULL,
  `player_id` int DEFAULT NULL,
  `player_club_id` int DEFAULT NULL,
  `player_current_club_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `player_name` varchar(150) DEFAULT NULL,
  `competition_id` varchar(10) DEFAULT NULL,
  `yellow_cards` int DEFAULT NULL,
  `red_cards` int DEFAULT NULL,
  `goals` int DEFAULT NULL,
  `assists` int DEFAULT NULL,
  `minutes_played` int DEFAULT NULL,
  PRIMARY KEY (`appearance_id`),
  KEY `idx_a_player` (`player_id`),
  KEY `idx_a_game` (`game_id`),
  KEY `idx_a_comp` (`competition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.clubs definition

CREATE TABLE `clubs` (
  `club_id` int NOT NULL,
  `club_code` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `domestic_competition_id` varchar(10) DEFAULT NULL,
  `total_market_value` decimal(15,2) DEFAULT NULL,
  `squad_size` int DEFAULT NULL,
  `average_age` decimal(4,1) DEFAULT NULL,
  `foreigners_number` int DEFAULT NULL,
  `foreigners_percentage` decimal(5,1) DEFAULT NULL,
  `national_team_players` int DEFAULT NULL,
  `stadium_name` varchar(100) DEFAULT NULL,
  `stadium_seats` int DEFAULT NULL,
  `net_transfer_record` varchar(30) DEFAULT NULL,
  `coach_name` varchar(100) DEFAULT NULL,
  `last_season` int DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`club_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.competitions definition

CREATE TABLE `competitions` (
  `competition_id` varchar(10) NOT NULL,
  `competition_code` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `sub_type` varchar(50) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `country_id` int DEFAULT NULL,
  `country_name` varchar(50) DEFAULT NULL,
  `domestic_league_code` varchar(10) DEFAULT NULL,
  `confederation` varchar(20) DEFAULT NULL,
  `total_clubs` int DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`competition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.game_events definition

CREATE TABLE `game_events` (
  `game_event_id` varchar(40) NOT NULL,
  `date` date DEFAULT NULL,
  `game_id` int DEFAULT NULL,
  `minute` int DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `club_id` int DEFAULT NULL,
  `club_name` varchar(100) DEFAULT NULL,
  `player_id` int DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `player_in_id` int DEFAULT NULL,
  `player_assist_id` int DEFAULT NULL,
  PRIMARY KEY (`game_event_id`),
  KEY `idx_e_game` (`game_id`),
  KEY `idx_e_player` (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.games definition

CREATE TABLE `games` (
  `game_id` int NOT NULL,
  `competition_id` varchar(10) DEFAULT NULL,
  `season` int DEFAULT NULL,
  `round` varchar(50) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `home_club_id` int DEFAULT NULL,
  `away_club_id` int DEFAULT NULL,
  `home_club_goals` int DEFAULT NULL,
  `away_club_goals` int DEFAULT NULL,
  `home_club_position` int DEFAULT NULL,
  `away_club_position` int DEFAULT NULL,
  `home_club_manager_name` varchar(100) DEFAULT NULL,
  `away_club_manager_name` varchar(100) DEFAULT NULL,
  `stadium` varchar(100) DEFAULT NULL,
  `attendance` int DEFAULT NULL,
  `referee` varchar(100) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `home_club_formation` varchar(50) DEFAULT NULL,
  `away_club_formation` varchar(50) DEFAULT NULL,
  `home_club_name` varchar(100) DEFAULT NULL,
  `away_club_name` varchar(100) DEFAULT NULL,
  `aggregate` varchar(10) DEFAULT NULL,
  `competition_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`game_id`),
  KEY `idx_g_comp_season` (`competition_id`,`season`),
  KEY `idx_g_home` (`home_club_id`),
  KEY `idx_g_away` (`away_club_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.player_valuations definition

CREATE TABLE `player_valuations` (
  `player_id` int NOT NULL,
  `date` date NOT NULL,
  `market_value_in_eur` bigint DEFAULT NULL,
  `current_club_name` varchar(100) DEFAULT NULL,
  `current_club_id` int DEFAULT NULL,
  `player_club_domestic_competition_id` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`player_id`,`date`),
  KEY `idx_v_club` (`current_club_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.players definition

CREATE TABLE `players` (
  `player_id` int NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `name` varchar(150) DEFAULT NULL,
  `last_season` int DEFAULT NULL,
  `current_club_id` int DEFAULT NULL,
  `player_code` varchar(150) DEFAULT NULL,
  `country_of_birth` varchar(75) DEFAULT NULL,
  `city_of_birth` varchar(100) DEFAULT NULL,
  `country_of_citizenship` varchar(75) DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `sub_position` varchar(50) DEFAULT NULL,
  `position` varchar(25) DEFAULT NULL,
  `foot` varchar(10) DEFAULT NULL,
  `height_in_cm` int DEFAULT NULL,
  `contract_expiration_date` datetime DEFAULT NULL,
  `agent_name` varchar(100) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `international_caps` int DEFAULT NULL,
  `international_goals` int DEFAULT NULL,
  `current_national_team_id` int DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `current_club_domestic_competition_id` varchar(10) DEFAULT NULL,
  `current_club_name` varchar(100) DEFAULT NULL,
  `market_value_in_eur` bigint DEFAULT NULL,
  `highest_market_value_in_eur` bigint DEFAULT NULL,
  PRIMARY KEY (`player_id`),
  KEY `idx_pl_club` (`current_club_id`),
  KEY `idx_pl_position` (`position`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- TDP_MERCATO.transfers definition

CREATE TABLE `transfers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `player_id` int DEFAULT NULL,
  `transfer_date` date DEFAULT NULL,
  `transfer_season` varchar(10) DEFAULT NULL,
  `from_club_id` int DEFAULT NULL,
  `to_club_id` int DEFAULT NULL,
  `from_club_name` varchar(100) DEFAULT NULL,
  `to_club_name` varchar(100) DEFAULT NULL,
  `transfer_fee` decimal(15,3) DEFAULT NULL,
  `market_value_in_eur` decimal(15,3) DEFAULT NULL,
  `player_name` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_t_player` (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=65536 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
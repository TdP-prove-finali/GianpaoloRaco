# GianpaoloRaco
Consulente virtuale per il mercato calcistico: identificazione di giocatori sottovalutati e ottimizzazione della campagna acquisti sotto vincolo di budget

### Descrizione del problema proposto

Un direttore sportivo deve rafforzare la rosa con un budget limitato, scegliendo tra migliaia di giocatori sul mercato. Le decisioni coinvolgono simultaneamente più dimensioni: i ruoli da coprire, il budget disponibile (incrementabile con le cessioni), l'età e le prospettive di rivalutazione dei giocatori, e il rapporto tra costo e rendimento atteso. L'applicazione proposta agisce da consulente di mercato: analizza la rosa attuale individuandone le carenze (ruoli scoperti, struttura d'età, giocatori in declino), identifica sul mercato i giocatori "sottovalutati" (rendimento elevato rispetto al valore di mercato), suggerisce per ogni giocatore i sostituti più simili a costo inferiore, e calcola il piano di mercato ottimale — quali giocatori acquistare ed eventualmente cedere — che massimizza il miglioramento della rosa nel rispetto del budget e dei vincoli di composizione.

### Descrizione della rilevanza gestionale del problema

Il problema è un caso concreto di allocazione ottima di un budget su un portafoglio di asset: i giocatori sono investimenti con costo, rendimento atteso e valore di rivendita, e la campagna acquisti è una decisione di procurement multi-vincolo, strutturalmente identica alla selezione di fornitori o di progetti d'investimento sotto vincolo di capitale. Nel calcio moderno la sostenibilità economica (fair play finanziario, gestione delle plusvalenze) rende queste decisioni sempre più data-driven: i club si dotano di strutture di analytics proprio per individuare inefficienze di prezzo sul mercato. Il progetto mostra come tecniche di ricerca operativa e analisi dei dati supportino una decisione gestionale reale ad alto impatto economico.

### Descrizione dei data-set per la valutazione

Tutti i dati provengono da un'unica fonte: il dataset pubblico **"Football Data from Transfermarkt"** disponibile su Kaggle (licenza CC0), già strutturato in tabelle relazionali tra loro collegate — `players` (anagrafica, ruolo, piede, altezza, scadenza contratto, valore attuale e massimo storico), `appearances` (presenze, minuti, gol, assist e cartellini per giocatore/partita), `games`, `clubs`, `competitions`, `player_valuations` (serie storica dei valori di mercato) e `transfers` (storico trasferimenti con prezzo pagato). Il dataset è stato importato in un'unica base di dati relazionale MySQL, che è la sola sorgente interrogata dall'applicazione.

La dimensione è significativa: circa 37.000 giocatori, 80.000 partite, 1.800.000 record di presenze, 520.000 valutazioni di mercato e 99.000 trasferimenti, relativi ai principali campionati europei su più stagioni.

### Descrizione preliminare degli algoritmi coinvolti


1. **Scoring dei giocatori e identificazione dei sottovalutati**: costruzione di un indice di rendimento per ruolo a partire dai dati di presenza (minuti, gol e assist per 90 minuti, presenze, disciplina), normalizzato per età e campionato; il confronto tra rendimento e valore di mercato corrente produce una graduatoria di "occasioni di mercato". Lo storico dei trasferimenti (prezzo pagato vs valore) è usato per calibrare l'indicatore.

2. **Grafo di similarità tra giocatori**: grafo pesato, non orientato e semplice, i cui vertici sono i giocatori di un ruolo e di una stagione selezionati (con un vettore di caratteristiche normalizzate: età, minutaggio, gol/90', assist/90', valore e suo trend), e i cui archi collegano due giocatori solo se la distanza euclidea pesata tra i profili è inferiore a una soglia regolabile; il peso dell'arco è la distanza stessa. Sul grafo si realizzano: interrogazioni di vicinato ("i sostituti più simili al giocatore X con valore inferiore a Y"), cammini minimi con l'algoritmo di Dijkstra (catene di similarità per allargare progressivamente la ricerca quando i vicini diretti non sono abbordabili) e componenti connesse (segmenti di mercato: cluster di giocatori intercambiabili, dove l'offerta è più ampia e i prezzi più negoziabili).

3. **Ottimizzazione della campagna acquisti**: la selezione del sottoinsieme di acquisti (ed eventuali cessioni) che massimizza il miglioramento complessivo della rosa sotto vincolo di budget, di numero massimo di acquisti e di copertura dei ruoli è un problema di tipo knapsack multi-vincolo. Verrà affrontato con ricerca ricorsiva esatta con potatura sulle istanze ridotte (candidati pre-filtrati dallo scoring) valutando qualità delle soluzioni e tempi di calcolo.

4. **Valutazione probabilistica del piano**: il rendimento futuro dei giocatori acquistati è incerto; tramite simulazione Monte Carlo (rendimenti campionati dalle distribuzioni storiche per età e ruolo) si valuterà la robustezza dei piani proposti, confrontando scenari alternativi in termini di miglioramento atteso e rischio.

### Descrizione preliminare delle funzionalità previste per l'applicazione software

L'applicazione sarà una applicazione desktop sviluppata in linguaggio Python, con interfaccia grafica realizzata con il framework Flet e accesso alla base di dati MySQL tramite il pattern DAO, secondo l'architettura illustrata nel corso. L'utente potrà: selezionare un club e visualizzare l'analisi della rosa (valore, struttura d'età, copertura dei ruoli, contratti in scadenza, punti deboli); impostare budget e obiettivi della campagna (ruoli da rafforzare, vincoli su età o campionato di provenienza); consultare la classifica dei giocatori sottovalutati filtrabile per ruolo e fascia di prezzo; per un giocatore dato, ottenere i sostituti più simili a costo inferiore tramite il grafo di similarità, con soglia di similarità regolabile; generare il piano di mercato ottimale (acquisti e cessioni suggerite) e confrontare più scenari con indicatori e grafici (miglioramento atteso della rosa, spesa, rischio stimato).

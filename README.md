# PersonalExpenseSystem

Sistema di gestione delle spese personali e del budget, su console.
Progetto finale di Programmazione - Davide Di Giacomo.

Il programma è scritto in **Python** e usa un database relazionale **SQLite**.
Permette di:

- gestire le categorie di spesa
- inserire le spese giornaliere
- definire un budget mensile per categoria
- vedere tre report (totale per categoria, spese mensili vs budget, elenco spese per data)

## Struttura del repository

```
PersonalExpenseSystem/
├── src/
│   └── main.py          codice sorgente del programma
├── sql/
│   └── database.sql     creazione tabelle + dati di esempio
├── demo/
│   └── demo_video.mp4   video dimostrativo
└── README.md
```

## Requisiti

- **Python 3.10 o superiore** (serve per il costrutto `match`/`case` usato per i menu)
- Librerie: solo librerie standard di Python
  - `sqlite3` (database, già incluso in Python)
  - `os`
  - `datetime`

Non bisogna installare niente con pip e non serve un server per il database:
SQLite salva tutto in un file.

Per controllare la versione di Python:

```bash
python3 --version
```

(su Windows il comando di solito è `python` oppure `py`)

## Come eseguire il programma

Non serve nessuna compilazione, Python è interpretato.

1. Scaricare il repository:

```bash
git clone https://github.com/Mgpull/PersonalExpenseSystem.git
```

2. Entrare nella cartella:

```bash
cd PersonalExpenseSystem
```

3. Avviare il programma (comando esatto):

```bash
python3 src/main.py
```

Su Windows:

```bash
python src\main.py
```

Al primo avvio il programma crea il file `src/spese.db` eseguendo lo script
`sql/database.sql`, quindi il database contiene già alcune categorie, spese e
budget di esempio. Per ripartire da zero basta cancellare `src/spese.db`.

## Uso

All'avvio compare il menu principale:

```
-------------------------
 SISTEMA SPESE PERSONALI
-------------------------
1. Gestione Categorie
2. Inserisci Spesa
3. Definisci Budget Mensile
4. Visualizza Report
5. Esci
-------------------------
Inserisci la tua scelta:
```

- le date vanno scritte come `YYYY-MM-DD` (es. `2025-01-15`)
- i mesi del budget come `YYYY-MM` (es. `2025-01`)
- per gli importi si può usare sia il punto che la virgola

## Demo

Il video `demo/demo_video.mp4` mostra l'avvio del programma, l'uso dei menu,
l'inserimento di una categoria, di una spesa e di un budget e la generazione
dei report.

# Sistema di Gestione delle Spese Personali e del Budget
# Progetto finale di Programmazione
#
# Programma su console scritto in Python che usa un database SQLite.
# Il file del database (spese.db) viene creato nella stessa cartella del
# programma usando lo script sql/database.sql la prima volta che si avvia.

import os
import sqlite3
from datetime import datetime

CARTELLA = os.path.dirname(os.path.abspath(__file__))
FILE_DB = os.path.join(CARTELLA, "spese.db")
FILE_SQL = os.path.join(CARTELLA, "..", "sql", "database.sql")


# ---------------------------------------------------------------
# Database
# ---------------------------------------------------------------

def apri_database():
    nuovo = not os.path.exists(FILE_DB)
    conn = sqlite3.connect(FILE_DB)
    # in SQLite le chiavi esterne vanno attivate ad ogni connessione
    conn.execute("PRAGMA foreign_keys = ON")
    if nuovo:
        with open(FILE_SQL, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    return conn


def cerca_categoria(conn, nome):
    # ritorna l'id della categoria oppure None se non esiste
    riga = conn.execute(
        "SELECT id_categoria FROM categorie WHERE lower(nome) = lower(?)",
        (nome,)).fetchone()
    if riga is None:
        return None
    return riga[0]


# ---------------------------------------------------------------
# Funzioni di supporto per l'input
# ---------------------------------------------------------------

def leggi_numero(messaggio):
    testo = input(messaggio).strip().replace(",", ".")
    try:
        return float(testo)
    except ValueError:
        return None


def data_valida(testo, formato):
    try:
        datetime.strptime(testo, formato)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------
# MODULO 1 - Gestione categorie
# ---------------------------------------------------------------

def gestione_categorie(conn):
    print("\n--- GESTIONE CATEGORIE ---")
    righe = conn.execute("SELECT nome FROM categorie ORDER BY nome").fetchall()
    if len(righe) > 0:
        print("Categorie presenti:", ", ".join(r[0] for r in righe))

    nome = input("Nome della nuova categoria: ").strip()

    if nome == "":
        print("Errore: il nome della categoria non puo' essere vuoto.")
        return

    if cerca_categoria(conn, nome) is not None:
        print("La categoria esiste gia'.")
        return

    conn.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
    conn.commit()
    print("Categoria inserita correttamente.")


# ---------------------------------------------------------------
# MODULO 2 - Inserimento spesa
# ---------------------------------------------------------------

def inserisci_spesa(conn):
    print("\n--- INSERISCI SPESA ---")
    data = input("Data (YYYY-MM-DD): ").strip()
    importo = leggi_numero("Importo: ")
    categoria = input("Categoria: ").strip()
    descrizione = input("Descrizione (facoltativa): ").strip()

    if not data_valida(data, "%Y-%m-%d"):
        print("Errore: data non valida, usare il formato YYYY-MM-DD.")
        return

    if importo is None or importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return

    id_cat = cerca_categoria(conn, categoria)
    if id_cat is None:
        print("Errore: la categoria non esiste.")
        return

    if descrizione == "":
        descrizione = None

    conn.execute(
        "INSERT INTO spese (data, importo, id_categoria, descrizione) "
        "VALUES (?, ?, ?, ?)",
        (data, round(importo, 2), id_cat, descrizione))
    conn.commit()
    print("Spesa inserita correttamente.")


# ---------------------------------------------------------------
# MODULO 3 - Budget mensile
# ---------------------------------------------------------------

def definisci_budget(conn):
    print("\n--- DEFINISCI BUDGET MENSILE ---")
    mese = input("Mese (YYYY-MM): ").strip()
    categoria = input("Categoria: ").strip()
    importo = leggi_numero("Importo del budget: ")

    if not data_valida(mese, "%Y-%m"):
        print("Errore: mese non valido, usare il formato YYYY-MM.")
        return

    if importo is None or importo <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        return

    id_cat = cerca_categoria(conn, categoria)
    if id_cat is None:
        print("Errore: la categoria non esiste.")
        return

    # se c'e' gia' un budget per quel mese e categoria lo aggiorno,
    # altrimenti lo inserisco
    esistente = conn.execute(
        "SELECT id_budget FROM budget WHERE mese = ? AND id_categoria = ?",
        (mese, id_cat)).fetchone()

    if esistente is None:
        conn.execute(
            "INSERT INTO budget (mese, id_categoria, importo) VALUES (?, ?, ?)",
            (mese, id_cat, round(importo, 2)))
    else:
        conn.execute(
            "UPDATE budget SET importo = ? WHERE id_budget = ?",
            (round(importo, 2), esistente[0]))
    conn.commit()
    print("Budget mensile salvato correttamente.")


# ---------------------------------------------------------------
# MODULO 4 - Report
# ---------------------------------------------------------------

def report_totale_categorie(conn):
    righe = conn.execute(
        "SELECT c.nome, SUM(s.importo) "
        "FROM categorie c JOIN spese s ON s.id_categoria = c.id_categoria "
        "GROUP BY c.nome ORDER BY c.nome").fetchall()

    print("\nCategoria".ljust(18, ".") + "Totale Speso")
    if len(righe) == 0:
        print("Nessuna spesa registrata.")
    for nome, totale in righe:
        print(nome.ljust(17, ".") + "%.2f" % totale)


def report_mensile_budget(conn):
    righe = conn.execute(
        "SELECT b.mese, c.nome, b.importo, IFNULL(SUM(s.importo), 0) "
        "FROM budget b "
        "JOIN categorie c ON c.id_categoria = b.id_categoria "
        "LEFT JOIN spese s ON s.id_categoria = b.id_categoria "
        "                 AND substr(s.data, 1, 7) = b.mese "
        "GROUP BY b.id_budget "
        "ORDER BY b.mese, c.nome").fetchall()

    if len(righe) == 0:
        print("\nNessun budget definito.")
        return

    for mese, categoria, budget, speso in righe:
        if speso > budget:
            stato = "SUPERAMENTO BUDGET"
        elif speso == budget:
            stato = "BUDGET RAGGIUNTO"
        else:
            stato = "NEI LIMITI (restano %.2f)" % (budget - speso)
        print()
        print("Mese:", mese)
        print("Categoria:", categoria)
        print("Budget: %.2f" % budget)
        print("Speso: %.2f" % speso)
        print("Stato:", stato)


def report_elenco_spese(conn):
    righe = conn.execute(
        "SELECT s.data, c.nome, s.importo, IFNULL(s.descrizione, '') "
        "FROM spese s JOIN categorie c ON c.id_categoria = s.id_categoria "
        "ORDER BY s.data, s.id_spesa").fetchall()

    print()
    print("%-12s %-14s %10s  %s" % ("Data", "Categoria", "Importo", "Descrizione"))
    print("-" * 62)
    if len(righe) == 0:
        print("Nessuna spesa registrata.")
    for data, categoria, importo, descrizione in righe:
        print("%-12s %-14s %10.2f  %s" % (data, categoria, importo, descrizione))


def visualizza_report(conn):
    while True:
        print("\n------ MENU REPORT ------")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese")
        print("4. Ritorna al menu principale")
        scelta = input("Inserisci la tua scelta: ").strip()

        match scelta:
            case "1":
                report_totale_categorie(conn)
            case "2":
                report_mensile_budget(conn)
            case "3":
                report_elenco_spese(conn)
            case "4":
                return
            case _:
                print("Scelta non valida. Riprovare.")


# ---------------------------------------------------------------
# Menu principale
# ---------------------------------------------------------------

def menu_principale():
    print()
    print("-------------------------")
    print(" SISTEMA SPESE PERSONALI")
    print("-------------------------")
    print("1. Gestione Categorie")
    print("2. Inserisci Spesa")
    print("3. Definisci Budget Mensile")
    print("4. Visualizza Report")
    print("5. Esci")
    print("-------------------------")
    return input("Inserisci la tua scelta: ").strip()


def main():
    print("Benvenuto nel Sistema di Gestione delle Spese Personali!")
    conn = apri_database()

    uscita = False
    while not uscita:
        scelta = menu_principale()
        try:
            match scelta:
                case "1":
                    gestione_categorie(conn)
                case "2":
                    inserisci_spesa(conn)
                case "3":
                    definisci_budget(conn)
                case "4":
                    visualizza_report(conn)
                case "5":
                    uscita = True
                case _:
                    print("Scelta non valida. Riprovare.")
        except sqlite3.Error as e:
            # i vincoli del database fanno da ultimo controllo
            print("Errore del database:", e)
            conn.rollback()

    conn.close()
    print("Arrivederci!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgramma terminato.")

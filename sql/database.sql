-- =====================================================
-- Sistema di Gestione delle Spese Personali e del Budget
-- Script di creazione del database (SQLite)
-- =====================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS budget;
DROP TABLE IF EXISTS spese;
DROP TABLE IF EXISTS categorie;

-- Tabella delle categorie di spesa
CREATE TABLE categorie (
    id_categoria  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL UNIQUE,
    CHECK (length(trim(nome)) > 0)
);

-- Tabella delle spese
CREATE TABLE spese (
    id_spesa      INTEGER PRIMARY KEY AUTOINCREMENT,
    data          TEXT    NOT NULL,
    importo       REAL    NOT NULL CHECK (importo > 0),
    id_categoria  INTEGER NOT NULL,
    descrizione   TEXT,
    CHECK (data GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabella dei budget mensili (un solo budget per categoria e mese)
CREATE TABLE budget (
    id_budget     INTEGER PRIMARY KEY AUTOINCREMENT,
    mese          TEXT    NOT NULL,
    id_categoria  INTEGER NOT NULL,
    importo       REAL    NOT NULL CHECK (importo > 0),
    CHECK (mese GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'),
    UNIQUE (mese, id_categoria),
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- =====================================================
-- Dati di esempio
-- =====================================================

INSERT INTO categorie (nome) VALUES
    ('Alimentari'),
    ('Trasporti'),
    ('Svago'),
    ('Bollette');

INSERT INTO spese (data, importo, id_categoria, descrizione) VALUES
    ('2025-01-03', 85.40, 1, 'Spesa settimanale'),
    ('2025-01-08', 35.00, 2, 'Abbonamento bus'),
    ('2025-01-10', 110.10, 1, 'Supermercato'),
    ('2025-01-15', 25.00, 1, 'Pranzo'),
    ('2025-01-18', 45.00, 2, 'Benzina'),
    ('2025-01-20', 18.50, 3, 'Cinema'),
    ('2025-01-24', 100.00, 1, 'Spesa mensile'),
    ('2025-01-28', 40.00, 2, 'Treno'),
    ('2025-01-30', 62.30, 4, 'Bolletta luce'),
    ('2025-02-02', 54.20, 1, 'Spesa'),
    ('2025-02-05', 30.00, 3, 'Concerto');

INSERT INTO budget (mese, id_categoria, importo) VALUES
    ('2025-01', 1, 300.00),
    ('2025-01', 2, 150.00),
    ('2025-01', 3, 50.00),
    ('2025-02', 1, 250.00);

-- =====================================================
-- Query usate per i report
-- =====================================================

-- Report 1: totale spese per categoria
-- SELECT c.nome, SUM(s.importo) AS totale
-- FROM categorie c JOIN spese s ON s.id_categoria = c.id_categoria
-- GROUP BY c.nome ORDER BY c.nome;

-- Report 2: speso per mese e categoria confrontato con il budget
-- SELECT b.mese, c.nome, b.importo AS budget, IFNULL(SUM(s.importo), 0) AS speso
-- FROM budget b
-- JOIN categorie c ON c.id_categoria = b.id_categoria
-- LEFT JOIN spese s ON s.id_categoria = b.id_categoria
--                  AND substr(s.data, 1, 7) = b.mese
-- GROUP BY b.id_budget ORDER BY b.mese, c.nome;

-- Report 3: elenco completo delle spese ordinate per data
-- SELECT s.data, c.nome, s.importo, IFNULL(s.descrizione, '')
-- FROM spese s JOIN categorie c ON c.id_categoria = s.id_categoria
-- ORDER BY s.data, s.id_spesa;

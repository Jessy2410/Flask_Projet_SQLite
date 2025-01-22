import sqlite3

# Connexion à la base de données
connection = sqlite3.connect('database2.db')

# Création des tables à partir du fichier schema.sql
with open('schema.sql', 'w') as schema_file:
    schema_file.write("""
-- Table pour les livres
CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    genre TEXT,
    disponible INTEGER DEFAULT 1, -- 1 pour disponible, 0 pour non disponible
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les utilisateurs
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Utilisateur', 'Administrateur')) -- Rôles : Utilisateur ou Administrateur
);

-- Table pour les emprunts
CREATE TABLE emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    livre_id INTEGER NOT NULL,
    date_emprunt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_retour TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('En cours', 'Terminé')), -- Statut de l'emprunt
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (livre_id) REFERENCES livres(id)
);

-- Table pour les clients
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    adresse TEXT NOT NULL
);
    """)
    
with open('schema.sql') as f:
    connection.executescript(f.read())

# Ajout des données initiales
cur = connection.cursor()

# Ajout des clients
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('DUPONT', 'Emilie', '123, Rue des Lilas, 75001 Paris'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('LEROUX', 'Lucas', '456, Avenue du Soleil, 31000 Toulouse'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('MARTIN', 'Amandine', '789, Rue des Érables, 69002 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('TREMBLAY', 'Antoine', '1010, Boulevard de la Mer, 13008 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('LAMBERT', 'Sarah', '222, Avenue de la Liberté, 59000 Lille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('GAGNON', 'Nicolas', '456, Boulevard des Cerisiers, 69003 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('DUBOIS', 'Charlotte', '789, Rue des Roses, 13005 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)", ('LEFEVRE', 'Thomas', '333, Rue de la Paix, 75002 Paris'))

# Ajout des utilisateurs
cur.execute("INSERT INTO utilisateurs (nom, email, role) VALUES (?, ?, ?)", ('Admin', 'admin@bibliotheque.com', 'Administrateur'))
cur.execute("INSERT INTO utilisateurs (nom, email, role) VALUES (?, ?, ?)", ('Utilisateur1', 'utilisateur1@bibliotheque.com', 'Utilisateur'))
cur.execute("INSERT INTO utilisateurs (nom, email, role) VALUES (?, ?, ?)", ('Utilisateur2', 'utilisateur2@bibliotheque.com', 'Utilisateur'))

# Ajout des livres
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('1984', 'George Orwell', 'Dystopie'))
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('Le Petit Prince', 'Antoine de Saint-Exupéry', 'Conte'))
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('L\'Étranger', 'Albert Camus', 'Philosophie'))
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('Harry Potter à l\'école des sorciers', 'J.K. Rowling', 'Fantastique'))
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('Les Misérables', 'Victor Hugo', 'Roman historique'))
cur.execute("INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)", ('La Peste', 'Albert Camus', 'Philosophie'))

connection.commit()
connection.close()

print("Base de données initialisée avec succès.")

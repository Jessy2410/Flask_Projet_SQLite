from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')#comm

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route pour enregistrer un livre
@app.route('/enregistrer_livre', methods=['GET', 'POST'])
def enregistrer_livre():
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        genre = request.form.get('genre', '')

        # Connexion à la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)', (titre, auteur, genre))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))

    return render_template('formulaire_livre.html')

# Route pour afficher les livres
@app.route('/liste_livres')
def liste_livres():
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres')
    livres = cursor.fetchall()
    conn.close()
    return render_template('liste_livres.html', livres=livres)

# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    utilisateur_id = session.get('utilisateur_id')

    if utilisateur_id:
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()
        # Vérifier si le livre est disponible
        cursor.execute('SELECT disponible FROM livres WHERE id = ?', (livre_id,))
        disponible = cursor.fetchone()

        if disponible and disponible[0] == 1:
            # Enregistrer l'emprunt
            cursor.execute('INSERT INTO emprunts (utilisateur_id, livre_id, statut) VALUES (?, ?, ?)',
                           (utilisateur_id, livre_id, 'En cours'))
            # Marquer le livre comme non disponible
            cursor.execute('UPDATE livres SET disponible = 0 WHERE id = ?', (livre_id,))
            conn.commit()

        conn.close()
        return redirect(url_for('liste_livres'))

    return redirect(url_for('authentification'))

# Route pour afficher les emprunts
@app.route('/emprunts')
def afficher_emprunts():
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, l.titre, u.nom, e.date_emprunt, e.date_retour, e.statut
        FROM emprunts e
        JOIN livres l ON e.livre_id = l.id
        JOIN utilisateurs u ON e.utilisateur_id = u.id
    ''')
    emprunts = cursor.fetchall()
    conn.close()
    return render_template('emprunts.html', emprunts=emprunts)

# Route pour retourner un livre
@app.route('/retourner_livre/<int:emprunt_id>', methods=['POST'])
def retourner_livre(emprunt_id):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    # Mettre à jour le statut de l'emprunt et marquer le livre comme disponible
    cursor.execute('''
        UPDATE emprunts
        SET statut = 'Terminé', date_retour = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (emprunt_id,))
    cursor.execute('''
        UPDATE livres
        SET disponible = 1
        WHERE id = (SELECT livre_id FROM emprunts WHERE id = ?)
    ''', (emprunt_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('afficher_emprunts'))

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password': # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_by_nom():
    message = ""
    results = []

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()

        if nom:
            try:
                # Connexion à la base SQLite
                conn = sqlite3.connect('database2.db')
                cursor = conn.cursor()

                # Requête SQL pour rechercher le client par nom
                cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom,))
                results = cursor.fetchall()

                if not results:
                    message = "Aucun client trouvé avec ce nom."

                conn.close()
            except Exception as e:
                message = f"Erreur lors de la recherche : {e}"
        else:
            message = "Veuillez entrer un nom."

    return render_template('searchUser.html', results=results, message=message)


@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement
                                                                                                                                       
if __name__ == "__main__":
  app.run(debug=True)

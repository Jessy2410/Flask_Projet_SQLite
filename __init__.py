from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

DATABASE = 'database2.db'  # Nom de la base de données

# Fonction pour vérifier si un utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)', (titre, auteur, genre))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))

    return render_template('formulaire_livre.html')

# Route pour afficher les livres
@app.route('/liste_livres')
def liste_livres():
    conn = sqlite3.connect(DATABASE)
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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT disponible FROM livres WHERE id = ?', (livre_id,))
        disponible = cursor.fetchone()

        if disponible and disponible[0] == 1:
            cursor.execute('INSERT INTO emprunts (utilisateur_id, livre_id, statut) VALUES (?, ?, ?)', 
                           (utilisateur_id, livre_id, 'En cours'))
            cursor.execute('UPDATE livres SET disponible = 0 WHERE id = ?', (livre_id,))
            conn.commit()

        conn.close()
        return redirect(url_for('liste_livres'))

    return redirect(url_for('authentification'))


# Route pour afficher les emprunts
@app.route('/emprunts')
def afficher_emprunts():
    conn = sqlite3.connect(DATABASE)
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
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE emprunts SET statut = 'Terminé', date_retour = CURRENT_TIMESTAMP WHERE id = ?
    ''', (emprunt_id,))
    cursor.execute('''
        UPDATE livres SET disponible = 1 WHERE id = (SELECT livre_id FROM emprunts WHERE id = ?)
    ''', (emprunt_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('afficher_emprunts'))

# Route pour rechercher un client par nom
@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_by_nom():
    message = ""
    results = []

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()

        if nom:
            try:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
                results = cursor.fetchall()
                if not results:
                    message = "Aucun client trouvé avec ce nom."
                conn.close()
            except Exception as e:
                message = f"Erreur lors de la recherche : {e}"
        else:
            message = "Veuillez entrer un nom."

    return render_template('searchUser.html', results=results, message=message)

# Route pour consulter tous les clients
@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# Route pour ajouter un client
@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)', (nom, prenom, "Adresse par défaut"))
        conn.commit()
        conn.close()
        return redirect('/consultation/')

    return render_template('formulaire.html')

if __name__ == "__main__":
    app.run(debug=True)

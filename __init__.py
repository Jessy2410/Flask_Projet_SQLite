l


from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour la gestion des sessions

DATABASE = 'database2.db'  # Nom de la base de données

# Fonction pour exécuter des requêtes SQL
def executer_requete(query, params=(), fetchone=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Vérifier si l'utilisateur est connecté
def est_authentifie():
    return "utilisateur" in session

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route d'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Vérifier si l'utilisateur existe en base de données
        user = executer_requete("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, password), fetchone=True)

        if user:
            session['utilisateur'] = user[1]  # Stocker le nom d'utilisateur en session
            session['utilisateur_id'] = user[0]  # Stocker l'ID utilisateur pour les emprunts
            return redirect(url_for('accueil.html'))  # Redirection vers la page après connexion
        else:
            error = "Email ou mot de passe incorrect."

    return render_template('authentification.html', error=error)

# Route après connexion
@app.route('/dashboard')
def dashboard():
    if est_authentifie():
        return f"<h1>Bienvenue, {session['utilisateur']}!</h1><a href='/logout'>Se déconnecter</a>"
    return redirect(url_for('authentification'))

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('utilisateur', None)
    session.pop('utilisateur_id', None)
    return redirect(url_for('authentification'))

# Route pour afficher les livres disponibles
@app.route('/liste_livres')
def liste_livres():
    livres = executer_requete('SELECT * FROM livres')
    return render_template('liste_livres.html', livres=livres)

# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    utilisateur_id = session.get('utilisateur_id')

    # Vérifier si le livre est disponible
    livre = executer_requete('SELECT disponible FROM livres WHERE id = ?', (livre_id,), fetchone=True)

    if livre and livre[0] == 1:
        executer_requete('INSERT INTO emprunts (utilisateur_id, livre_id, statut) VALUES (?, ?, ?)', 
                         (utilisateur_id, livre_id, 'En cours'))
        executer_requete('UPDATE livres SET disponible = 0 WHERE id = ?', (livre_id,))
    return redirect(url_for('liste_livres'))

# Route pour afficher les emprunts
@app.route('/emprunts')
def afficher_emprunts():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    emprunts = executer_requete('''
        SELECT e.id, l.titre, u.nom, e.date_emprunt, e.date_retour, e.statut
        FROM emprunts e
        JOIN livres l ON e.livre_id = l.id
        JOIN utilisateurs u ON e.utilisateur_id = u.id
    ''')
    return render_template('emprunts.html', emprunts=emprunts)

# Route pour retourner un livre
@app.route('/retourner_livre/<int:emprunt_id>', methods=['POST'])
def retourner_livre(emprunt_id):
    executer_requete('''
        UPDATE emprunts SET statut = 'Terminé', date_retour = CURRENT_TIMESTAMP WHERE id = ?
    ''', (emprunt_id,))
    executer_requete('''
        UPDATE livres SET disponible = 1 WHERE id = (SELECT livre_id FROM emprunts WHERE id = ?)
    ''', (emprunt_id,))
    return redirect(url_for('afficher_emprunts'))

# Route pour rechercher un client par nom
@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_by_nom():
    message = ""
    results = []

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()

        if nom:
            results = executer_requete('SELECT * FROM clients WHERE nom = ?', (nom,))
            if not results:
                message = "Aucun client trouvé avec ce nom."
        else:
            message = "Veuillez entrer un nom."

    return render_template('searchUser.html', results=results, message=message)

# Route pour consulter tous les clients
@app.route('/consultation/')
def ReadBDD():
    clients = executer_requete('SELECT * FROM clients')
    return render_template('read_data.html', data=clients)

# Route pour ajouter un client
@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']

        executer_requete('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)', 
                         (nom, prenom, "Adresse par défaut"))
        return redirect('/consultation/')

    return render_template('formulaire.html')

if __name__ == "__main__":
    app.run(debug=True)


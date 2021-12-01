from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("accueil.html")

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/problematiques')
def problematiques():
    liste_prob = [[1,'01-12-2021','Ca manque de verdure !','La ville est grise donc ajoutons de la verdure',1],
                [2,'01-12-2021','Avancement du projet','Je pense qu on est trop fort, on avance bien',2]
                ]
                 # querry de type SELECT * FROM problematiques
    # besoin de traiter les données avant de les renvoyers ?
    return render_template('problematiques.html',liste_prob = liste_prob,len = len(liste_prob)) 


@app.route('/problematique/<int:id_prob>')
def problematique(id_prob):
    pb = id_prob # avec une querry on va chercher donner de la problématique
    return render_template('problematique.html',pb = pb)

@app.route('/login')
def login():
    return render_template('login.html')
from flask import Flask, render_template, session,request,redirect
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        return redirect("/")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session["name"] = None
    return redirect('/')
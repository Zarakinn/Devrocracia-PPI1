from flask import Flask, render_template, session,request,redirect
from flask_session import Session
import fonctions_pratique

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

@app.route('/problematiques', methods=["GET","POST"])
def problematiques():
    liste_prob = fonctions_pratique.GetProblematiques()
    len_ = 0
    if liste_prob != None:
        len_  = len(liste_prob)
    if request.method == "POST":
        new_pb_title = request.form.get("new_pb_title")
        new_pb_desc = request.form.get("new_pb_desc")
        first_spb = request.form.get("first_spb")
        if new_pb_desc is not None and new_pb_title is not None:
            fonctions_pratique.Creation_Problemes(new_pb_title, new_pb_desc, first_spb, session["name"])
            print(new_pb_title,new_pb_desc,session["name"])
            return redirect('/problematiques')
    return render_template('problematiques.html',liste_prob = liste_prob,len = len_, showform=request.args.get("showform")


) 


@app.route('/problematique/<int:id_prob>')

@app.route('/problematique/<int:id_prob>')
def problematique(id_prob):

    spbs = fonctions_pratique.GetSousProblematiques(id_prob)
    if spbs == None or spbs == []:
        raise "il n'y pas de sous problématique associé, mauvaise initialisation"
    id_last_sous_prob = spbs[-1][0]
    props = fonctions_pratique.GetPropositions(id_last_sous_prob)
    return render_template('problematique.html',spbs = spbs,props=props)

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
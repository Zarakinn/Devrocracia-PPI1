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
        first_question = request.form.get("first_question")
        if new_pb_desc is not None and new_pb_title is not None:
            fonctions_pratique.Creation_Problemes(new_pb_title, new_pb_desc, first_question, session["mail"]) ## Attention, mettre mail pas name
            print(new_pb_title,new_pb_desc,session["mail"])
            return redirect('/problematiques')
    return render_template('problematiques.html',liste_prob = liste_prob,len = len_, showform=request.args.get("showform"))


@app.route('/problematique/<int:id_prob>')
def problematique(id_prob):

    questions = fonctions_pratique.GetQuestions(id_prob)
    if questions == None or questions == []:
        raise "il n'y pas de question associé, mauvaise initialisation"
    id_last_question = questions[-1][0]
    solutions = fonctions_pratique.GetSolutions(id_last_question)

    #Spécifique au vote
    vote_id = request.args.get("id")

    if vote_id != None and session["mail"]!= None:
        fonctions_pratique.Vote(vote_id, id_last_question, session["mail"])
        return redirect("/problematique/"+str(id_prob))

    #solutions pour lequel l'utilisateur a voté
    voted_solution = None

    if "mail" in session and session["mail"]!=None:
        voted_solution=fonctions_pratique.Get_Solution_Voter_by_User(id_last_question,session["mail"])
        print("Voted prop = " + str(voted_solution))
    return render_template('problematique.html',id_prob=id_prob,questions = questions,solutions=solutions,voted_solution=voted_solution,len_questions=len(questions))

@app.route('/problematique/ajout_prop/<int:id_prob>/<int:id_question>',methods=["GET","POST"])
def Ajoute_prop(id_prob,id_question):

    if request.method == "GET":
        return render_template("ajout_proposition.html",id_prob=id_prob,id_question=id_question)
    else :
        print("Ajoute d'une proposition")
        fonctions_pratique.Creation_Solution(id_question,request.form.get("titre"),request.form.get("texte"))
        return redirect("/problematique/"+str(id_prob))    

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["mail"] = request.form.get("mail")

        names = fonctions_pratique.GetNames(session["mail"])
        if not (names == None) :
            session["name"],session["fname"]=names 

        return redirect("/")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session["mail"] = None
    session["name"] = None
    session["fname"] = None
    return redirect('/')
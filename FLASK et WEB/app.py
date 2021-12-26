from logging import error
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
            print(new_pb_title,new_pb_desc, first_question, session["mail"])
            return redirect('/problematiques')
    return render_template('problematiques.html',liste_prob = liste_prob,len = len_, showform=request.args.get("showform"))


@app.route('/problematique/<int:id_prob>')
def problematique(id_prob):

    prob = fonctions_pratique.GetProblematique(id_prob)

    questions = fonctions_pratique.GetQuestions(id_prob)
    if questions == None or questions == []:
        raise "il n'y pas de question associé, mauvaise initialisation"

    choosen_solution = fonctions_pratique.Get_Choosen_Solutions(questions)

    last_question = questions[-1]
    possible_solutions = fonctions_pratique.GetSolutions(last_question[0])

    #Spécifique au vote
    vote_id = request.args.get("id")

    if vote_id != None and session["mail"]!= None:
        fonctions_pratique.Vote(vote_id, last_question[0], session["mail"])
        return redirect("/problematique/"+str(id_prob))

    #Différenciation de la page selon si l'on vote pour la prochaine question ou pour la prochaine solution
    etat = fonctions_pratique.Get_Voting_For_Solution_or_Question(id_prob)
    if etat == "vote solution":
        message_vote = "Votez pour une solution ou proposez-en une nouvelle."
    elif etat == "vote question":
        message_vote = "Votez pour la prochaine question ou proposez-en une nouvelle."


    most_voted_solution = fonctions_pratique.Get_Most_Voted_Solution(last_question[0])
    #Création d'une nouvelle branche à partir de la solution la plus votée
    if request.args.get("cloture") and most_voted_solution != None:        
        most_voted_solution_texte = most_voted_solution[2]
        if etat == "vote solution":
            fonctions_pratique.Etend_Branche("Choix de la question faisant suite à : " + most_voted_solution_texte, None, last_question[0], id_prob)
            return redirect("/problematique/"+str(id_prob))
        elif etat == "vote question":
            #Il n'y a pour l'instant pas de mémoire pour l'id de l'utilisateur qui propose la solution retenue d'ou le None ci-dessous
            fonctions_pratique.Etend_Branche(most_voted_solution_texte, None,last_question[0], id_prob) 
            return redirect("/problematique/"+str(id_prob))

    #solutions pour lequel l'utilisateur a voté
    voted_solution = None

    if "mail" in session and session["mail"]!=None:
        voted_solution=fonctions_pratique.Get_Solution_Voter_by_User(last_question[0],session["mail"])
        print("Voted prop = " + str(voted_solution))

    messages = fonctions_pratique.Get_Messages(last_question[0])

    return render_template(
        'problematique.html',
        prob=prob,
        last_question=last_question,
        questions = questions,
        choosen_solution=choosen_solution,
        len_question=len(questions),
        possible_solutions=possible_solutions,
        voted_solution=voted_solution,
        message_vote=message_vote,
        messages=messages
        )




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

        email, password = request.form.get("mail"),request.form.get("password")
        if fonctions_pratique.ValidLogin(email,password):
            session["mail"] = request.form.get("mail")

            names = fonctions_pratique.GetNames(session["mail"])
            if not (names == None) :
                session["name"],session["fname"]=names 

            return redirect("/")
        else:
            return render_template('login.html',error_msg="Login invalide")
    return render_template('login.html')

@app.route('/inscription',methods=["POST"])
def inscription():
    if request.method != "POST":
        return render_template('login.html',error_msg="tente de s'inscrire avec un get")

    email,name,fname = request.form.get("mail"),request.form.get("name"),request.form.get("fname")

    if not fonctions_pratique.ValidEmail(email) or name =="" or name==None or fname=="" or fname=="":
        return render_template('login.html',error_msg="Données invalides")

    if fonctions_pratique.NotAlreadyRegister(email):
        fonctions_pratique.Register(email,name,fname)
        session["mail"] = email
        session["name"] = name
        session["fname"] = fname
        return redirect('/')
    else :
        return render_template('login.html',error_msg = "Déjà enregistré")


@app.route('/logout')
def logout():
    session["mail"] = None
    session["name"] = None
    session["fname"] = None
    return redirect('/')

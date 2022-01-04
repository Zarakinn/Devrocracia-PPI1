from logging import error
from sqlite3.dbapi2 import DatabaseError
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


@app.route('/problematique/<int:id_prob>',methods=["GET","POST"])
def problematique(id_prob):

    prob = fonctions_pratique.GetProblematique(id_prob)

    if prob == None or []:
        raise DatabaseError("La problématique n'existe pas")

    questions = fonctions_pratique.GetQuestions(id_prob)
    if questions == None or questions == []:
        raise "il n'y pas de question associé, mauvaise initialisation"
    last_question = questions[-1]


    if request.method == "POST":
        #ajout de message
        texte = request.form.get("message") 
        if texte != None:
            print("envoie le msg :" + texte)
            fonctions_pratique.EnvoieMessage(session["mail"],texte,last_question[0])
            return redirect("/problematique/"+str(id_prob))
        #Ajout de proposition
        new_prop_title = request.form.get("new_prop_title")
        new_prop_desc = request.form.get("new_prop_desc")
        if new_prop_title != None and new_prop_desc != None:
            id_question = last_question[0]
            fonctions_pratique.Creation_Solution(id_question,new_prop_title,new_prop_desc)
            return redirect("/problematique/"+str(id_prob))    

    possible_solutions = fonctions_pratique.GetSolutions(last_question[0])
    messages = fonctions_pratique.Get_Messages(last_question[0])
    all_choosen_solutions = fonctions_pratique.Get_Choosen_Solution(questions)

    choosen_questions = questions[0::2] #On retire toutes les "questions suivante" en gardant les éléments pairs
    choosen_solutions = all_choosen_solutions[0::2]


    every_solutions = fonctions_pratique.GetAllSolutions(choosen_questions)
    every_questions = fonctions_pratique.GetAllQuestions(choosen_questions)

    for i in range(len(choosen_questions)): #on veut que le premier element soit de la forme "q'x'", il s'agit d'un tuple donc on le reconstruit.
        choosen_questions[i] = ("q"+str(choosen_questions[i][0]),) + choosen_questions[i][1:] 
    for i in range(len(choosen_solutions)):
        choosen_solutions[i] = ("s"+str(choosen_solutions[i][0]),) + choosen_solutions[i][1:]
        
    print("------------ATTENTION variables interessantes--------------")
    print("questions")
    print(questions)
    print("choosen_questions")
    print(choosen_questions)
    print("every_questions")
    print(every_questions)
    print("every_solution")
    print(every_solutions)
    print("choosen_solutions")
    print(choosen_solutions)
    print("Possible solution")
    print(possible_solutions)
    

    #Spécifique au vote
    vote_id = request.args.get("id")
    if vote_id != None and session["mail"]!= None:
        fonctions_pratique.Vote(vote_id, last_question[0], session["mail"])
        return redirect("/problematique/"+str(id_prob))

    #Différenciation de la page selon si l'on vote pour la prochaine question ou pour la prochaine solution
    etat = fonctions_pratique.Get_Voting_For_Solution_or_Question(id_prob)
    if all_choosen_solutions != [] and all_choosen_solutions[-1][2] == "Backtracking":
        message_vote = "Votez pour la solution à laquelle retourner. (backtracking)"
        etat="backtracking"
    elif etat == "vote solution":
        message_vote = "Votez pour une solution ou proposez-en une nouvelle."
    elif etat == "vote question":
        message_vote = "Votez pour la prochaine question ou proposez-en une nouvelle."

    most_voted_solution = fonctions_pratique.Get_Most_Voted_Solution(last_question[0])
        #Création d'une nouvelle branche à partir de la solution la plus votée
    if request.args.get("cloture") and most_voted_solution != None:        
        most_voted_solution_texte = most_voted_solution[2]
        print("MOST VOTED SOLUTION DESCRIPTION:" + most_voted_solution_texte)
        redirect_to = "/problematique/"+str(id_prob)
        if all_choosen_solutions != [] and all_choosen_solutions[-1][2] == "Backtracking":
            backtrack_to = most_voted_solution[3][9:] #Ce parametre a été inscrit dans la description de la solution votée
            i=0 #On ne connait pas le nombre de chiffre dans la donnée donc on prend toute la chaîne de chiffre
            while backtrack_to[i+1] != ")":
                i+=1
            backtrack_to = backtrack_to[:i+1]
            print("backtracking to :"+str(backtrack_to))
            fonctions_pratique.do_backtracking(backtrack_to, id_prob)
            return redirect(redirect_to)
        elif most_voted_solution_texte == "Backtracking":
            fonctions_pratique.init_backtracking_vote(id_prob, last_question[0], all_choosen_solutions)
            return redirect(redirect_to)
        elif etat == "vote solution":
            fonctions_pratique.Etend_Branche("Question suivante", None, last_question[0], id_prob)
            print("branche etendue en vote solution")
            return redirect(redirect_to)
        elif etat == "vote question":
            print("branche etendue en vote question")
            #Il n'y a pour l'instant pas de mémoire pour l'id de l'utilisateur qui propose la solution retenue d'ou le None ci-dessous
            fonctions_pratique.Etend_Branche(most_voted_solution_texte, None,last_question[0], id_prob) 
            return redirect(redirect_to)

    #solutions pour lequel l'utilisateur a voté
    voted_solution = None

    if "mail" in session and session["mail"]!=None:
        voted_solution=fonctions_pratique.Get_Solution_Voter_by_User(last_question[0],session["mail"])
        print("Voted prop = " + str(voted_solution))

    incr_etat = 0
    if etat == "vote solution" or etat == "backtracking": # si on est dans une phase de vote solution, la derniere question choisi n'a pas encore de réponse choisi associé
        incr_etat = 1
    
    print(etat)
    print("incr_etat = " + str(incr_etat))

    return render_template( #il faut homogeniser tous les s en fin de variables
        'problematique.html',
        prob = prob,
        last_question = last_question,
        questions = questions,
        all_choosen_solutions = all_choosen_solutions,
        every_solution = every_solutions,
        every_question = every_questions,
        choosen_question = choosen_questions,
        choosen_solution = choosen_solutions,
        len_question = len(choosen_questions),
        possible_solutions = possible_solutions,
        voted_solution = voted_solution,
        message_vote = message_vote,
        messages = messages,
        incr_etat = incr_etat,
        etat=etat,
        showform=request.args.get("showform")
        )

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
        return render_template('login.html',error_msg="tente de s'inscrire avec une méthode Get")

    email,name,fname,password = request.form.get("mail"),request.form.get("name"),request.form.get("fname"),request.form.get("password")

    if not fonctions_pratique.ValidEmail(email) or name =="" or name==None or fname=="" or fname=="" or password=="":
        return render_template('login.html',error_msg="Données invalides")

    if fonctions_pratique.NotAlreadyRegister(email):
        fonctions_pratique.Register(email,name,fname,password)
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

@app.errorhandler(404)
def error404(error):
    return render_template("error.html",error_msg="Erreur : " + str(error))

@app.errorhandler(DatabaseError)
def error_db(error):
    return render_template("error.html",error_msg="Erreur sur la base de donnée: " + str(error))

@app.route("/changekey/<string:key>")
def changekey(key):
    fonctions_pratique.ChangeKey(key)
    return redirect("/")
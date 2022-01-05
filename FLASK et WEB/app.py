from logging import error
from sqlite3.dbapi2 import DatabaseError
from flask import Flask, render_template, session,request,redirect
from flask_session import Session
import fonctions_pratiques

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
    liste_prob = fonctions_pratiques.Get_Problematiques()
    len_ = 0
    if liste_prob != None:
        len_  = len(liste_prob)
    if request.method == "POST":
        new_pb_title = request.form.get("new_pb_title")
        new_pb_desc = request.form.get("new_pb_desc")
        first_question = request.form.get("first_question")
        if new_pb_desc is not None and new_pb_title is not None:
            fonctions_pratiques.Creation_Problemes(new_pb_title, new_pb_desc, first_question, session["mail"]) ## Attention, mettre mail pas name
            print(new_pb_title,new_pb_desc, first_question, session["mail"])
            return redirect('/problematique/'+str(len_+1))
    return render_template('problematiques.html',liste_prob = liste_prob,len = len_, showform=request.args.get("showform"))


@app.route('/problematique/<int:id_prob>',methods=["GET","POST"])
def problematique(id_prob):
    prob = fonctions_pratiques.Get_Problematique(id_prob)

    if prob == None or []:
        raise DatabaseError("La problématique n'existe pas")

    questions = fonctions_pratiques.Get_Questions(id_prob)
    if questions == None or questions == []:
        raise "il n'y pas de question associé, mauvaise initialisation"
    last_question = questions[-1]


    if request.method == "POST":
        #ajout de message
        texte = request.form.get("message") 
        if texte != None:
            print("envoie le msg :" + texte)
            fonctions_pratiques.Send_Message_In_Chat(session["mail"],texte,last_question[0])
            return redirect("/problematique/"+str(id_prob))
        #Ajout de proposition
        new_prop_title = request.form.get("new_prop_title")
        new_prop_desc = request.form.get("new_prop_desc")
        #une proposition au titre "La problématique est résolue serait un moyen frauduleux d'archiver la problématique"
        if new_prop_title != None and new_prop_desc != None and not new_prop_title == "La problématique est résolue":
            id_question = last_question[0]
            fonctions_pratiques.Creation_Solution(id_question,new_prop_title,new_prop_desc)
            return redirect("/problematique/"+str(id_prob))    

    possible_solutions = fonctions_pratiques.Get_Solutions(last_question[0])
    messages = fonctions_pratiques.Get_Messages(last_question[0])
    all_chosen_solutions = fonctions_pratiques.Get_Chosen_Solution(questions)

    chosen_questions = questions[0::2] #On retire toutes les "questions suivante" en gardant les éléments pairs
    chosen_solutions = all_chosen_solutions[0::2]


    every_solutions = fonctions_pratiques.Get_All_Solutions(chosen_questions)
    every_questions = fonctions_pratiques.Get_All_Questions(chosen_questions)

    for i in range(len(chosen_questions)): #on veut que le premier element soit de la forme "q'x'", il s'agit d'un tuple donc on le reconstruit.
        chosen_questions[i] = ("q"+str(chosen_questions[i][0]),) + chosen_questions[i][1:] 
    for i in range(len(chosen_solutions)):
        chosen_solutions[i] = ("s"+str(chosen_solutions[i][0]),) + chosen_solutions[i][1:]
        
    print("------------ATTENTION variables interessantes--------------")
    print("questions")
    print(questions)
    print("chosen_questions")
    print(chosen_questions)
    print("every_questions")
    print(every_questions)
    print("every_solution")
    print(every_solutions)
    print("chosen_solutions")
    print(chosen_solutions)
    print("Possible solution")
    print(possible_solutions)
    
    #Spécifique au vote
    vote_id = request.args.get("id")
    if vote_id != None and session["mail"]!= None:
        fonctions_pratiques.Vote(vote_id, last_question[0], session["mail"])
        return redirect("/problematique/"+str(id_prob))

    #Différenciation de la page selon si l'on vote pour la prochaine question ou pour la prochaine solution
    etat = fonctions_pratiques.Get_Voting_For_Solution_or_Question(id_prob)
    if all_chosen_solutions != [] and all_chosen_solutions[-1][2] == "Backtracking":
        message_vote = "Votez pour la solution la plus lointaine à invalider."
        etat="backtracking"
    elif etat == "vote solution":
        message_vote = "Votez pour une solution ou proposez-en une nouvelle."
    elif etat == "vote question":
        message_vote = "Votez pour la prochaine question ou proposez-en une nouvelle."

    most_voted_solution = fonctions_pratiques.Get_Most_Voted_Solution(last_question[0])
    #Création d'une nouvelle branche à partir de la solution la plus votée
    if request.args.get("cloture") and most_voted_solution != None:        
        most_voted_solution_texte = most_voted_solution[2]
        redirect_to = "/problematique/"+str(id_prob) #on retire le paramètre indiquant qu'il faut cloturer
        if all_chosen_solutions != [] and all_chosen_solutions[-1][2] == "Backtracking": #si l'état était déjà en backtracking
            backtrack_to = most_voted_solution[3][9:] #L'id de la question à laquelle revenir a été inscrit dans la description de la solution votée: "(hauteur X) description"
            i=0 #On ne connait pas le nombre de chiffre, donc on prend tous les chiffes avant la parenthèse fermante à l'aide de la boucle ci-dessous
            while backtrack_to[i+1] != ")":
                i+=1
            backtrack_to = backtrack_to[:i+1]
            print("backtracking to :"+str(backtrack_to))
            fonctions_pratiques.Do_Backtracking(backtrack_to, id_prob)
            return redirect(redirect_to)
        elif most_voted_solution_texte == "Backtracking": #si les utilisateurs ont voté pour démarrer le backtracking
            fonctions_pratiques.Init_Backtracking_Vote(id_prob, last_question[0], chosen_solutions) #OS DE CONTENTION RIGHT THERE
            return redirect(redirect_to)
        elif etat == "vote solution":
            fonctions_pratiques.Etend_Branche("Question suivante", None, last_question[0], id_prob)
            print("branche etendue en vote solution")
            return redirect(redirect_to)
        elif etat == "vote question":
            print("branche etendue en vote question")
            #Il n'y a pour l'instant pas de mémoire pour l'id de l'utilisateur qui propose la solution retenue d'ou le None ci-dessous
            fonctions_pratiques.Etend_Branche(most_voted_solution_texte, None,last_question[0], id_prob) 
            return redirect(redirect_to)

    #solutions pour lequel l'utilisateur a voté
    voted_solution = None

    if "mail" in session and session["mail"]!=None:
        voted_solution=fonctions_pratiques.Get_Solution_Voter_by_User(last_question[0],session["mail"])
        print("Voted prop = " + str(voted_solution))

    incr_etat = 0
    if etat == "vote solution" or etat == "backtracking": # si on est dans une phase de vote solution, la derniere question choisi n'a pas encore de réponse choisi associé
        incr_etat = 1
    
    print(etat)
    print("incr_etat = " + str(incr_etat))

    return render_template(
        'problematique.html',
        prob = prob,
        last_question = last_question,
        questions = questions,
        all_chosen_solutions = all_chosen_solutions,
        every_solutions = every_solutions,
        every_questions = every_questions,
        chosen_questions = chosen_questions,
        chosen_solutions = chosen_solutions,
        len_question = len(chosen_questions),
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
        if fonctions_pratiques.Valid_Login(email,password):
            session["mail"] = request.form.get("mail")

            names = fonctions_pratiques.Get_Names(session["mail"])
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

    if not fonctions_pratiques.Valid_Email(email) or name =="" or name==None or fname=="" or fname=="" or password=="":
        return render_template('login.html',error_msg="Données invalides")

    if fonctions_pratiques.Not_Already_Registered(email):
        fonctions_pratiques.Register(email,name,fname,password)
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

#@app.route("/changekey/<string:key>")
#def changekey(key):
#    fonctions_pratiques.ChangeKey(key)
#    return redirect("/")
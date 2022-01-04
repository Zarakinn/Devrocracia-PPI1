# -*- coding: utf-8 -*-
from logging import fatal, raiseExceptions
from re import U
import sqlite3
from typing import List

database = "data/database.db"


def basic_query(sql, param_sql, error_msg):
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        cursor.execute(sql,param_sql)
        query = cursor.fetchall()

        cursor.close()
        connexion.close()
        return query
    except sqlite3.Error as error:
        print(error_msg, error)

def Creation_Problemes(titre,description,question_titre,utilisateur) -> None :
    """
    Cette fonction a pour but de créer un nouveau problème, pour cela on calcule la date, un nouvel id unique et on créé une ligne dans les schéma problématique et question
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT CURRENT_TIMESTAMP")
        date =cursor.fetchone()
        date=date[0]

        cursor.execute("SELECT max(id) FROM pb ")
        new_pb_id=cursor.fetchone()
        
        if new_pb_id==(None,): # Si il n'y a pas encore de problème, max(id) renvoie None : on catch l'erreur et on résoud le problème
            new_pb_id=[0]
        new_pb_id=new_pb_id[0]+1

        sql_pb = "INSERT INTO pb (id,DateCreation,titre,texte,utilisateur_email) VALUES (?,?,?,?,?)"
        donnees_pb=[(new_pb_id,date,titre,description,utilisateur)] #attention, utilisateur est text et non id
        cursor.executemany(sql_pb, donnees_pb)


        cursor.execute("SELECT max(id) FROM question ")
        new_question_id=cursor.fetchone()
        if new_question_id==(None,): # Si il n'y a pas encore de question, max(id) renvoie None : on catch l'erreur et on résoud le problème
            new_question_id=[0]
        new_question_id=new_question_id[0]+1

        sql_question = "INSERT INTO question (id,DateCreation,titre ,auteur_email, question_parent_id, pb_parent_id) VALUES (?,?,?,?,?,?)"
        donnees_spb=[(new_question_id,date,question_titre,utilisateur,new_question_id,new_pb_id)]
        cursor.executemany(sql_question, donnees_spb)

        connexion.commit()
        print("Enregistrements insérés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)
    

def Creation_Solution(question_id,titre,description) -> None :
    """
    Pour une question donnée identifié par question_id, on ajoute une proposition à partir des paramètres données et d'autres que l'on calcul tel que la date, un id ...
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM solutions ")
        new_id=cursor.fetchone()
        if new_id==(None,): # Si il n'y a pas encore de solution, max(id) renvoie None : on catch l'erreur et on résoud le problème
            new_id = [0]
        new_id = new_id[0] + 1

        donnees=[(new_id,question_id,titre,description,0)]
        sql = "INSERT INTO solutions (id,question_id,titre,texte,nb_vote) VALUES (?, ?, ?, ?,?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        
        print("Enregistrements insérés avec succès dans la table solutions")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table solutions", error)

def Get_Solution_Voter_by_User(question_id, user) -> int:
    """
    On essaie de trouver si l'utilisateur passer en paramètre a déjà voté pour le choix identifié par question_id. Si c'est le cas, on renvoi son choixi sinon on renvoie None
    """
    query = "SELECT solution_id FROM votes WHERE utilisateur_email = ? AND question_id =?"
    param = (user,question_id)
    error = "Erreur lors du vote"
    solution = basic_query(query, param, error)

    if solution != None and solution != []: 
        solution = int(solution[0][0]) #On renvoie uniquement l'id de la solution pour laquelle il a voté
        
    return solution



def Get_Most_Voted_Solution(question_id) -> int :
    """
    Cherche toutes les solutions associées à la question, retourne celle qui à le plus de vote
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        #print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(question_id,))
        nb_vote_max=cursor.fetchone()
        nb_vote_max=nb_vote_max[0]

        # Ici, grâce à la structure qu'on a choisi, il y a toujours la solution "backtracking" ce qui assure qu'il n'y a pas de problème

        #print("Le maximum de vote est " + str(nb_vote_max))
        cursor.execute("SELECT * FROM solutions WHERE question_id=? AND nb_vote=? ", (question_id,nb_vote_max))
        best_solution=cursor.fetchone() 
        
        # Si deux solutions on le même nombre de votes, on en choisit un arbitrairement 

        cursor.close()
        connexion.close()
        #print("Connexion SQLite est fermée")
        return best_solution
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de la solution la plus voté", error)

def Get_Choosen_Solution(questions : list) -> list:
    """
    On souhaite récupérer la liste de toutes les solutions qui ont été choisit dans cette problématique lors des choix précédents
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        #print("Connexion réussie à SQLite")
        choosen_solutions = []

        for q in questions:
            cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(q[0],))
            nb_vote_max=cursor.fetchone()
            nb_vote_max=nb_vote_max[0]

            # Ici, grâce à la structure qu'on a choisi, il y a toujours la solution "backtracking" ce qui assure qu'il n'y a pas de problème

            #print("Le maximum de vote est " + str(nb_vote_max))
            cursor.execute("SELECT * FROM solutions WHERE question_id=? AND nb_vote=? ", (q[0],nb_vote_max))
            best_solution=cursor.fetchone()

            # Si deux solutions on le même nombre de votes, on en choisit un arbitrairement 

            choosen_solutions.append(best_solution)
    
        cursor.close()
        connexion.close()
        #print("Connexion SQLite est fermée")
        return choosen_solutions[:-1]
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des solutions choisi", error)


def GetAllSolutions(choosen_question:list):
    """
    On souhaite récupérer la liste de toutes les solutions qui ont été proposé dans cette problématique, pour cela on part de la liste des questions qui ont été posé
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        all_solutions=[] #liste de liste de solution

        for q in choosen_question:
            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(q[0],))
            solutions = cursor.fetchall() #liste de solutions proposé pour la question q

            nb_total_vote=0
            for s in solutions:
                nb_total_vote+=s[4]
            if nb_total_vote==0:
                nb_total_vote=1
            for i,s in enumerate(solutions):
                s=list(s)
                s.append(int((s[4]/nb_total_vote)*10000)/100)
                s=tuple(s)
                solutions[i]=s

            all_solutions.append(solutions)

        print("Récupération de toutes les solutions réussi, il y en a = " + str(len(all_solutions)))
        cursor.close()
        connexion.close()
        print(all_solutions)
        return all_solutions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de toutes les solutions :",error)

def GetAllQuestions(choosen_question : list):
    """
    On souhaite récupérer les questions qui ont été choisi par les utilisateurs, grâce à notre structure  on sait que le parent à le string de ces fonctions 
    a pour titre la variable NextQuestionString
    """
    try :
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        assert len(choosen_question) > 0, "aucune question choisi, ne peux pas renvoyer GetAllQuestions"

        all_questions =[[choosen_question[0]]]

        for i in range(1,len(choosen_question)):
            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(choosen_question[i][4],)) # question avec le meme choix parent
            questions = cursor.fetchall()

            nb_total_vote=0
            for q in questions:
                nb_total_vote+=q[4]
            if nb_total_vote==0:
                nb_total_vote=1

            for i,q in enumerate(questions):
                q=list(q)
                q.append(int((q[4]/nb_total_vote)*10000)/100)
                q=tuple(q)
                questions[i]=q

            all_questions.append(questions)
        
        cursor.close()
        connexion.close()
        print("Récupération de toutes les questions effectués")
        return all_questions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de toutes les questions :",error)

def Get_Voting_For_Solution_or_Question(pb_parent_id) -> int :
    """
    On souhaite savoir si on est dans un choix de question ou un choix de solution. On utilise à notre avantage la structure de nos données :
    si le nombre de question d'un problème est impair on vote pour une solution, sinon pour une question.
    """
    query = "SELECT count(id) FROM question WHERE pb_parent_id = ?"
    param = (pb_parent_id,)
    error = "Erreur de la récupération de l'état du vote"
    parité = basic_query(query, param, error)[0][0] % 2
    # count(id) ne peux pas être nul : quand on créé une problématique on demande une première question
    if parité == 1:
        return "vote solution"
    else:
        return "vote question"


def Etend_Branche(titre,utilisateur,question_parent, pb_parent_id) -> None :
    """
    Fonction appellé lors de la clotûre d'un vote, elle doit:
    -> récupérer le choix ayant eu le plus de vote
    -> créer une question en fonction de ce choix
    -> ajouter comme solution le backtracking 
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM solutions")
        new_id_sol=cursor.fetchone()
        if new_id_sol == (None,):
            new_id_sol = [0]
        new_id_sol = new_id_sol[0]+1

        cursor.execute("SELECT max(id) FROM question")
        new_id_question=cursor.fetchone()
        if new_id_question==(None,):
            new_id_question = [0]
        new_id_question = new_id_question[0]+1

        cursor.execute("SELECT date('now')")
        date=cursor.fetchone()[0]

        donnees=[(new_id_question,date,titre,utilisateur,question_parent, pb_parent_id)]
        sql = "INSERT INTO question (id,DateCreation,titre,auteur_email,question_parent_id, pb_parent_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)

        donnees=[(new_id_sol, new_id_question, "Backtracking", "Vote pour le retour en arrière.", 0)]
        sql = "INSERT INTO solutions (id, question_id, titre, texte, nb_vote) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)
        
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table question et solutions")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lorsque la branche a été étendu", error)


def init_backtracking_vote(pb_parent_id, question_parent_id, solution_list) -> None :
    """
    Ajoute "backtracking" en tant que nouvelle question et tous les points de retour possibles en solutions
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM solutions")
        new_id_sol=cursor.fetchone()
        if new_id_sol == (None,):
            new_id_sol = [0]
        new_id_sol = new_id_sol[0]+1

        cursor.execute("SELECT max(id) FROM question")
        new_id_question=cursor.fetchone()
        if new_id_question== (None,):
            new_id_question = [0]
        new_id_question = new_id_question[0]+1

        cursor.execute("SELECT date('now')")
        date=cursor.fetchone()[0]

        donnees=[(new_id_question, date, "Où revenir ?", None, question_parent_id, pb_parent_id)]
        sql = "INSERT INTO question (id,DateCreation,titre,auteur_email,question_parent_id, pb_parent_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)

        for i,question in enumerate(solution_list[:-1]):
            #question[1]: question à laquelle la solution répond initialement, nécessaire pour savoir où backtracker
            donnees=[(new_id_sol+i, new_id_question, question[2], "(Hauteur "+str(question[1])+") "+question[3], 0)]
            sql = "INSERT INTO solutions (id, question_id, titre, texte, nb_vote) VALUES (?, ?, ?, ?, ?)"
            cursor.executemany(sql, donnees)
                
        connexion.commit()
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("init_backtracking_vote erreur", error)



def do_backtracking(backtrack_to_id, pb_parent_id) -> None :
    """
    Coupe toutes les questions postérieures à celle où on backtrack et réimplente la question en question
    """ 
    try:
        print("___DO BACKTRACKING___")
        print(backtrack_to_id, pb_parent_id)
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM question")
        new_id_question=cursor.fetchone()
        if new_id_question==None:
            new_id_question=[0]
        new_id_question=new_id_question[0]+1

        #Coupage
        cursor.execute("UPDATE question SET branche_morte = 1 WHERE pb_parent_id = ? AND id > ?", (pb_parent_id, backtrack_to_id))
        cursor.execute("DELETE FROM question WHERE branche_morte = 1") #Pour l'instant pas de mémoire du backtracking

        #Reimplementation
        cursor.execute("SELECT DateCreation, titre, auteur_email, question_parent_id FROM question where id = ?",(backtrack_to_id,))
        question_to_restore=cursor.fetchone()
        DateCreation, titre, auteur_email, question_parent_id = question_to_restore
        donnees=[(new_id_question,DateCreation,titre,auteur_email,question_parent_id,pb_parent_id)]
        sql = "INSERT INTO question (id,DateCreation,titre,auteur_email,question_parent_id, pb_parent_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)        

        connexion.commit()
        print("do_backtracking succès")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("do_backtracking echec", error)

def Vote(solution_id, id_question, utilisateur) -> None :
    """
    Enregistre le vote d'un utilisateur, vérifie qu'elle n'a pas déjà voté. Si c'est le cas, on supprime son ancien vote.
    """
    try:
    #removing previous vote
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        #decrease vote count if user already voted in the same spb
        cursor.execute(" UPDATE solutions SET nb_vote = (nb_vote - 1) WHERE id = \
            (SELECT solution_id FROM votes WHERE utilisateur_email = ? AND question_id = ?)",(utilisateur,id_question))

        #remove the vote occurence on the table vote
        print("remove occurence ...")
        cursor.execute("DELETE FROM votes WHERE utilisateur_email = ? AND question_id = ?",(utilisateur,id_question))

        #adding new one
        print("add vote to tables votes ...")
        cursor.execute("INSERT INTO votes (utilisateur_email, solution_id, question_id) VALUES (?,?,?)",(utilisateur,solution_id,id_question))

        print("Update nombre de votes ...")
        cursor.execute("UPDATE solutions SET nb_vote = (nb_vote + 1) WHERE id = ?", (solution_id,))
        connexion.commit()
        
        print("Vote comptabilisé avec succès !")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return
    except sqlite3.Error as error:
        print("Erreur lors du vote :", error)
        return

def break_text(text, char_per_line):
    broke_text = ""
    while len(text) > char_per_line:
        broke_text += text[:char_per_line]
        broke_text += "<br>"
        text = text[char_per_line+1:]
        return broke_text

def EnvoieMessage(utilisateur : str,texte : str,question_id : int) -> None :
    """
    Envoie un message :
    Créé une ligne dans le schéma message et l’associe à la question
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        print("Insertion de message ...")
        cursor.execute("SELECT max(id) FROM msg ")
        new_id=cursor.fetchone()
        if new_id == (None,):
            new_id = [0]
        new_id=new_id[0]+1

        cursor.execute("SELECT CURRENT_TIMESTAMP")
        date =cursor.fetchone()
        date=date[0]

        #text = break_text(text, 5)

        sql = "INSERT INTO msg (id,texte,utilisateur_email,question_id,date) VALUES (?, ?, ?, ?,?)"
        donnes=[(new_id,texte,utilisateur,question_id,date)]
        cursor.executemany(sql,donnes )
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table message")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table message/question", error)

def GetNames(utilisateur):
    """
    On récupère le nom et prénom d'un utilisateur à partir de son email
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT nom,prenom FROM utilisateurs WHERE email = ? ",(utilisateur,))
        names = cursor.fetchone()

        # Cette fonction ne peux être appellé que si l'utilisateur est a réussi à se connecter, donc si il est inscrit et qu'il y a bien une ligne dans le schéma user lui correspondant

        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        print("Names = " + str(names))
        return names
    except sqlite3.Error as error:
        print("Erreur lors de la récupération du nom", error)

## Récupération de données à afficher

def GetProblematiques() -> list:
    """
    Récupère la liste de toutes les problématiques
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        sql_request = "SELECT * FROM pb"
        cursor.execute(sql_request )
        pbs = cursor.fetchall()
        print("Récupération des problématiques réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return pbs
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des problématiques", error)


def GetProblematique(id_prob : int) -> list:
    """
    Récupère les informations  sur une problématique grâce à son id
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT * FROM pb WHERE id=?",(id_prob,))
        pb = cursor.fetchone()

        if pb == None:
            print("Erreur, la problématique n'existe pas")

        print("Récupération de la problématique")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return pb
    except sqlite3.Error as error:
        print("Erreur lors de la récupération d'une problématique", error)

def GetQuestions(id_prob : int) -> list:
    """
    Récupère les questions successives associées à une problématique
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        liste_questions = []

        cursor.execute("SELECT * FROM question WHERE pb_parent_id = ? AND id=question_parent_id ",(id_prob,))
        question = cursor.fetchone()

        # Grâce à l'initialisation, il existe forcément une première question.

        liste_questions.append(question)

        
        while True:
            cursor.execute("SELECT * FROM question WHERE question_parent_id = ? AND NOT id=question_parent_id", (liste_questions[-1][0],)) 
            # on cherche si la derniere sous proposition a un enfant
            question = cursor.fetchone()
            if question == None:
                break
            else :
                 liste_questions.append(question)


        print("Récupération des questions réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return liste_questions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des questions", error)

def GetSolutions(id_question : int) -> list:
    """
    On récupère toutes les solutions associé à une question
    """
    query = "SELECT * FROM solutions WHERE question_id = ?"
    param = (id_question,)
    error = "SELECT * FROM utilisateurs WHERE email=?"
    liste_solution = basic_query(query, param, error)
    return liste_solution

def ValidEmail(email :str) -> bool:
    """
    On vérifie que le format proposé en email vérifie quelque condition de base:
    il est de la forme xxx@xxx.fr|eu|com|net
    """
    if email == "" or email == None:
        return False

    email_decomposé = email.split("@")
    if len(email_decomposé) != 2:
        return False
    if email_decomposé[0]=="" or email_decomposé[1]=="":
        return False

    print(email_decomposé)
    if not (email_decomposé[1].endswith(".com") or email_decomposé[1].endswith(".fr") or email_decomposé[1].endswith(".eu") or email_decomposé[1].endswith(".net")):
        return False
    return True

def NotAlreadyRegister(email : str) -> bool:
    """
    Vérifie que l'email passé en paramètre n'est pas déjà dans la base de donnée,
    c'est à dire que personne ne s'est inscrit avec le mail email
    """
    query = "SELECT * FROM utilisateurs WHERE email=?"
    param = (email,)
    error = "Erreur lors de la vérification que le nouveau mail n'est pas déjà dans la BD"
    utilisateur = basic_query(query, param, error)
    b = utilisateur == []
    print("Vérification réussi ="+str(b))
    return b

def Register(email : str, name :str, fname: str, password : str):
    """
    Enregistre un nouvelle utilisateur grâce aux paramètre donnée
    Cette fonction doit être utilisé après avoir appellé la fonction ValidEmail pour vérifié que cet email n'est pas déjà dans la base de donnée
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("INSERT INTO utilisateurs VALUES (?,?,?,?)",(email,name,fname,cryptageXOR(password)))

        print("Nouvel utilisateurs insérer")
        connexion.commit()
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return 
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion du nouvel utilisateurs", error)
    

def ValidLogin(email : str, password : str) -> bool:
    """
    Vérifie que le login  donnée existe dans la base de donnée et que le mot de passe correspond. 
    """
    query = "SELECT * FROM utilisateurs WHERE email=?"
    param = (email,)
    error = "Erreur lors de la vérification du login"
    user = basic_query(query, param, error)
    if user == None or user==[]:
        return False
    print(user)
    if decryptageXOR(user[0][3])==password:
        return True
    return False

def Get_Messages(id_question : int ) -> List:
    """
    Récupère tous les messages associé à une question
    """
    print("L'id de la question est " + str(id_question))
    query = "SELECT * FROM msg WHERE question_id=?"
    param = (id_question,)
    error = "Erreur lors de la récupération des messages"
    messages = basic_query(query, param, error)
    print("Il y a "+str(len(messages))+" messages.")
    return messages


def GetKey():
    with open("key.txt") as file :
        temp = file.read()
        if len(temp) > 5:
            return temp
        else :
            raiseExceptions("Impossible de lire la clef")

key = GetKey()
##print("key = " + key)
def ChangeKey(new_key): 
    try :

        for carac in new_key:
            if not carac in "abcedfghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
                raiseExceptions("Clef non valide, accepte seulement lettre et chiffre")
                return

        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()


        cursor.execute("SELECT * FROM utilisateurs")
        users = cursor.fetchall()

        for u in users:
            plain_mdp = decryptageXOR(u[3])
            new_mdp = cryptageXOR(plain_mdp,new_key)
            cursor.execute("UPDATE utilisateurs SET mdp = ? WHERE email = ?", (new_mdp,u[0]))

        connexion.commit()
        cursor.close()
        connexion.close()

        with open("key.txt",'w') as file :
            file.write(new_key)
            return
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion du nouvel utilisateurs", error)
    

"""

Fonctions XOR issue d'un projet de première année de CPGE par CHANEL Valentin en collaboration avec FUCHS Léon aux lycée Claude Louis Berthollet

"""

def cryptageXOR(plain_text : str, key = key) -> str:
    """
    Encrypte un texte grâce à la méthode XOR
    """
    encrypted_text= ""
    key_itr = 0
    for i in range(len(plain_text)):
        lettre_encrpt = ord(plain_text[i]) ^ ord(key[key_itr])
        encrypted_text += hex(lettre_encrpt)[2:].zfill(2) # enlève 0x et ajoute des zeros devant si nécessaire pour avoir deux chiffre hexa <-> 1 nombre
        key_itr +=1
        if key_itr>=len(key):
            key_itr=0
    return encrypted_text

def decryptageXOR(encrypted_text : str, key = key) -> str:
    """
    Decrypte un texte grâce à la méthode XOR
    """
    if encrypted_text=="" or encrypted_text == None:
        return ""

    text_unicode = ""
    for i in range(0, len(encrypted_text), 2):     
        text_unicode += bytes.fromhex(encrypted_text[i:i+2]).decode('utf-8')
    plain_text =""
    clef_itr = 0 
    for i in range(len(text_unicode)):   
        lettre_dcrpt = ord(text_unicode[i]) ^ ord(key[clef_itr])    
        plain_text += chr(lettre_dcrpt)
        clef_itr += 1      
        if clef_itr >= len(key):         
            clef_itr = 0
    return plain_text
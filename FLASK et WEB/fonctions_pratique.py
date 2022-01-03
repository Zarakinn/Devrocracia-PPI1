# -*- coding: utf-8 -*-
from logging import fatal
from re import U
import sqlite3
from typing import List
## from werkzeug.datastructures import V        c'est quoi ca ????????

database = "data/database.db"


def Creation_Problemes(titre,description,question_titre,utilisateur) -> None :
    """calcule de la date, d’un id unique et création d’une ligne dans le schéma problématique et question associée"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT date('now')")
        date =cursor.fetchone()
        date=date[0]

        cursor.execute("SELECT max(id) FROM pb ")
        new_pb_id=cursor.fetchone()
        print(new_pb_id)
        if new_pb_id==(None,):
            new_pb_id=[0]
        new_pb_id=new_pb_id[0]+1

        sql_pb = "INSERT INTO pb (id,DateCreation,titre,texte,utilisateur_email) VALUES (?,?,?,?,?)"
        donnees_pb=[(new_pb_id,date,titre,description,utilisateur)] #attention, utilisateur est text et non id
        cursor.executemany(sql_pb, donnees_pb)


        cursor.execute("SELECT max(id) FROM question ")
        new_question_id=cursor.fetchone()
        if new_question_id==(None,):
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
    """ajoute une solution pour une question"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM solutions ")
        new_id=cursor.fetchone()
        if new_id==(None,):
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
    try:
        #removing previous vote
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        cursor.execute("SELECT solution_id FROM votes WHERE utilisateur_email = ? AND question_id =?",(user,question_id))
        solution = cursor.fetchone()
        if solution != None:
            solution = int(solution[0])
            
        cursor.close()
        connexion.close()
        print("Récupèration réussi de la solution que l'utilisateur a choisi")
        return solution

    except sqlite3.Error as error:
        print("Erreur lors du vote", error)
        return



def Get_Most_Voted_Solution(question_id) -> int :
    """cherche toutes les solutions associées à la question, retourne celle qui à le plus de vote"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        #print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(question_id,))
        nb_vote_max=cursor.fetchone()
        nb_vote_max=nb_vote_max[0]
        #print("Le maximum de vote est " + str(nb_vote_max))
        cursor.execute("SELECT * FROM solutions WHERE question_id=? AND nb_vote=? ", (question_id,nb_vote_max))
        best_solution=cursor.fetchone()

        cursor.close()
        connexion.close()
        #print("Connexion SQLite est fermée")
        return best_solution
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de la solution la plus voté", error)

def Get_Choosen_Solution(questions : list) -> list:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        #print("Connexion réussie à SQLite")
        choosen_solutions = []

        for q in questions:
            cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(q[0],))
            nb_vote_max=cursor.fetchone()
            nb_vote_max=nb_vote_max[0]
            #print("Le maximum de vote est " + str(nb_vote_max))
            cursor.execute("SELECT * FROM solutions WHERE question_id=? AND nb_vote=? ", (q[0],nb_vote_max))
            best_solution=cursor.fetchone()
            choosen_solutions.append(best_solution)
    
        cursor.close()
        connexion.close()
        #print("Connexion SQLite est fermée")
        return choosen_solutions[:-1]
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des solutions choisi", error)


def GetAllSolutions(choosen_question:list):
    #L'argument choosen_question est une liste de question
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        all_solutions=[] #liste de liste de solution

        for q in choosen_question:
            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(q[0],))
            solutions = cursor.fetchall() #liste de solutions proposé pour la question q
            all_solutions.append(solutions)

        print("Récupération de toutes les solutions réussi, il y en a = " + str(len(all_solutions)))
        cursor.close()
        connexion.close()
        print(all_solutions)
        return all_solutions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de toutes les solutions :",error)

def GetAllQuestions(choosen_question : list):
    ## celle dont le parent a pour titre NextQuestionString
    try :
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        assert len(choosen_question) > 0, "aucune question choisi, ne peux pas renvoyer GetAllQuestions"

        all_questions =[[choosen_question[0]]]

        for i in range(1,len(choosen_question)):

            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(choosen_question[i][4],)) # question avec le meme choix parent
            questions = cursor.fetchall()
            all_questions.append(questions)
        
        cursor.close()
        connexion.close()
        print("Récupération de toutes les questions effectués")
        print(all_questions)
        return all_questions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de toutes les questions :",error)

def Get_Voting_For_Solution_or_Question(pb_parent_id) -> int :
    """Si le nombre de question d'un problème est impair on vote pour une solution, sinon pour une question."""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT count(id) FROM question WHERE pb_parent_id = ?",(pb_parent_id,))
        parité = cursor.fetchone()[0] % 2

        print("Récupération de l'état vote pour question ou solution réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        if parité == 1:
            return "vote solution"
        else:
            return "vote question"
    except sqlite3.Error as error:
        print("Erreur de la récupération de l'état du vote", error)


def Etend_Branche(titre,utilisateur,question_parent, pb_parent_id) -> None :
    """créé une nouvelle question en fonction de la solution choisit, créé les données associé dans la base de données 
    -> le en fonction de la solution à besoin d'une fonction pour savoir qui a eu le plus de vote"""
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
    """Ajoute "backtracking" en tant que nouvelle solution et tous les points de retour possibles en solutions"""
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
        print("init_backtracking_vote erreur")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("init_backtracking_vote erreur", error)



def do_backtracking(backtrack_to_id, pb_parent_id) -> None :
    """Coupe toutes les questions postérieures à celle où on backtrack et réimplente la question en question""" 
    try:
        print("___do BACKTRACKIGN")
        print(backtrack_to_id, pb_parent_id)
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM question")
        new_id_question=cursor.fetchone()[0]+1

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
    """vérifie contrainte d’intégrité, éligibilité aux votes et change compte de vote"""
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

def EnvoieMessage(utilisateur : str,texte : str,question_id : int) -> None :
    """créé une ligne dans le schéma message, l’associe à la question"""
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
        sql = "INSERT INTO msg (id,texte,utilisateur_email,question_id) VALUES (?, ?, ?, ?)"
        donnes=[(new_id,texte,utilisateur,question_id)]
        cursor.executemany(sql,donnes )
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table message")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table message/question", error)

def GetNames(utilisateur):
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT nom,prenom FROM utilisateurs WHERE email = ? ",(utilisateur,))
        names = cursor.fetchone()

        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        print("Names = " + str(names))
        return names
    except sqlite3.Error as error:
        print("Erreur lors de la récupération du nom", error)

## Récupération de données à afficher

def GetProblematiques() -> list:
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
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT * FROM pb WHERE id=?",(id_prob,))
        pb = cursor.fetchone()
        print("Récupération de la problématique")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return pb
    except sqlite3.Error as error:
        print("Erreur lors de la récupération d'une problématique", error)

def GetQuestions(id_prob : int) -> list:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        liste_questions = []

        cursor.execute("SELECT * FROM question WHERE pb_parent_id = ? AND id=question_parent_id ",(id_prob,))
        question = cursor.fetchone()
        liste_questions.append(question)

        b = True
        while b:
            cursor.execute("SELECT * FROM question WHERE question_parent_id = ? AND NOT id=question_parent_id", (liste_questions[-1][0],)) # on cherche si la derniere sous proposition a un enfant
            question = cursor.fetchone()
            if question == None:
                b = False
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
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT * FROM solutions WHERE question_id = ?",(id_question,))
        liste_solution = cursor.fetchall()
        
        print("Récupération des propositions réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return liste_solution
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des solutions", error)

def ValidEmail(email :str) -> bool:
    
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
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT * FROM utilisateurs WHERE email=?",(email,))
        utilisateur = cursor.fetchall()
        
        b = utilisateur == []

        print("Vérification réussi ="+str(b))
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return b
    except sqlite3.Error as error:
        print("Erreur lors de la vérification que le nouveau mail n'est pas déjà dans la BD", error)

def Register(email : str, name :str, fname: str, password : str):
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")


        cursor.execute("SELECT date('now')")
        date =cursor.fetchone()
        date=date[0]
        cursor.execute("INSERT INTO utilisateurs VALUES (?,?,?,?)",(email,name,fname,cryptageXOR(password),date))

        print("Nouvel utilisateurs insérer")
        connexion.commit()
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return 
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion du nouvel utilisateurs", error)

def ValidLogin(email : str, password : str) -> bool:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT * FROM utilisateurs WHERE email=?",(email,))
        user = cursor.fetchone()

        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")

        if user == None or user==[]:
            return False
        print(user)
        ## Check password ici

        if decryptageXOR(user[3])==password:
            return True

        return False
    except sqlite3.Error as error:
        print("Erreur lors de la vérification du login", error)

def Get_Messages(id_question : int ) -> List:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        print("L'id de la question est " + str(id_question))

        cursor.execute("SELECT * FROM msg WHERE question_id=?",(id_question,))
        messages = cursor.fetchall()

        print("Il y a "+str(len(messages))+" messages.")

        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")

        return messages
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des messages", error)


key = "038UTRENDGKFGS43I48302RZIPÖGJDLFM?"

def cryptageXOR(plain_text : str) -> str:
    encrypted_text= ""
    key_itr = 0
    for i in range(len(plain_text)):
        lettre_encrpt = ord(plain_text[i]) ^ ord(key[key_itr])
        encrypted_text += hex(lettre_encrpt)[2:].zfill(2) # enlève 0x et ajoute des zeros devant si nécessaire pour avoir deux chiffre hexa <-> 1 nombre
        key_itr +=1
        if key_itr>=len(key):
            key_itr=0
    return encrypted_text

def decryptageXOR(encrypted_text : str) -> str: 
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
# -*- coding: utf-8 -*-
from logging import fatal
from re import U
import sqlite3
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
        new_pb_id=new_pb_id[0]+1

        sql_pb = "INSERT INTO pb (id,DateCreation,titre,texte,utilisateur_email) VALUES (?,?,?,?,?)"
        donnees_pb=[(new_pb_id,date,titre,description,utilisateur)] #attention, utilisateur est text et non id
        cursor.executemany(sql_pb, donnees_pb)


        cursor.execute("SELECT max(id) FROM question ")
        new_question_id=cursor.fetchone()
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
        new_id=cursor.fetchone()[0] + 1

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
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT question_id FROM votes WHERE utilisateur_email = ? AND question_id =?",(user,question_id))
        solution = cursor.fetchone()
        if solution != None:
            solution = int(solution[0])

        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return solution

    except sqlite3.Error as error:
        print("Erreur lors du vote", error)
        return



def Get_Most_Voted_Solution(question_id) -> int :
    """cherche toutes les solutions associées à la question, retourne l’id celle qui à le plus de vote"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(question_id,))
        nb_vote_max=cursor.fetchone()
        nb_vote_max=nb_vote_max[0]
        print("Le maximum de vote est " + str(nb_vote_max))
        cursor.execute("SELECT id FROM solutions WHERE question_id=? AND nb_vote=? ", (question_id,nb_vote_max))
        id_best_solution=cursor.fetchone()
        id_best_solution=id_best_solution[0]
        print("Enregistrements éxécutés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return id_best_solution
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)

def Etend_Branche(titre,utilisateur,question_parent) -> None :
    """créé une nouvelle question en fonction de la solution choisit, créé les données associé dans la base de données 
    -> le en fonction de la solution à besoin d'une fonction pour savoir qui a eu le plus de vote"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM question")
        new_id=cursor.fetchone()

        date=cursor.fetchone()
        date=date[0]

        donnees=[(new_id,date,titre,utilisateur,question_parent)]
        sql = "INSERT INTO question (id,DateCreation,titre,auteur,question_parent_id) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table question")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table question", error)


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

def EnvoieMessage(utilisateur,texte,question_id) -> None :
    """créé une ligne dans le schéma message, l’associe à la question"""
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(id) FROM message ")
        new_id=cursor.fetchone()
        new_id=new_id[0]+1
        sql = "INSERT INTO message (id,texte,utilisateur,question_id) VALUES (?, ?, ?, ?)"
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

    if not email_decomposé[1].endswith(".com") or email_decomposé[1].endswith(".fr"):
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

def Register(email : str, name :str, fname: str):
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("INSERT INTO utilisateurs VALUES (?,?,?)",(email,name,fname,))

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

        return True
    except sqlite3.Error as error:
        print("Erreur lors de la vérification du login", error)
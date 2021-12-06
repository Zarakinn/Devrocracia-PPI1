# -*- coding: utf-8 -*-
import sqlite3

database = "data/database.db"


def Creation_Problemes(titre,description,utilisateur) -> None :
    """calcule de la date, d’un id unique et création d’une ligne dans le schéma problématique"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT date('now')")
        date =cursor.fetchone()
        date=date[0]
        cursor.execute("SELECT max(id) FROM pb ")
        new_id=cursor.fetchone()
        new_id=new_id[0]+1
        sql = "INSERT INTO pb (id,DateCreation,titre,texte,utilisateur_id) VALUES (?, ?, ?, ?,?)"
        donnees=[(new_id,date,titre,description,utilisateur)]
        cursor.executemany(sql, donnees)
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)


def Creation_Proposition(Sous_probleme_id,titre,description) -> None :
    """ajoute une proposition pour un sous_problème"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM propositions ")
        new_id=cursor.fetchone()

        donnees=[(new_id,Sous_probleme_id,titre,description,0)]
        sql = "INSERT INTO propositions (id,sous_pb_id,titre,texte,nb_vote) VALUES (?, ?, ?, ?,?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        
        print("Enregistrements insérés avec succès dans la table propositions")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table propositions", error)


def Get_Selected_Propostion(sous_prob_id) -> int :
    """cherche toutes les propositions associées aux problèmes, retourne l’id celle qui à le plus de vote"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(nb_vote) FROM propositions ")
        nb_vote_max=cursor.fetchone()
        nb_vote_max=nb_vote_max[0]
        print("Le maximum de vote est " + str(nb_vote_max))
        cursor.execute("SELECT PR.id FROM propositions WHERE sous_pb_id=? AND nb_vote=? ", (sous_prob_id,nb_vote_max))
        id_best_prop=cursor.fetchone()
        id_best_prop=id_best_prop[0]
        print("Enregistrements éxécutés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return id_best_prop
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)

def Etend_Branche(titre,utilisateur_id,sous_pb_parent) -> None :
    """créé un nouveau sous problème en fonction de la proposition choisit, créé les données associé dans la base de données 
    -> le en fonction de sous proposition à besoin d'une fonction pour savoir qui a eu le plus de vote"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT max(id) FROM sous_pb ")
        new_id=cursor.fetchone()

        date=cursor.fetchone()
        date=date[0]

        donnees=[(new_id,date,titre,utilisateur_id,sous_pb_parent)]
        sql = "INSERT INTO sous_pb (id,DateCreation,titre,auteur_id,sous_pb_parent_id) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table sous_pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table sous_pb", error)


def Vote(utilisateur, proposition) -> None :
    """vérifie contrainte d’intégrité, éligibilité aux votes et change compte de vote"""
    return None 


def EnvoieMessage(utilisateur,texte,sous_proposition_id) -> None :
    """créé une ligne dans le schéma message, l’associe aux sous problème"""
    try:
        connexion = sqlite3.connect('database.db')
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(id) FROM message ")
        new_id=cursor.fetchone()
        new_id=new_id[0]+1
        sql = "INSERT INTO message (id,texte,utilisateur_id,sous_pb_id) VALUES (?, ?, ?, ?)"
        donnes=[(new_id,texte,utilisateur,sous_proposition_id)]
        cursor.executemany(sql,donnes )
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table message")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table message/sous_pb", error)


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



def GetSousProblematiques(id_prob : int) -> list:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        liste_spbs = []

        cursor.execute("SELECT * FROM sous_pb WHERE pb_parent_id = ? AND id=sous_pb_parent_id ",(id_prob,))
        spb = cursor.fetchone()
        liste_spbs.append(spb)

        b = True
        while b:
            cursor.execute("SELECT * FROM sous_pb WHERE sous_pb_parent_id = ? AND NOT id=sous_pb_parent_id", (liste_spbs[-1][0],)) # on cherche si la derniere sous proposition a un enfant
            spb = cursor.fetchone()
            print(spb)
            if spb == None:
                b = False
                break
            else :
                liste_spbs.append(spb)


        print("Récupération des sous_problématiques réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return liste_spbs
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des sous-problématiques", error)

def GetPropositions(id_sous_prob : int) -> list:
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")

        cursor.execute("SELECT * FROM propositions WHERE sous_pb_id = ?",(id_sous_prob,))
        liste_sous_props = cursor.fetchall()
        
        print("Récupération des sous_problématiques réussi")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return liste_sous_props
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des propositions", error)
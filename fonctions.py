# -*- coding: utf-8 -*-
import sqlite3

def Creation_Problemes(titre,description) -> None :
    """calcule de la date, d’un id unique et création d’une ligne dans le schéma problématique"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT date('now')")
        date =cursor.fetchone()
        date=date[0]
        cursor.execute("SELECT max(id) FROM pb ")
        res=cursor.fetchone()
        res=res[0]+1
        sql = "INSERT INTO pb (id,DateCreation,titre,texte) VALUES (?, ?, ?, ?)"
        donnees=[(res,date,titre,description)]
        cursor.executemany(sql, donnees)
        connexion.commit()
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)


def Creation_Proposition(Utilisateur,Sous_probleme_id,titre,description) -> None :
    """ajoute une proposition pour un problème"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        donnees=[(Utilisateur,Sous_probleme_id,titre,description)]
        sql = "INSERT INTO propositions (id,sous_pb_id,titre,texte) VALUES (?, ?, ?, ?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table propositions")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table propositions", error)


def Get_Selected_Propostion(id) -> int :
    """cherche toutes les propositions associées aux problèmes, retourne l’id celle qui à le plus de vote"""
    try:
        connexion = sqlite3.connect("database2.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(nb_vote) FROM propositions ")
        res=cursor.fetchone()
        res=res[0]
        print(res)
        cursor.execute("SELECT PR.id FROM propositions PR JOIN  pb PB ON PR.id=? WHERE nb_vote=? ", (id,res,))
        new_id=cursor.fetchone()
        new_id=new_id[0]
        print("Enregistrements éxécutés avec succès dans la table pb")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
        return new_id
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table pb", error)


print(Get_Selected_Propostion(1))


def Etend_Branche(utilisateur,sous_problème) -> None :
    """créé un nouveau sous problème en fonction de la proposition choisit, créé les données associé dans la base de données 
    -> le en fonction de sous proposition à besoin d'une fonction pour savoir qui a eu le plus de vote"""
    try:
        connexion = sqlite3.connect("database.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        donnees=[(utilisateur, sous_problème)]
        sql = "INSERT INTO sous_pb (id,titre) VALUES (?, ?)"
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
        connexion = sqlite3.connect('database2.db')
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        cursor.execute("SELECT max(id) FROM message ")
        res=cursor.fetchone()
        res=res[0]+1
        sql = "INSERT INTO message (id,texte,utilisateur_id,sous_pb_id) VALUES (?, ?, ?, ?)"
        donnes=[(res,texte,utilisateur,sous_proposition_id)]
        cursor.executemany(sql,donnes )
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table message")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table message/sous_pb", error)


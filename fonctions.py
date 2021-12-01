# -*- coding: utf-8 -*-
import sqlite3


def Creation_Proposition(Utilisateur,id_Sous_problème,titre,description) -> None :
    """ajoute une proposition pour un problème"""
    try:
        connexion = sqlite3.connect("tables.db")
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        donnees=[(Utilisateur,id_Sous_problème,titre,description)]
        sql = "INSERT INTO propositions (propositions_id,sous_pb_id,titre,description) VALUES (?, ?, ?, ?)"
        cursor.executemany(sql, donnees)
        print("t")
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table propositions")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table propositions", error)


Creation_Proposition(1,10,"plantons des arbres","Ca manque de verdure !")


"""        sql = "INSERT INTO propositions (Utilisateur,id_Sous_problème,titre,description) VALUES (?, ?, ?, ?)"
        cursor.executemany(sql, donnees)"""
        

def EnvoieMessage(utilisateur,texte,sous_proposition) -> None :
    """créé une ligne dans le schéma message, l’associe aux sous problème"""
    try:
        connexion = sqlite3.connect('myd')
        cursor = connexion.cursor()
        print("Connexion réussie à SQLite")
        sql = "INSERT INTO Message (utilisateur,texte,sous_proposition) VALUES (?, ?, ?)"
        cursor.executemany(sql, utilisateur,texte,sous_proposition)
        connexion.commit()
        print("Enregistrements insérés avec succès dans la table Message")
        cursor.close()
        connexion.close()
        print("Connexion SQLite est fermée")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table Message", error)






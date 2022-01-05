# -*- coding: utf-8 -*-
from logging import fatal, raiseExceptions
from re import U
import sqlite3
from typing import List
import string
alphabet = string.ascii_letters + string.digits
hexa="0123456789abcdef"
database = "data/database.db"

def Basic_Query(sql, param_sql, error_msg):
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

        cursor.execute("SELECT max(id) FROM solutions ")
        new_id=cursor.fetchone()
        if new_id==(None,): # Si il n'y a pas encore de solution, max(id) renvoie None : on catch l'erreur et on résoud le problème
            new_id = [0]
        new_id = new_id[0] + 1

        donnees=[(new_id,question_id,titre,description,0)]
        sql = "INSERT INTO solutions (id,question_id,titre,texte,nb_vote) VALUES (?, ?, ?, ?,?)"
        cursor.executemany(sql, donnees)
        connexion.commit()
        
        cursor.close()
        connexion.close()
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table solutions", error)

def Get_Solution_Voter_by_User(question_id, user) -> int:
    """
    On essaie de trouver si l'utilisateur passer en paramètre a déjà voté pour le choix identifié par question_id. Si c'est le cas, on renvoi son choixi sinon on renvoie None
    """
    query = "SELECT solution_id FROM votes WHERE utilisateur_email = ? AND question_id =?"
    param = (user,question_id)
    error = "Erreur lors du vote"
    solution = Basic_Query(query, param, error)
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

def Get_Chosen_Solution(questions : list) -> list:
    """
    On souhaite récupérer la liste de toutes les solutions qui ont été choisit dans cette problématique lors des choix précédents
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        #print("Connexion réussie à SQLite")
        chosen_solutions = []
        for q in questions:
            cursor.execute("SELECT max(nb_vote) FROM solutions WHERE question_id=? ",(q[0],))
            nb_vote_max=cursor.fetchone()
            nb_vote_max=nb_vote_max[0]

            # Ici, grâce à la structure qu'on a choisi, il y a toujours la solution "backtracking" ce qui assure qu'il n'y a pas de problème

            #print("Le maximum de vote est " + str(nb_vote_max))
            cursor.execute("SELECT * FROM solutions WHERE question_id=? AND nb_vote=? ", (q[0],nb_vote_max))
            best_solution=cursor.fetchone()

            # Si deux solutions on le même nombre de votes, on en choisit un arbitrairement 
            chosen_solutions.append(best_solution)
    
        cursor.close()
        connexion.close()
        #print("Connexion SQLite est fermée")
        return chosen_solutions[:-1]
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des solutions choisi", error)


def Ajout_pourcentage_vote(choix : list ) -> list:
    """
    Prend une liste de solutions à une même question sous la forme d'une liste de tuple, et renvoie cette même liste en rajoutant le pourcentage de votes ce chaque solution à la fin 
    """
    if len(choix)==0:
        return []
    for c in choix:
        assert type(c)==tuple, "un des choix n'est pas sous la forme de tuples"
        assert len(c)==5, "un choix n'est pas de taille 5"
        assert type(c[0])==type(c[1])==int and type(c[2])==type(c[3])==str, "type invalide"
        assert type(c[4])==int, "le champs votes n'est pas un entier"
        vote = c[4]
        assert vote >= 0, "erreur, nombre de votes négatif"
    
    q_id = choix[0][1]
    nb_total_vote=0
    for c in choix:
        assert c[1] == q_id, "solutions pas associé aux même votes"
        nb_total_vote+=c[4]
    if nb_total_vote==0:
        nb_total_vote=1 # on évite le zero division error, et on altère pas si il n'y a aucun vote

    for i,c in enumerate(choix):
        c=list(c)
        c.append(int((c[4]/nb_total_vote)*10000)/100) # Approximation à la deuxième virgule près
        c=tuple(c)
        choix[i]=c
    
    return choix



def Get_All_Solutions(chosen_question:list):
    """
    On souhaite récupérer la liste de toutes les solutions qui ont été proposé dans cette problématique, pour cela on part de la liste des questions qui ont été posé
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        all_solutions=[] #liste de liste de solution
        for q in chosen_question:
            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(q[0],))
            solutions = cursor.fetchall() #liste de solutions proposé pour la question q

            solutions_w_pourcent = Ajout_pourcentage_vote(solutions)
            all_solutions.append(solutions_w_pourcent)

        print("Récupération de toutes les solutions réussi, il y en a = " + str(len(all_solutions)))
        cursor.close()
        connexion.close()
        print(all_solutions)
        return all_solutions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération de toutes les solutions :",error)

def Get_All_Questions(chosen_question : list):
    """
    On souhaite récupérer les questions qui ont été choisi par les utilisateurs, grâce à notre structure  on sait que le parent à le string de ces fonctions 
    a pour titre la variable NextQuestionString
    """
    try :
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        assert len(chosen_question) > 0, "aucune question choisi, ne peux pas renvoyer Get_All_Questions"

        all_questions =[[chosen_question[0]]]
        for i in range(1,len(chosen_question)):
            cursor.execute("SELECT * FROM solutions WHERE question_id=?",(chosen_question[i][4],)) # question avec le meme choix parent
            questions = cursor.fetchall()

            solutions_w_pourcent = Ajout_pourcentage_vote(questions)
            all_questions.append(solutions_w_pourcent)

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
    parité = Basic_Query(query, param, error)[0][0] % 2
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

        #on bloque le backtracking et l'archivage trop tôt dans la branche
        cursor.execute("SELECT count(*) FROM question where pb_parent_id = ?",(pb_parent_id,))
        count = cursor.fetchone()[0]
        if count > 3: 
            donnees=[(new_id_sol, new_id_question, "Backtracking", "Vote pour le retour en arrière.", 0)]
            sql = "INSERT INTO solutions (id, question_id, titre, texte, nb_vote) VALUES (?, ?, ?, ?, ?)"
            cursor.executemany(sql, donnees)
            donnees=[(new_id_sol+1, new_id_question,
            "La problématique est résolue", "Voter pour cet élément si vous considérez que les solutions votées sont suffisantes pour résoudre le problème initial.",0)]
            sql = "INSERT INTO solutions (id, question_id, titre, texte, nb_vote) VALUES (?, ?, ?, ?, ?)"
            cursor.executemany(sql, donnees)
        
        connexion.commit()
        cursor.close()
        connexion.close()
    except sqlite3.Error as error:
        print("Erreur lorsque la branche a été étendu", error)


def Init_Backtracking_Vote(pb_parent_id, question_parent_id, solution_list) -> None :
    """
    Ajoute "backtracking" en tant que nouvelle question et tous les points de retour possibles en solutions
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

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

        #insère la question "où revenir" qui sera parent des options de backtracking
        donnees=[(new_id_question, date, "Où revenir ?", None, question_parent_id, pb_parent_id)]
        sql = "INSERT INTO question (id,DateCreation,titre,auteur_email,question_parent_id, pb_parent_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, donnees)

        #on ajoute les solutions
        for i,question in enumerate(solution_list[1:]):
            #question[1] est l'id de la question à laquelle une solution répond initialement, nécessaire pour savoir où backtracker
            donnees=[(new_id_sol+i, new_id_question, question[2], "(Hauteur "+str(question[1])+") "+question[3], 0)]
            sql = "INSERT INTO solutions (id, question_id, titre, texte, nb_vote) VALUES (?, ?, ?, ?, ?)"
            cursor.executemany(sql, donnees)
                
        connexion.commit()
        cursor.close()
        connexion.close()
    except sqlite3.Error as error:
        print("Init_Backtracking_Vote erreur", error)



def Do_Backtracking(backtrack_to_id, pb_parent_id) -> None :
    """
    Coupe toutes les questions postérieures à celle où on backtrack et réimplente la question à laquelle backtracker
    """ 
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

        cursor.execute("SELECT max(id) FROM question")
        new_id_question=cursor.fetchone()
        if new_id_question==None:
            new_id_question=[0]
        new_id_question=new_id_question[0]+1

        #Coupage de toutes les questions postérieures à celle où on backtrack
        cursor.execute("UPDATE question SET branche_morte = 1 WHERE pb_parent_id = ? AND id > ?", (pb_parent_id, backtrack_to_id))
        cursor.execute("DELETE FROM question WHERE branche_morte = 1") #(Pour l'instant pas de mémoire du backtracking)
        #Reimplementation de la question à laquelle backtracker: on change son id et elle devient nouvelle d'un point de vue de la BD
        cursor.execute("UPDATE question SET id = ? WHERE id = ?", (new_id_question, backtrack_to_id))        

        connexion.commit()
        cursor.close()
        connexion.close()
    except sqlite3.Error as error:
        print("Do_Backtracking echec", error)

def Vote(solution_id, id_question, utilisateur) -> None :
    """
    Enregistre le vote d'un utilisateur, vérifie qu'elle n'a pas déjà voté. Si c'est le cas, on supprime son ancien vote.
    """
    try:
    #removing previous vote
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

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
        return
    except sqlite3.Error as error:
        print("Erreur lors du vote :", error)
        return

def Break_Text(text : str, char_per_line : int) -> str:
    """
    Ajoute des <br> dans les chaines tout les *char_per_line* caractères
    Utile pour le formattage du texte dans l'affichage du chat
    """
    broke_text = ""
    while len(text) > char_per_line:
        broke_text += text[:char_per_line]
        broke_text += "<br>"
        text = text[char_per_line+1:]
    return broke_text+text

def Send_Message_In_Chat(utilisateur : str,texte : str,question_id : int) -> None :
    """
    Envoie un message :
    Créé une ligne dans le schéma message et l’associe à la question
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()
        print("Insertion de message ...")
        cursor.execute("SELECT max(id) FROM msg ")
        new_id=cursor.fetchone()
        if new_id == (None,):
            new_id = [0]
        new_id=new_id[0]+1

        cursor.execute("SELECT CURRENT_TIMESTAMP")
        date =cursor.fetchone()
        date=date[0]

        texte = Break_Text(texte, 120)

        sql = "INSERT INTO msg (id,texte,utilisateur_email,question_id,date) VALUES (?, ?, ?, ?,?)"
        donnes=[(new_id,texte,utilisateur,question_id,date)]
        cursor.executemany(sql,donnes )
        connexion.commit()
        cursor.close()
        connexion.close()
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion dans la table message/question", error)

def Get_Names(utilisateur):
    """
    On récupère le nom et prénom d'un utilisateur à partir de son email
    """
    query = "SELECT nom,prenom FROM utilisateurs WHERE email = ? "
    param = (utilisateur,)
    error = "Erreur lors de la récupération du nom"
    names = Basic_Query(query, param, error)[0]
    # Cette fonction ne peux être appellé que si l'utilisateur est a réussi à se connecter, donc si il est inscrit et qu'il y a bien une ligne dans le schéma user lui correspondant
    print("Names = " + str(names))
    return names

## Récupération de données à afficher

def Get_Problematiques() -> list:
    """
    Récupère la liste de toutes les problématiques
    """
    query = "SELECT * FROM pb"
    param = ()
    error = "Erreur lors de la récupération des problématiques"
    problematiques = Basic_Query(query, (), error)
    return problematiques


def Get_Problematique(id_prob : int) -> list:
    """
    Récupère les informations  sur une problématique grâce à son id
    """
    query = "SELECT * FROM pb WHERE id=?"
    param = (id_prob,)
    error = "Erreur lors de la récupération d'une problématique"
    problematique = Basic_Query(query, param, error)
    if problematique == None or problematique == []:
        print("Erreur, la problématique n'existe pas")
    return problematique[0]

def Get_Questions(id_prob : int) -> list:
    """
    Récupère les questions successives associées à une problématique
    """
    try:
        connexion = sqlite3.connect(database)
        cursor = connexion.cursor()

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
        return liste_questions
    except sqlite3.Error as error:
        print("Erreur lors de la récupération des questions", error)

def Get_Solutions(id_question : int) -> list:
    """
    On récupère toutes les solutions associé à une question
    """
    query = "SELECT * FROM solutions WHERE question_id = ?"
    param = (id_question,)
    error = "SELECT * FROM utilisateurs WHERE email=?"
    liste_solution = Basic_Query(query, param, error)
    return liste_solution

def Valid_Email(email :str) -> bool:
    """
    On vérifie que le format proposé en email vérifie quelque condition de base:
    il est de la forme xxx@xxx.fr|eu|com|net
    """
    assert type(email)==str, "L'argument n'est pas un string"

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

def Not_Already_Registered(email : str) -> bool:
    """
    Vérifie que l'email passé en paramètre n'est pas déjà dans la base de donnée,
    c'est à dire que personne ne s'est inscrit avec le mail email
    """
    query = "SELECT * FROM utilisateurs WHERE email=?"
    param = (email,)
    error = "Erreur lors de la vérification que le nouveau mail n'est pas déjà dans la BD"
    utilisateur = Basic_Query(query, param, error)
    b = utilisateur == []
    print("Vérification réussi ="+str(b))
    return b

def Register(email : str, name :str, fname: str, password : str):
    """
    Enregistre un nouvelle utilisateur grâce aux paramètre donnée
    Cette fonction doit être utilisé après avoir appellé la fonction Valid_Email pour vérifié que cet email n'est pas déjà dans la base de donnée
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
    

def Valid_Login(email : str, password : str) -> bool:
    """
    Vérifie que le login  donnée existe dans la base de donnée et que le mot de passe correspond. 
    """
    query = "SELECT * FROM utilisateurs WHERE email=?"
    param = (email,)
    error = "Erreur lors de la vérification du login"
    user = Basic_Query(query, param, error)
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
    messages = Basic_Query(query, param, error)
    print("Il y a "+str(len(messages))+" messages.")
    return messages


def Get_Key():
    with open("key.txt") as file :
        temp = file.read()
        if len(temp) > 5:
            return temp
        else :
            raiseExceptions("Impossible de lire la clef")

key = Get_Key()
##print("key = " + key)
def ChangeKey(new_key): 
    try :

        for carac in new_key:
            if not carac in alphabet:
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

def cryptageXOR(plain_text : str, key : str = key ) -> str:
    """
    Encrypte un texte grâce à la méthode XOR
    """
    assert type(plain_text) == type(key) == str, "Le texte ou la clef n'est pas un texte"
    for carac in key:
            assert carac in alphabet,"Clef ne contenant pas que des chiffres et lettres sans accent"
            
    assert key != "" and key != None, "clef vide"
    
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
    assert type(encrypted_text) == type(key) == str, "Le texte ou la clef n'est pas un texte"
    assert key != "" and key != None, "clef vide"
    for carac in key:
            assert carac in alphabet,"Clef ne contenant pas que des chiffres et lettres sans accent"
    for carac in encrypted_text:
            assert carac in hexa,"Texte ne contenant pas que de l'hexadécimal"
    assert len(encrypted_text)%2==0,"Texte encrypté de longueur impair"
            

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
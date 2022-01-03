CREATE TABLE pb (
id integer,
DateCreation date,
titre text,  
texte text,
utilisateur_email text,
CONSTRAINT pb_PK PRIMARY KEY (id),
FOREIGN KEY(utilisateur_email) REFERENCES "utilisateurs"("email"));

CREATE TABLE utilisateurs (
email text,
nom VARCHAR (15),
prenom VARCHAR (15),  
mdp text,
CONSTRAINT utilisateurs_PK PRIMARY KEY (email));

CREATE TABLE question (
id integer,
DateCreation date,
titre VARCHAR(100),
auteur_email text,
question_parent_id integer,
pb_parent_id integer,
branche_morte integer DEFAULT 0,
CONSTRAINT sous_pb_PK PRIMARY KEY (id),
FOREIGN KEY(auteur_email) REFERENCES "utilisateurs"("email"),
FOREIGN KEY(question_parent_id) REFERENCES "question"("id"),
FOREIGN KEY(pb_parent_id) REFERENCES "pb"("id"));

CREATE TABLE solutions (
id integer,
question_id integer,
titre text,
texte text,
nb_vote integer,
CONSTRAINT propositions_PK PRIMARY KEY (id),
FOREIGN KEY(question_id) REFERENCES "question"("id"));

CREATE TABLE votes (
utilisateur_email text,
solution_id integer,
question_id integer,
CONSTRAINT vote_PK PRIMARY KEY (utilisateur_email, question_id),
FOREIGN KEY(utilisateur_email) REFERENCES "utilisateurs"("email"),
FOREIGN KEY(solution_id) REFERENCES "solutions"("id"),
FOREIGN KEY(question_id) REFERENCES "question"(id));

CREATE TABLE "msg" (
	"id"	integer,
	"texte"	text,
	"utilisateur_email" integer,
	"question_id"	integer,
	"date" date,
	CONSTRAINT "msg_PK" PRIMARY KEY("id"),
	FOREIGN KEY("question_id") REFERENCES "question_pb"("id"),
	FOREIGN KEY(utilisateur_email) REFERENCES "utilisateurs"("email")
);

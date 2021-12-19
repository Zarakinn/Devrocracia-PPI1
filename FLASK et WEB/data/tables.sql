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
CONSTRAINT utilisateurs_PK PRIMARY KEY (email));

CREATE TABLE sous_pb (
id integer,
DateCreation date,
titre VARCHAR(100),
auteur_email text,
sous_pb_parent_id integer,
pb_parent_id integer,
CONSTRAINT sous_pb_PK PRIMARY KEY (id),
FOREIGN KEY(auteur_email) REFERENCES "utilisateurs"("email"),
FOREIGN KEY(sous_pb_parent_id) REFERENCES "sous_pb"("id"),
FOREIGN KEY(pb_parent_id) REFERENCES "pb"("id"));

CREATE TABLE propositions (
id integer,
sous_pb_id integer,
titre text,
texte text,
nb_vote integer,
CONSTRAINT propositions_PK PRIMARY KEY (id),
FOREIGN KEY(sous_pb_id) REFERENCES "sous_pb"("id"));

CREATE TABLE votes (
utilisateur_email text,
proposition_id integer,
sous_pb_id integer,
CONSTRAINT vote_PK PRIMARY KEY (utilisateur_email, sous_pb_id),
FOREIGN KEY(utilisateur_email) REFERENCES "utilisateurs"("email"),
FOREIGN KEY(proposition_id) REFERENCES "propositions"("id"),
FOREIGN KEY(sous_pb_id) REFERENCES "sous_pb"(id));

CREATE TABLE "msg" (
	"id"	integer,
	"texte"	text,
	"utilisateur_email" integer,
	"sous_pb_id"	integer,
	CONSTRAINT "msg_PK" PRIMARY KEY("id"),
	FOREIGN KEY("sous_pb_id") REFERENCES "sous_pb"("id"),
	FOREIGN KEY(utilisateur_email) REFERENCES "utilisateurs"("email")
);

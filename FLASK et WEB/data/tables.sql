CREATE TABLE pb (
id integer,
DateCreation date,
titre text,  
texte text,
utilisateur_id integer references utilisateurs(id),
CONSTRAINT pb_PK PRIMARY KEY (id));

CREATE TABLE utilisateurs (
email text,
nom VARCHAR (15),
prenom VARCHAR (15),  
CONSTRAINT utilisateurs_PK PRIMARY KEY (email));

CREATE TABLE sous_pb (
id integer,
DateCreation date,
titre VARCHAR(100),
auteur_id integer references utilisateurs(id),
sous_pb_parent_id integer references sous_pb(id),
pb_parent_id integer references pb(id),
CONSTRAINT sous_pb_PK PRIMARY KEY (id));

CREATE TABLE msg (
id integer,
texte text,
utilisateur_id integer references utilisateurs(id),
sous_pb_id integer references sous_pb(id),
CONSTRAINT msg_PK PRIMARY KEY (id));

CREATE TABLE propositions (
id integer,
sous_pb_id integer references sous_pb(id),
titre text,
texte text,
nb_vote integer,
CONSTRAINT propositions_PK PRIMARY KEY (id));

CREATE TABLE votes (
utilisateur text references utilisateurs(mail),
proposition_id integer references propositions(id),
sous_pb_id integer references sous_pb_id,
CONSTRAINT vote_PK PRIMARY KEY (utilisateur, sous_pb_id));

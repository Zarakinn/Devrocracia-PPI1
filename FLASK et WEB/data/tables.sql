CREATE TABLE pb (
id integer,
DateCreation date,
titre text,  
texte text,
utilisateur_id integer references utilisateurs(id),
CONSTRAINT pb_PK PRIMARY KEY (id));

CREATE TABLE utilisateurs (
id integer,
nom VARCHAR (15),
prenom VARCHAR (15),  
CONSTRAINT utilisateurs_PK PRIMARY KEY (id));

CREATE TABLE sous_pb (
id integer,
DateCreation date,
titre VARCHAR(100),
auteur_id integer references utilisateurs(id),
sous_pb_parent_id integer references sous_pb(id),
CONSTRAINT sous_pb_PK PRIMARY KEY (id));

CREATE TABLE forum (
id integer,
texte text,
utilisateur_id integer references utilisateurs(id),
sous_pb_id integer references sous_pb(id),
CONSTRAINT forum_PK PRIMARY KEY (id));

CREATE TABLE propositions (
id integer,
sous_pb_id integer references sous_pb(id),
titre text,
texte text,
nb_vote integer,
CONSTRAINT propositions_PK PRIMARY KEY (id));
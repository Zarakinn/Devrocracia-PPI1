import pytest,random
from fonctions_pratiques import Ajout_pourcentage_vote

def sample(n=50):
    return [[i,0,"","",random.randrange(0,9999)] for i in range(n)] # fournit une liste de solution 
def tuple_sample(n=50):
    samples = sample()
    for i in range(len(samples)):
        samples[i] = tuple(samples[i])
    return samples

def test_not_tuple():
    with pytest.raises(Exception, match="un des choix n'est pas sous la forme de tuples"):
        assert Ajout_pourcentage_vote(sample())

def test_wrongsize():
    t1 = sample()
    t1[0] = t1[0][1:]

    for i in range(len(t1)):
        t1[i]=tuple(t1[i])
    with pytest.raises(Exception, match="un choix n'est pas de taille 5"):
        assert Ajout_pourcentage_vote(t1)

def test_invalide_type():

    t2 = sample()
    t2[0][0] = ""

    for i in range(len(t2)):
        t2[i]=tuple(t2[i])
    with pytest.raises(Exception, match="type invalide"):
        assert Ajout_pourcentage_vote(t2)



def test_negative_vote():
    
    t3 = sample()
    t3[0][4] = -1

    for i in range(len(t3)):
        t3[i]=tuple(t3[i])

    with pytest.raises(Exception, match="erreur, nombre de votes négatif"):
        assert Ajout_pourcentage_vote(t3)

def test_not_same_question():
    t4 = sample()
    t4[0][1] = -1

    for i in range(len(t4)):
        t4[i]=tuple(t4[i])

    with pytest.raises(Exception, match="solutions pas associé aux même votes"):
        assert Ajout_pourcentage_vote(t4)

def test_right():
    s1 = [(0,0,"","",5)]
    assert Ajout_pourcentage_vote([(0,0,"","",5)]) == [(0,0,"","",5,100.0)]

    s2 = s1 + [(1,0,"","",5)]
    assert Ajout_pourcentage_vote(s2) == [(0,0,"","",5,50.0),(1,0,"","",5,50.0)]

    t5=tuple_sample()
    t6 = Ajout_pourcentage_vote(t5)
    sum_per=0
    for sam in t6:
        sum_per+=sam[5]
    assert abs(100-sum_per) < 0.1 + len(t6)*0.02 # Vérifie que la somme des pourcentage est proche de 100% dans la limite d'une approximation

if __name__ == "__main__":
   pytest.main([__file__, "-k", "test_", "-v", "-s"])


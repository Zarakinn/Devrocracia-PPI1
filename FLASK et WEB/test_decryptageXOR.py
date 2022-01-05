import pytest,random,string
from fonctions_pratiques import cryptageXOR,decryptageXOR
alphabet = string.ascii_letters + string.digits
hexa = "0123456789abcdef"

def test_vide():
    with pytest.raises(Exception, match="clef vide"):
        assert cryptageXOR("","")



def test_wrong_type():
    with pytest.raises(Exception, match="Le texte ou la clef n'est pas un texte"):
        assert decryptageXOR("12a27e",7654322)
    with pytest.raises(Exception, match="Le texte ou la clef n'est pas un texte"):
        assert decryptageXOR(123456,"ceci est ma clef")

def test_clef_valide():
    with pytest.raises(Exception, match="Clef ne contenant pas que des chiffres et lettres sans accent"):
        assert cryptageXOR("test string","%ù")
    
def test_hexa():
    m=50
    for _ in range(m):
        n = random.randrange(0,999)
        test_string = ''.join(random.choice(alphabet) for _ in range(n)) # Merci à Mr Oster Gerald pour cette fonction git -> exam4
        test_key = ''.join(random.choice(alphabet) for _ in range(n))

        encrypted_test = cryptageXOR(test_string,test_key)
        for carac in encrypted_test:
            assert carac in hexa

def test_valide():

    assert cryptageXOR("ABC","EFG") == '040404'
    assert cryptageXOR("ezlrmklihtuç_zà$êzemerptk","ezokkijorgfhdu2345") == '00000319060206061a13138f3b0fd217de4f00170a191b1d01'


    m=50
    for _ in range(m):
        n = random.randrange(0,999)
        test_string = ''.join(random.choice(alphabet) for _ in range(n)) # Merci à Mr Oster Gerald pour cette fonction git -> exam4
        test_key = ''.join(random.choice(alphabet) for _ in range(n))
        assert decryptageXOR(cryptageXOR(test_string,test_key),test_key) == test_string


if __name__ == "__main__":
   pytest.main([__file__, "-k", "test_", "-v", "-s"])
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
        assert decryptageXOR("1212ab98","%ù")
    
def test_alpha():
    m=50
    for _ in range(m):
        n = random.randrange(0,999)
        test_encrypted_string = ''.join(random.choice(hexa) for _ in range(2*n)) # Merci à Mr Oster Gerald pour cette fonction git -> exam4
        test_key = ''.join(random.choice(alphabet) for _ in range(n))

        decrypted_test = decryptageXOR(test_encrypted_string,test_key)
        for carac in decrypted_test:
            assert carac in alphabet

def test_pair():
    with pytest.raises(Exception, match="Texte encrypté de longueur impair"):
        assert decryptageXOR("1212ab981","testkey")    

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
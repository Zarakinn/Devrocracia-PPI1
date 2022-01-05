import pytest,random
from fonctions_pratiques import Valid_Email

def test_should_ValidEmail():
    assert Valid_Email('thomas.pallet@telecomancy.eu') == True
    assert Valid_Email('') == False
    assert Valid_Email('@.com') == False
    assert Valid_Email('.@com') == False
    assert Valid_Email('_@_.fr') == True
    assert Valid_Email('_@_.eu') == True
    assert Valid_Email('_@_.com') == True
    assert Valid_Email('_@_.net') == True
    assert Valid_Email('_@_.en') == False 
    assert Valid_Email('?@?.en') == False 
    assert Valid_Email('*$.com') == False
    


if __name__ == "__main__":
   pytest.main([__file__, "-k", "test_", "-v", "-s"])
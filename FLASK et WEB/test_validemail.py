import pytest,random
from fonctions_pratiques import ValidEmail

def test_should_ValidEmail():
    assert ValidEmail('thomas.pallet@telecomancy.eu') == True
    assert ValidEmail('') == False
    assert ValidEmail('@.com') == False
    assert ValidEmail('.@com') == False
    assert ValidEmail('_@_.fr') == True
    assert ValidEmail('_@_.eu') == True
    assert ValidEmail('_@_.com') == True
    assert ValidEmail('_@_.net') == True
    assert ValidEmail('_@_.en') == False 
    assert ValidEmail('?@?.en') == False 
    assert ValidEmail('*$.com') == False
    


if __name__ == "__main__":
   pytest.main([__file__, "-k", "test_", "-v", "-s"])
import pytest,random
from fonctions_pratiques import Break_Text

#on utilise la fonction qu'avec le paramètre char_per_line fixé à 120, on test donc avec ce paramètre.

textes_limites = [
    "",
    "apsodkpaokdpokd qwepqowjepjdaipdj poqwjepoqwjeqpowjepo jqwpoejqpowejqpowje apsodkpaokdpokd qwepqowjepjdaipdj poqwjepoqwjeqpowjepo jqwpoejqpowejqpowje",
    "lmlksdmclksdmclksdmclksd123cmlksdmclksdmclksdmclksdmclkdmclksdmclskdmclskdcmslc",
    "a"
]

textes_attentus_limites = [
    '',
    'apsodkpaokdpokd qwepqowjepjdaipdj poqwjepoqwjeqpowjepo jqwpoejqpowejqpowje apsodkpaokdpokd qwepqowjepjdaipdj poqwjepoqwj<br>qpowjepo jqwpoejqpowejqpowje',
    'lmlksdmclksdmclksdmclksdcmlksdmclksdmclksdmclksdmclkdmclksdmclskdmclskdcmslc',
    'a']

def test():
    for i in range(len(textes_limites)):
        assert(Break_Text(textes_limites[i], 120)==textes_attentus_limites[i])

if __name__ == "__main__":
   pytest.main([__file__, "-k", "test_", "-v", "-s"])
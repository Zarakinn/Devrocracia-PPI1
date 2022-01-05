from fonctions_pratiques import cryptageXOR
import datetime
import random,string
from matplotlib import pyplot as plt
import numpy as np

alphabet = string.ascii_letters + string.digits
hexa = "0123456789abcdef"



def performance():

    x,y,z=[],[],[]



    for i in range(1,100000,10000):
        for j in range(1,100000,10000):
            test_string = ''.join(random.choice(alphabet) for _ in range(i)) # Merci à Mr Oster Gerald pour cette fonction git -> exam4
            test_key = ''.join(random.choice(alphabet) for _ in range(j))
            start_time = datetime.datetime.now()
            _ = cryptageXOR(test_string,test_key)
            end_time = datetime.datetime.now()
            x.append(i)
            y.append(j)
            z.append((end_time - start_time).microseconds)
    
    ax = plt.axes(projection='3d')
    ax.scatter(x,y,z)
    ax.set_xlabel("Taille du texte")
    ax.set_ylabel("Taille de la clef")
    ax.set_zorder("Temps d'éxécution en microseconds")
    plt.show()

performance()
print("Fin")

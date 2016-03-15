# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 21:08:26 2016

@author: sylom
"""

import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import pandas as pd

"""
La grille A comporte 54 contraintes,
La grille B comporte 148 contraintes,
La grille C comporte 240 contraintes
"""

dico_size = [848,22472,58108]

#AC3 Uniquement

time_A = [1.126,23.588,42.598]
time_B = [.681,77.639,127.931]
time_C = [4.121,320.140,766.171]

plt.figure()
plt.xlabel("Taille du dictionnaire (cardinalité)")
plt.ylabel("Temps d'exécution (s)")

ax = plt.axes()
ax.set_xticks(dico_size)
plt.axis([0, 60000, 0, 800])

plt.plot(dico_size,time_A, 'ro')
plt.plot(dico_size,time_B, 'bo')
plt.plot(dico_size,time_C, 'yo')

plt.legend(["Grille A", "Grille B", "Grille C"], loc='best')
plt.title("AC3 uniquement")
plt.show()

#FC uniquement

time_A = [1.893,4.432,0.976]
time_B = [0.928,8.713,2.338]
time_C = [3.242,22.265,15.329]
fc = np.array([time_A, time_B, time_C])
plt.figure()
plt.xlabel("Taille du dictionnaire (cardinalité)")
plt.ylabel("Temps d'exécution (s)")

ax = plt.axes()
ax.set_xticks(dico_size)
plt.axis([0, 60000, 0, 25])

plt.plot(dico_size,time_A, 'ro')
plt.plot(dico_size,time_B, 'bo')
plt.plot(dico_size,time_C, 'yo')

plt.legend(["Grille A", "Grille B", "Grille C"], loc='best')
plt.title("Forward Checking uniquement")
plt.show()

#AC3 et FC

time_A = [2.036,53.537,90.722]
time_B = [1.331,175.916,273.419]
time_C = [8.942,751.287,789.336]

plt.figure()
plt.xlabel("Taille du dictionnaire (cardinalité)")
plt.ylabel("Temps d'exécution (s)")

ax = plt.axes()
ax.set_xticks(dico_size)
plt.axis([0, 60000, 0, 800])

plt.plot(dico_size,time_A, 'ro')
plt.plot(dico_size,time_B, 'bo')
plt.plot(dico_size,time_C, 'yo')

plt.legend(["Grille A", "Grille B", "Grille C"], loc='best')
plt.title("AC3 + Forward Checking")
plt.show()

#CBJ

time_A = [0.389,0.826,0.681]
time_B = [0.351,1.745,3.649]
time_C = [0.597,19.863,4.926]
cbj = np.array([time_A, time_B, time_C])
plt.figure()
plt.xlabel("Taille du dictionnaire (cardinalité)")
plt.ylabel("Temps d'exécution (s)")

ax = plt.axes()
ax.set_xticks(dico_size)
plt.axis([0, 60000, 0, 25])

plt.plot(dico_size,time_A, 'ro')
plt.plot(dico_size,time_B, 'bo')
plt.plot(dico_size,time_C, 'yo')

plt.legend(["Grille A", "Grille B", "Grille C"], loc='best')
plt.title("Conflict Backjumping")
plt.show()

avantageCBJ_FC = ((np.divide(cbj,fc) * 100) - 100) * -1
meanAv = np.mean(avantageCBJ_FC)

"""
La matrice représente les avantages de l'algorithme CBJ sur le FC
Chaque ligne correspond à une grille (A,B,C) et chaque colonne les dictionnaires
Les valeurs de la matrice montre l'avantage en pourcentage du CBJ sur le FC
On remarque que le FC est plus plus avantageux sur la grille B et le dictionnaire de 58000 mots 
mais les temps du CBJ sont en moyenne un peu près 50% meilleurs que ceux du FC
"""


data = np.array(
[
    [1.126, 54, 848],
    [23.588, 54, 22472],
    [19.649, 54, 23070],
    [42.598, 54, 58108],
    [56.845, 54, 77235],
    
    [.681, 148, 848],
    [77.639, 148, 22472],
    [43.047,148,23070],
    [127.931, 148, 58108],
    [113.066,148,77235],

    [4.121, 240, 848],
    [320.140, 240, 22472],
    [105.016,240,23070],
    [766.171, 240, 58108],
    [271.213,240,77235]
]);

df = pd.DataFrame(data, columns=['Temps', 'Contraintes', 'Dictionnaire'])
X = df[['Contraintes', 'Dictionnaire']]
y = df[['Temps']]

X1 = sm.add_constant(X)
est = sm.OLS(y,X1).fit()
P = est.params

"""
On utilise la régression multiple pour essayer de déduire une loi dirigeant le temps d'exécution de l'AC3 en fonction
de la taille du dictionnaire et du nombre de contraintes.
Cette analyse nous mène à une fonction telle que :
"""
def predictTime(contraintes,dico):
    return (dico * P['Dictionnaire']) + (contraintes * P['Contraintes']) + P['const']

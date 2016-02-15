# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 20:27:44 2016

@author: sylom
"""

import random

class CSP:
    """
    Class CSP contenant l'algorithme AC3
    """
    
    """
    Le constructeur de la classe prend en paramètre:
    
    
    - Les variables X sous forme de liste 
    (ex : Variable 0,1 = [0,1])
    
    
    - Le domaine D qui est un dictionnaire dont la clé d'indexation x permet de retrouver
    le domaine de la variable x sous forme de liste 
    (ex: D = {0 : ['ABC','EDF'], 1 : ['ABC', 'XYZ']})
    
    
    - Les contraintes C qui est un couple (R1,R2) qui sont tous les deux des dictionnaires
    Tout comme le domaine D, R1 est un dictionnaire dont la clé d'indexation x permet de retrouver
    les contraintes de la variable x sous la forme de liste. Chaque contrainte est une fonction.
    R2 est un dictionnaire dont la clé d'indexation est un couple (x,y) permettant de retrouver les contraintes
    du couple x,y sous la forme de liste
    Les contraintes R1 devront stocker des fonctions prenant un argument et les contraintes R2 des
    fonctions prenant deux arguments. Ils devront tous renvoyer un booléen
    
    (ex : R1 = {0 : [lambda x: len(x) == 4], 1 : [lambda x: len(x) == 5]} ) : 
    Contraintes vérifiant respectivement
    que la variable x0 soit de longueur 4 et que la variable x1 soit de longueur 5
    
    (ex : R2 = {(0,1) : [lambda x, y: x.startswith('a') and y.startswith('b')] )
    Contrainte vérifiant que la variable x0 commence par un a et que la variable x1 commence par un b
    
    """
    def __init__(self,X,D,C):
        (R1,R2) = C
        self.X = X
        self.D = D
        self.R1 = R1
        self.R2 = R2
        
    """
    Procédure arcReduce comme définit dans les polys
    """
    def arcReduce(self,x,y):
        change = False
        for vx in self.D[x]:
            if all( any( not(c(vx,vy)) for c in self.R2[(x,y)]) for vy in self.D[y]):
                self.D[x].remove(vx)
                change = True
        return change
    
    """
    Procédure ac3 comme définit dans les polys
    L'algorithme modifie les variables contenues dans l'instance de la classe, on a donc aucun return
    """
    def ac3(self):
        for x in self.X:
            for c in self.R1[x]:
                self.D[x] = list(filter(c,self.D[x]))
        worklist = list(self.R2.keys())
        while worklist:
            (x,y) = worklist.pop()
            if self.arcReduce(x,y):
                worklist = list(set(list(filter(lambda c: not(c[0] == y) and c[1] == x, list(self.R2.keys()))) + worklist))
    
    """
    Fonction solve permettant simplement d'appeler la procédure de filtrage AC3
    et de renvoyer l'ensemble des variables de l'instance à savoir X,D,C
    dont le D aura donc été filtré préalablement par l'AC3
    """
    def solve(self):
        self.ac3()
        """
        self.V = []
        self.I = {}
        for x in self.X:
            l = len(self.D[x])
            if l == 0:
                raise Exception
            elif l == 1:
                self.I[l] = self.D[x][0]
            else:
                self.V += [x]
        """
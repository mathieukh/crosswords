# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 20:27:44 2016

@author: sylom
"""

import copy as cp
import random as rand
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
            if not any( not any( not(c(vx,vy)) for c in self.R2[(x,y)]) for vy in self.D[y]):
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
    Fonction card_max permettant de renvoyer depuis une liste de variables données la liste des variables
    ayant un nombre de contraintes maximum avec les variables déjà instanciées par le forward_checking
    """
    def card_max(self,V):
        Vi = list(set(self.X) - set(V))
        if not Vi:
            return cp.deepcopy(V)
        cV = {}
        for v in V:
            cV[v] = 0
            for vi in Vi:
                if (v,vi) in self.R2:
                    cV[v] += len(self.R2[(v,vi)])
                if (vi,v) in self.R2:
                    cV[v] += len(self.R2[(vi,v)])
        m = max(cV, key=lambda i: cV[i])
        Vc = []
        for v,c in cV.items():
            if v==m or c == cV[m]:
                Vc += [v]
        return Vc
    
    """
    Fonction domain_min permettant de renvoyer depuis une liste de variables données une liste de variables
    ayant une cardinalité de domaine minimum
    """
    def domain_min(self,V):
        cV = {}
        for v in V:
            cV[v] = len(self.D[v])
        m = min(cV, key=lambda i: cV[i])
        Vc = []
        for v,c in cV.items():
            if v==m or c == cV[m]:
                Vc += [v]
        return Vc
    
    """
    Fonction choose_variable permettant depuis une liste de variables données de renvoyer une variable
    On appelle tout d'abord la fonction card_max, si une variable se distincte, on la renvoie.
    Sinon on continue : avec la liste des variables renvoyés par card_max on appelle domain_min.
    On renvoie depuis cette fonction un choix aléatoire de la liste renvoyé par la fonction
    """
    def choose_variable(self,V):
        Vc = self.card_max(V)
        if len(Vc)==1:
            return Vc[0]
        else:
            Vc = self.domain_min(Vc)
            return rand.choice(Vc)
    """
    Procédure check_forward permettant de vérifier la consistance d'une variable associé à une valeur et de réduire les domaines
    au maximum pour la suite de l'exécution de la procédure forward_checking
    """
                    
    def check_forward(self,xk,v):
        consistant = True
        for xj in self.X:
            if not xk == xj:
                self.D[xj] = list(filter(lambda vp: all(c(v,vp) for c in self.R2[(xk,xj)]), self.D[xj]))
                if not self.D[xj]:
                    consistant = False
                    break
        return consistant
                
    """
    Procédure forward_checking
    Si la liste des variables a instancier est vide, alors on quitte la procédure
    Sinon on choisit une variable x a instancier depuis la fonction choose_variable
    On boucle ensuite sur l'ensemble des valeurs du domaine de la variable x
    On sauvegarde l'ensemble des domaines en vue d'une restauration ultérieure en cas de backtrack
    Si l'appel à la procédure check_forward renvoie True (et donc que la valeur choisie est consistante),
    alors on entre dans la condition:
        On recopie l'ensemble des variables à instancier et l'on supprime à cette copie la variable xk. On la nomme Vt
        On réduit le domaine de la variable x à la valeur v
        On appelle la fonction forward_checking avec la liste des variables Vt
        Si la fonction échoue, on catche cette exception mais ne faisons rien
    On rétablit le domaine précedemment sauvegardé
    Si toutes les valeurs ont été testés, alors on échoue
    """
    def forward_checking(self,V):
        if not V:
            return
        else:
            xk = self.choose_variable(V)
            for v in self.D[xk]:
                Dt = cp.deepcopy(self.D)
                if self.check_forward(xk,v):
                    Vt = cp.deepcopy(V)
                    Vt.remove(xk)
                    self.D[xk] = [v]
                    try:
                        return self.forward_checking(Vt)
                    except Exception:
                        pass
                self.D = Dt
        raise Exception
            
    """
    Fonction solve
    On réduit les domaines par un filtrage AC3
    On recopie les variables X dans une variable V
    On recopie les domaines D dans une variable D car la procédure forward_checking modifie les domaines
    On essaie d'exécuter la fonction forward_checking
        A la fin de l'exécution du forward_checking et si il n'a pas échoué, cela signifie que tous les domaines sont
        réduits à un seul élément qui font office de solution
        On récupère l'ensemble de ces éléments que l'on met dans un dictionnaire I
    si elle échoue, cela signifie qu'il n'y a aucune solution, on affiche un message en ce sens, on échoue ensuite
    On restaure les domaines qui ont surement été modifiés par la procédure forward_checking
    On ne restaure pas les domaines en cas d'exception car la procédure forward_cheking s'occupe de la restaurer à chaque boucle
    """
    def solve(self):
        self.ac3()
        V = cp.deepcopy(self.X)
        D = cp.deepcopy(self.D)
        I = {}
        try:
            self.forward_checking(V)
            for x,v in self.D.items():
                I[x] = v[0]
        except Exception:
            print("No solution found")
            raise Exception
        self.D = D
        return I
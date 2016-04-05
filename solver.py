# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 20:27:44 2016

@author: sylom
"""

import copy as cp
import random as rand
import numpy as np
import functools as ft
      
class CSP:
    """
    Class CSP contenant l'algorithme AC3, Forward Checking, Conflict Backjumping
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
    Elle modifie directement les domaines de l'objet
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
    L'algorithme modifie directement les domaines de l'objet
    """
    def ac3(self):
        for x in self.R1.keys():
            for c in self.R1[x]:
                self.D[x] = list(filter(c,self.D[x]))
        worklist = list(self.R2.keys())
        R2k = list(self.R2.keys())
        while worklist:
            (x,y) = worklist.pop()
            if self.arcReduce(x,y):
                for (k,x) in filter(lambda c: not(c[0] == y) and c[1] == x, R2k):
                    if (k,x) not in worklist:
                        worklist.append((k,x))
    
    """
    Fonction domain_min permettant de renvoyer depuis une liste de variables données une liste de variables
    ayant une cardinalité de domaine minimum
    """
    def domain_min(self,V):
        cV = {}
        for v in V.keys():
            cV[v] = len(V[v])
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
        Vc = self.domain_min(V)
        return rand.choice(Vc)
        
    """
    Procédure check_forward permettant de vérifier la consistance d'une variable associée à une valeur et de réduire les domaines
    au maximum pour la suite de l'exécution de la procédure forward_checking
    Elle se rappelle récursivement si elle trouve un domaine unitaire après réduction
    """
                    
    def check_forward(self,x,vx,I,V):
        for y in (y for y in V.keys() if (x,y) in self.R2):
            V[y] = list(filter(lambda vy: all(c(vx,vy) for c in self.R2[(x,y)]), V[y]))
            if not V[y]:
                raise Exception
        v = next((c for c in V.keys() if len(V[c]) == 1),None)
        if v:
            I[v] = cp.deepcopy(V[v][0])
            del V[v]
            self.check_forward(v,I[v],I,V)
                
    """
    Procédure forward_checking
    Si la liste des variables a instancier est vide, alors on quitte la procédure
    Sinon on choisit une variable x a instancier depuis la fonction choose_variable
    On boucle ensuite sur l'ensemble des valeurs du domaine de la variable x
        On crée une copie de l'instance courante auquel on ajoute {x <- v}
        On crée une copie des variables auquel on ampute la variable x
        Ces copies permettent de ne pas altérer les variables et l'instance en cas de backtrack
        
        On cercle les procédures check_forward et forward_checking par un try except qui permettra de
        catcher les exceptions éventuellement soulevées par la découverte d'un domaine vide ou
        le parcours de toutes les valeurs d'une variable n'ayant pas abouti
    """
    def forward_checking(self,V,I):
        if not V:
            return I
        else:
            xk = self.choose_variable(V)
            for v in V[xk]:
                I_n = cp.deepcopy(I)
                I_n[xk] = v
                V_n = cp.deepcopy(V)
                del V_n[xk]
                try:
                    self.check_forward(xk,v,I_n,V_n)
                    return self.forward_checking(V_n,I_n)
                except Exception:
                    pass
        raise Exception
    

            

    
    """
    Fonction domain_min permettant de renvoyer depuis une liste de variables données une liste de variables
    ayant une cardinalité de domaine minimum
    """
    def domain_min_cbj(self,V):
        cV = {}
        for v in V.keys():
            cV[v] = len(V[v]['D'])
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
    def choose_variable_cbj(self,V):
        Vc = self.domain_min_cbj(V)
        return rand.choice(Vc)

    """
    Fonction propagate_cbj permettant de réduire les domaines commela fonction de check_forward.
    Celle-ci toutefois vient annoter les variables réduissant les domaines
    """
    def propagate_cbj(self,x,vx,I,V):
        for y in (y for y in V.keys() if (x,y) in self.R2):
            Vy = list(filter(lambda vy: all(c(vx,vy) for c in self.R2[(x,y)]), V[y]['D']))
            if set(V[y]['D']).intersection(Vy) or not Vy:
                V[y]['D'] = Vy
                V[y]['A'] = list(set(V[y]['A'] + I[x]['D']))
        v = next((c for c in V.keys() if len(V[c]['D']) == 1),None)
        if v:
            I[v] = {'V':cp.deepcopy(V[v]['D'][0]), 'D':cp.deepcopy(V[v]['A'])}
            del V[v]
            self.propagate_cbj(v,I[v]['V'],I,V)
        
    """
    Fonction cbj 
    La fonction de cbj permet de récupérer les variables ayant amenés une exception.
    Ces variables permettent de backjumper les niveaux n'ayant pas influencer la réduction absolu d'un domaine 
    """
    def cbj(self,V,I):
        if not V:
            return I
        A = next((V[x]['A'] for x in V.keys() if not V[x]['D']), None)
        if A:
            raise Exception(A)
        xk = self.choose_variable_cbj(V)
        conflit = []
        for v in V[xk]['D']:
            I_n = cp.deepcopy(I)
            I_n[xk] = {'V':v, 'D': [xk]}
            V_n = cp.deepcopy(V)
            del V_n[xk]
            try:
                self.propagate_cbj(xk,v,I_n,V_n)
                return self.cbj(V_n,I_n)
            except Exception as conflict:
                causes = conflict.args[0]
                if xk in causes:
                    conflit = list(set(causes + conflit))
                    pass
                else:
                    raise Exception(causes)
        raise Exception(conflit)
            
            
        
    """
    Fonction solve_cbj et solve_fc
    Elle appelle respectivement les procédures de résolution par cbj et fc
    Un paramètre ac3 booléen overridé par défaut à non permet de savoir si la résolution doit être précéder
    par un filtrage AC3 du CSP
    On filtre les domaines par les contraintes unitaires si l'AC3 n'est pas exécuté
    On copie le dictionnaire D dont les clés sont les variables.
    On récupère l'instance trouvée que l'on stocke dans l'objet dans la variable I pour être récupéré plus tard
    Si une exception est récupéré, ca signifie qu'aucune solution n'a été trouvée pour le CSP.
    On soulève donc une exception avec en argument le message
    """
    def solve_cbj(self, ac3=False):
        if ac3:
            self.ac3()
        else:
            for x in self.R1.keys():
                for c in self.R1[x]:
                    self.D[x] = list(filter(c,self.D[x]))
        try:
            V = cp.deepcopy(self.D)
            V = { k:{'D':v, 'A':[]}for k,v in V.items() }
            self.I = { x:v['V'] for x,v in self.cbj(V,{}).items() }
        except Exception:
            raise Exception('Aucune solution trouvée')
        return self.I
        
        
        
    def solve_fc(self, ac3=False):
        if ac3:
            self.ac3()
        else:
            for x in self.R1.keys():
                for c in self.R1[x]:
                    self.D[x] = list(filter(c,self.D[x]))
        try:
            V = cp.deepcopy(self.D)
            self.I = self.forward_checking(V,{})
        except Exception:
            raise Exception('Aucune solution trouvée')
        return self.I


class ValuedCSP:
    """
    Class ValuedCSP contenant l'algorithme DjiCSP
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
    
    - La matrice de valuations VM permet de stocker les valeurs associées
    Sous la forme 
    {
     'value1':
        {var1: v, var2: v2},
     'value2':
        {var1: v3, var2: v4} 
    }
    
    - La fonction f est une fonction qui devra prendre deux arguments et renvoyer un nombre.
    Cette fonction permet de définir la fonction qui permet d'évaluer un nouveau noeud depuis la valeur précédente value et la valeur de la variable v
    
    - La fonction fBorne est une fonction qui se sert de la fonction pour définir une borne supérieur
    La fonction prend en argument les variables V restantes à instancier et la valeur v courante de la variable
    On calcule ensuite la borne en choisissant pour chaque variable restante la valeur au poids le plus fort (sans regarder la consistante)
    pour savoir dans le meilleur des cas combien pourrait rapporter l'exploration de cette instance
    Cette évaluation permettra d'ordonner le développement des branches
    
    - Le initValue est la valeur initiale avec laquelle le CSP doit démarré
    
    Cette façon de stocker les valuations permet d'avoir plusieurs valuations associés à une valeur pour chaque variable
    """
    def __init__(self,X,D,C,VM,f,initValue):
        (R1,R2) = C
        self.X = X
        self.D = D
        self.R1 = R1
        self.R2 = R2
        self.VM = VM
        self.f = f
        self.initValue = initValue
        def fValue(I):
            return ft.reduce(f,I,initValue)
        def fBorne(V):
            return fValue([max([ vi for (wi,vi) in sorted([ (wd,self.VM[wd][kd]) for wd in ld],key=lambda w: w[1], reverse=True)]) for kd,ld in V.items()])
        self.fValue = fValue
        self.fBorne = fBorne
        
    """
    Fonction domain_min permettant de renvoyer depuis une liste de variables données une liste de variables
    ayant une cardinalité de domaine minimum
    """
    def domain_min(self,V):
        cV = {}
        for v in V.keys():
            cV[v] = len(V[v])
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
        Vca = {  k:sum([ 0 if (k,ky) not in self.R2 else len(self.R2[(k,ky)]) for ky in self.X if not ky == k]) for k in V.keys()}
        m = max(Vca.values())
        Vd = {k:l for k,l in V.items() if Vca[k] == m }
        Vc = self.domain_min(Vd)
        return rand.choice(Vc)
        
    """
    Procédure propagate permettant de réduire les domaines des variables V en rapport à la variable {x <- v}
    Modifie les variables V et I
    """
        
    def propagate(self,x,vx,V,I):
        for y in (y for y in V.keys() if (x,y) in self.R2):
            Vy = list(filter(lambda vy: all(c(vx,vy) for c in self.R2[(x,y)]), V[y]))
            V[y] = Vy
            if not V[y]:
                raise Exception
        v = next((c for c in V.keys() if len(V[c]) == 1),None)
        if v:
            I[v] = cp.deepcopy(V[v][0])
            del V[v]
            self.propagate(v,I[v],V,I)
    
    """
    Fonction DjjiCSP
    Une implémentation de l'algorithme de Djikstra de plus court chemin modifié afin de satisfaire le CSP
    On commence par ordonner de façon décroissante grâce à la matrice VM
    C'est à dire que plus le mot sera fort et voulu, plus le mot sera au début de la liste
    
    On instancie une frontiere qui permet de stocker les instances à développer par l'algorithme
        Une instance se présente sous la forme:
        {value : v, 'V': V, 'I': I, 'borne':b}
        value permet de stocker la valeur de l'instance en ce noeud
        V les variables restantes à instancier en ce noeud
        I l'instance courante en ce noeud
        borne est une borne supérieur du poids espéré depuis l'instance partielle
    Tant que la frontieres n'est pas vide, on pop l'instance retourné par getInstance
        getInstance tri sur deux critères.
        Tout d'abord la borne. Plus une instance est prometteuse, plus elle sera poussée vers le fond
        Puis sur le nombre de variables restants à instancier. Moins une instance aura de variables
        restantes, plus elle sera poussée vers le fond. Cela permet de récupérer au plus vite une solution
        Ces critères de tri appliqués permettent de pousser l'instance la plus prometteuse vers le fond de la liste que l'on pop alors
    On développe l'instance comme pour le forward_checking à la différence que si l'instanciation suivante est consistante localement,
    alors on ajoute cette instance à la frontiere    
    """
    
    def getInstance(self,frontiere):
        frontiere.sort(key=lambda f: (f['borne'], -len(f['V'])))
        return frontiere.pop()
        
    def DjiCSP(self,V,I):
        frontiere = [{'value':self.initValue, 'V': V, 'I': I, 'borne': self.fBorne(V)}]
        while frontiere:
            P = self.getInstance(frontiere)
            if not P['V']:
                return P['I']
            xk = self.choose_variable(P['V'])
            for v in P['V'][xk]:
                I_n = cp.deepcopy(P['I'])
                I_n[xk] = v                   
                V_n = cp.deepcopy(P['V'])
                del V_n[xk]
                try:
                    self.propagate(xk,v,V_n,I_n)
                    value = cp.deepcopy(self.f(P['value'],self.VM[v][xk]))
                    borne = value if not V_n else self.fBorne(V,value)
                    frontiere.append({'value':value, 'V':V_n, 'I':I_n, 'borne': borne})
                except Exception:
                    continue
        raise Exception

    def DFS_CSP(self,V,I,borne,value,bestSolution):
        if not V:
            return {'value': value, 'I': I}
        else:
            xk = self.choose_variable(V)
            for v in V[xk]:
                try:
                    V_n = cp.deepcopy(V)
                    I_n = cp.deepcopy(I)
                    del V_n[xk]
                    I_n[xk] = v
                    self.propagate(xk,v,V_n,I_n)
                    v_n = self.f(value, self.VM[v][xk])
                    bornSup = self.f(v_n,self.fBorne(V_n))
                    if bornSup<=borne and bestSolution:
                        break
                    else:
                        sol = self.DFS_CSP(V_n, I_n, borne, v_n, bestSolution)
                        if (sol and (not bestSolution or (sol['value']>bestSolution['value']))):
                            bestSolution = sol
                            borne = bestSolution['value']
                except Exception:
                    pass
            return bestSolution
        
            
        
                
    """
    La fonction solve permet d'appeler la fonction DjiCSP sur le problème de l'objet.
    L'extraction des domaines unitaires permet de définir dès le départ une instance de départ
    On stocke la solution si elle existe ou sinon on soulève une exception
    """
    def solve(self):
        try:
            V = cp.deepcopy(self.D)
            I = {}
            for x in self.R1.keys():
                for c in self.R1[x]:
                    V[x] = list(filter(c,V[x]))
            v = next((c for c in V.keys() if len(V[c]) == 1),None)
            if v:
                self.propagate(v,I[v],V,I)
#            self.I = self.DjiCSP(V,I)
            V = { kd: [ wi for (wi,vi) in sorted([ (wd,self.VM[wd][kd]) for wd in ld],key=lambda w: w[1], reverse=True)] for kd,ld in V.items()}
            sol = self.DFS_CSP(V,I,self.initValue,self.initValue,None)
            if sol:
                self.I = sol['I']
            else:
                raise Exception
        except Exception:
            raise Exception('Aucune solution trouvée')
        return self.I
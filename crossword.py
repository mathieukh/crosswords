# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 22:02:42 2016

@author: sylom
"""
import re
import numpy as np
import functools as ft
import solver as sl

class Crossword:
    """ 
    La classe crossword qui définit la grille de mots croisés
    avec un paramètre comprenant la hauteur et la largeur de la grille
    Un paramètre words permet de stocker un dictionnaire d'objet que l'on détaillera par la suite
    Le paramètre CSP permet de stocker le problème sous la forme d'un CSP (détaillé aussi par la suite)

    Le constructuer de cette classe prend en paramètre crossword qui est un np.array de 2 dimensions
    remplit par des - pour les cases blanches ou des lettres et un caractère quelconque pour les cases noires
    Par convention et pour faciliter l'unification, on définit les cases noirés par des *
    """
    def __init__(self, crossword, dico):
        (self.height, self.width) = crossword.shape;
        self.words = self.getWords(crossword)
        self.CSP = self.getCSP(dico)
        
    """ 
    Fonction générant un np.array depuis l'instance remplit des mots contenues dans words
    """
    def getCrossword(self):
        cr = np.array([['*' for j in range(self.width)]for i in range(self.height)])
        for k,w in self.words.items():
            (indice,start_char) = w['index']
            l = len(w['word'])
            for i in range(l):
                if w['orientation'] == 'H':
                    cr[indice][(start_char+i)] = w['word'][i]
                else:
                    cr[(start_char+i)][indice] = w['word'][i]
        return cr
        
    """
    Fonction permettant de trouver l'ensemble des mots de la grille crossword en np.array
    et retourner un dictionnaire dont la clé d'index attribue un numéro unique au mot
    Chaque mot comportera:
    - son orientation 'H' ou 'V'
    - Le mot sous forme de string
    - un couple index (i,j) où i est l'indice ligne ou colonne selon l'orientation et 
    j l'indice d'où commence le mot dans la ligne ou colonne
    """
        
    def getWords(self, crossword):
        """ On récupère la liste des lignes de la matrice """
        rows = ["".join(np.reshape(n,self.width).tolist()) for n in np.vsplit(crossword,self.height)];
        """ On récupère la liste des colonnes de la matrice"""
        columns = ["".join(np.reshape(n,self.height).tolist()) for n in np.hsplit(crossword,self.width)];
        """ 
        On instancie un dictionnaire vide words ainsi que la variable index à 0
        """
        words = {}
        index = 0
        
        """
        On filtre ensuite grâce à une regex [a-zA-Z\-][a-zA-Z\-]+ chaque ligne et colonne une à une
        La regex [a-zA-Z\-][a-zA-Z\-]+ récupère dans un string l'ensemble des groupes comportant au moins deux lettres ou deux tirets
        (on considère qu'un mot ne peut être inférieur à deux lettres)
        """
        for i in range(self.height):
            for m in re.finditer('[a-zA-Z\-][a-zA-Z\-]+', rows[i]):
                 words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'H'}
                 index += 1
        for i in range(self.width):
            for m in re.finditer('[a-zA-Z\-][a-zA-Z\-]+', columns[i]):
                 words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'V'}
                 index += 1
        return words
        
        
    """
    Fonction permettant de créer la liste des contraintes des mots entre eux en retournant
    une liste de dictionnaire avec un couple 'HORIZONTAL' et 'VERTICAL'
    Chaque couple permet de donner l'indice du mot sous contrainte et le caractère sous contrainte
    Soit le couple {'HORIZONTAL': (0,3), 'VERTICAL': (5,5)}, on lit donc que 
    le mot 0, caractère 4 (indice partant de 0) doit être égale au mot 5, caractère 6
    """
    def getConstraints(self):
        contraints = []
        words_h = []
        words_v = []
        for key, value in self.words.items():
            if(value['orientation'] == 'H'):
                words_h += [(key,value)]
            else:
                words_v += [(key,value)]
                
        for (key_h, horiz_word) in words_h:
            for horiz_word_char_index in range(horiz_word['index'][1], (horiz_word['index'][1] + len(horiz_word['word']))):
                for (key_v, vert_word) in filter(lambda w: w[1]['index'][0] == horiz_word_char_index, words_v):
                    for vert_word_char_index in range(vert_word['index'][1], (vert_word['index'][1] + len(vert_word['word']))):
                        if(vert_word_char_index == horiz_word['index'][0]):
                            contraints += [{
                            'HORIZONTAL': (key_h,  horiz_word_char_index - horiz_word['index'][1]), 
                            'VERTICAL': (key_v, vert_word_char_index - vert_word['index'][1]) }]
                            break
        return contraints
        
    """
    Fonction générant le CSP du mots croisés
    """
        
    def getCSP(self,dico):
        
        """
        On définit un dictionnaire de mots (un vrai dictionnaire) qui sera contenu dans une liste
        Pour cet exemple, le dico est hardcodé mais on peut imaginer un argument à la fonction qui permettra de définir le dico
        """
        """
        
        On définit l'ensemble des fonctions qui permettront de définir les contraintes (voir AC3 pour comprendre)
        La fonction testLen permet de savoir si la longueur de x est égale à n
        La fonction testCharacter permet de savoir si le caractère i du mot w est égale à c
        La fonction testSameCharacters permet de savoir si le caractère i1 du mot w1 est égale au caractère i2 du mot w2
        La fonction differentWord permet de vérifier que les mots w1 et w2 sont bien différents
        """
        def testLen(x,n):
            return len(x) == n    
        def testCharacter(w,i,c):
            return w[i] == c    
        def testSameCharacters(w1,w2,i1,i2):
            return w1[i1] == w2[i2]
        def differentWord(w1,w2):
            return not (w1 == w2)
        
        """
        On définitX et le nom des variables de chaque mot par leur numéro respectif dans le dictionnaire words (défini plus haut) 
        On initialise le domaine D et on copie le dictionnaire de mots (le vrai) dans le domaine de chaque variable
        """
        X = list(self.words.keys())
        D = {}
        for x in X:
            D[x] = dico.copy()
            
        """
        On initialise R1 et R2
        On ajoute grâce à partial la fonction testLen où l'on va surchager le paramètre n (contrainte de mot respectant la taille de la case)
        On ajoute la fonction testCharacter où l'on surcharge i et c (contrainte pour forcer les caractères déjà présents)
        """
        R1 = {}
        R2 = {}   
        
        for k,w in self.words.items():
            R1[k] = [ft.partial(testLen, n=len(w['word']))]
            R1[k] += [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
            
        """
        On ajoute à l'ensemble des couples la contrainte permettant de vérifier que tous les mots sont différents
        """
        
        for x in X:
            ydiff = (y for y in X if not x == y)
            for y in ydiff:
                R2[(x,y)] = [differentWord]
                
        """
        On récupère l'ensemble des contraintes entre les mots que l'on récupère par la fonction getConstraints()
        On ajoute au couple contraints la fonction testSameCharacters où l'on surchaffe les indices de comparaison
        """
                    
        for c in self.getConstraints():
            (ih,ch) = c['HORIZONTAL']
            (iv,cv) = c['VERTICAL']
            if (ih,iv) in R2:
                R2[(ih,iv)] += [ft.partial(testSameCharacters, i1=ch, i2=cv)]
            else:
                R2[(ih,iv)] = [ft.partial(testSameCharacters, i1=ch, i2=cv)]
            if (iv,ih) in R2:
                R2[(iv,ih)] += [ft.partial(testSameCharacters, i1=cv, i2=ch)]
            else:
                R2[(iv,ih)] = [ft.partial(testSameCharacters, i1=cv, i2=ch)]
            
        return sl.CSP(X,D,(R1,R2))
        
    """
    La fonction solve appelle la fonction solve de la variable CSP (voir classe CSP)
    On récupère le domaine filtré par l'algorithme ac3 (pour l'instant)
    Les domaines ne comportant qu'une valeur sont forcément solution de la variable,
    on les écrit donc dans le dictionnaire words qui permettra de reconstruire par la suite le mots croisés avec
    les mots trouvés
    """
    
    """
    def solve(self):
        (X,D,C) = self.CSP.solve()
        for kd,d in D.items():
            if(len(d) == 1):
                self.words[kd]['word'] = d[0]
    """    
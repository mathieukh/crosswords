# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 22:02:42 2016

@author: sylom
"""
import re
import tkinter as tk
import numpy as np
import functools as ft
import solver as sl

"""
Fonction permettant de générer une grille de mots croisés.
height : hauteur de la grille, width : la largeur et numberBlocks : le nombre de blocs noirs 
"""
def generateCrossword(height,width, numberBlocks=0):
    size = height*width
    ar = np.empty(size, dtype=np.str)
    for i in range(size):
        if i < numberBlocks:
            ar[i] = '*'
        else:
            ar[i]= '-'
    np.random.shuffle(ar)
    ar = np.reshape(ar, (height, width))
    return ar
        
"""
Fonction permettant de d'ouvrir l'application GUI
"""
def displayCrossword(crossword):
    crossword = getArrayCrossword(crossword)
    fenetre = tk.Tk()
    l=0
    c=0
    for ligne in crossword:
        l+=1
        larg=ligne.size
        for colonne in ligne:
            c=c+1
            if(colonne=='-'):
                tk.Button(fenetre, bg="white", width=5, height=2).grid(row=l, column=c-(l-1)*larg)
            elif(colonne=='*'):
                tk.Button(fenetre, bg="black", width=5, height=2).grid(row=l, column=c-(l-1)*larg)
            else:
                tk.Button(fenetre, text='%s' %colonne, bg="white", width=5, height=2).grid(row=l, column=c-(l-1)*larg)    
    fenetre.mainloop()
    return
    
""" 
Fonction générant un np.array depuis un crossword
"""
def getArrayCrossword(crossword):
    (height,width) = crossword['size']
    cr = np.array([['*' for j in range(width)]for i in range(height)])
    for k,w in crossword['words'].items():
        (indice,start_char) = w['index']
        l = len(w['word'])
        for i in range(l):
            if w['orientation'] == 'H':
                cr[indice][(start_char+i)] = w['word'][i]
            else:
                cr[(start_char+i)][indice] = w['word'][i]
    return cr
    
"""
Fonction générant un crossword depuis un np.array
"""
def getCrossword(crosswordArray):
    crossword = {}
    crossword['size'] = crosswordArray.shape
    crossword['words'] = getWords(crosswordArray)
    return crossword
    
"""
Fonction générant le CSP du mots croisés
"""       
def getCSP(crossword,dico):
    
    """
    Fonction qui permet de savoir si le caractère i du mot w est égale à c
    """ 
    def testCharacter(w,i,c):
        return w[i] == c    
        
    """
    Fonction qui permet de savoir si le caractère i1 du mot w1 est égale au caractère i2 du mot w2
    """
    def testSameCharacters(w1,w2,i1,i2):
        return w1[i1] == w2[i2]
        
    """
    Fonction qui permet de vérifier que les mots w1 et w2 sont bien différents
    """
    def differentWord(w1,w2):
        return not (w1 == w2)
        
    """
    X : contient la liste des variables
    D : contient le domaine de chaque variable
    """
    X = list(crossword['words'].keys())
    D = {}
    for x in X:
        D[x] = list(set(filter(lambda w: len(crossword['words'][x]['word']) == len(w),dico)))
        
    """
    R1 et R2 les dictionnaires contenant les contraintes 
    """
    R1 = {}
    R2 = {}   
    
    """
    On ajoute à R1 les contraintes pour forcer les caractères déjà présent
    """
    for k,w in crossword['words'].items():
        R1[k] = [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
        if not R1[k]:
            R1.pop(k)
        
    """
    On ajoute à R2 les contraintes permettant de vérifier que tous les mots sont différents
    """
    for x in X:
        ydiff = (y for y in X if not x == y and len(crossword['words'][x]['word']) == len(crossword['words'][y]['word']))
        for y in ydiff:
            R2[(x,y)] = [differentWord]
            
    """
    On récupère l'ensemble des contraintes entre les mots que l'on récupère par la fonction getConstraints()
    On ajoute au couple contraints la fonction testSameCharacters où l'on override les indices de comparaison
    """         
    for c in getConstraints(crossword):
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
Fonction générant le CSP valué du mots croisés
"""        
def getCSPValued(crossword,dico):
    
    def testCharacter(w,i,c):
        return w[i] == c   
        
    def testSameCharacters(w1,w2,i1,i2):
        return w1[i1] == w2[i2]
        
    def differentWord(w1,w2):
        return not (w1 == w2)
        
    X = list(crossword['words'].keys())
    D = {}
    
    for x in X:
        D[x] = list(set(filter(lambda w: len(crossword['words'][x]['word']) == len(w) , map(lambda w: w[0], dico))))
        
    """
    VM : matrice qui permet d'associer un poids au mot par variable
    """
    VM = { w:{ x:(v if w in D[x] else 0.1) for x in X } for (w,v) in sorted(dico,key=lambda w: w[1])}
        
    R1 = {}
    R2 = {}   
    
    for k,w in crossword['words'].items():
        R1[k] = [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
        if not R1[k]:
            R1.pop(k)
    
    for x in X:
        ydiff = (y for y in X if not x == y and len(crossword['words'][x]['word']) == len(crossword['words'][y]['word']))
        for y in ydiff:
            R2[(x,y)] = [differentWord]
                        
    for c in getConstraints(crossword):
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
    return sl.ValuedCSP(X,D,(R1,R2), VM, (lambda value, v: round((value * v), len(X))), 1)
    
"""
Fonction permettant de trouver l'ensemble des mots retourner sous forme de dictionnaire
Chaque mot comportera:
- son orientation 'H' ou 'V'
- Le mot sous forme de string
- un couple index (i,j) indices d'où commence le mot
"""
def getWords(crossword):
    
    """ row la liste des lignes de la matrice """
    rows = ["".join(np.reshape(n,crossword.shape[1]).tolist()) for n in np.vsplit(crossword,crossword.shape[0])];
    
    """ columns la liste des colonnes de la matrice"""
    columns = ["".join(np.reshape(n,crossword.shape[0]).tolist()) for n in np.hsplit(crossword,crossword.shape[1])];
    
    """ words dictionnaire vide """
    words = {}
    index = 0
    
    """
    On récupère dans un string l'ensemble des groupes comportant au moins deux lettres ou deux tirets
    """
    for i in range(crossword.shape[0]):
        for m in re.finditer('[a-zA-Z\-][a-zA-Z\-]+', rows[i]):
             words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'H'}
             index += 1
    for i in range(crossword.shape[1]):
        for m in re.finditer('[a-zA-Z\-][a-zA-Z\-]+', columns[i]):
             words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'V'}
             index += 1
    return words
    
"""
Fonction qui permet de créer la liste des contraintes des mots entre eux 
"""
def getConstraints(crossword):
    contraints = []
    words_h = []
    words_v = []
    for key, value in crossword['words'].items():
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
Fonction qui appelle la fonction solve de l'objet CSP 
I : instanciation 
words : dictionnaire qui permettra de reconstruire par la suite le mots croisés avec les mots trouvés
Renvoie False si aucune solution trouvée et True sinon
"""
def solve(crossword,dico, resolution='CBJ'):
    try:
        CSP = getCSP(crossword,dico)
        if resolution == 'CBJ':
            I = CSP.solve_cbj()
        elif resolution == 'AC3FC':
            I = CSP.solve_fc(True)
        elif resolution == 'FC':
            I = CSP.solve_fc()
        else:
            raise Exception('Les résolutions possibles sont CBJ, AC3FC, FC')
        for kd,d in I.items():
            crossword['words'][kd]['word'] = d
        return True
    except Exception as e:
        print(e.args[0])
        return False

"""
Fonction qui appelle la fonction solve de l'objet ValuedCSP 
I : : instanciation
words dictionnaire qui permet de reconstruire par la suite le mots croisés avec les mots trouvés
Renvoie False si aucune solution trouvée et True sinon
"""        
def solve_valued(crossword,dicoValued):
    try:
        CSP = getCSPValued(crossword,dicoValued)
        I = CSP.solve()
        for kd,d in I.items():
            crossword['words'][kd]['word'] = d
        return True
    except Exception as e:
        print(e.args[0])
        return False
    
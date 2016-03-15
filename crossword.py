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
La fonction prend 3 paramètres height, width et numberBlocks permettant respectivement
de une grille de la taille height * width ayant un nombre de blocs noirs égal à numberBlocks
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
    menubar = tk.Menu(fenetre)
    
    def alert():
        tk.showinfo("alerte", "Bravo!")

    menu1 = tk.Menu(menubar, tearoff=0)
    menu1.add_command(label="Nouveau", command=alert)
    menu1.add_command(label="Sauvegarder", command=alert)
    menu1.add_command(label="Charger", command=alert)
    menu1.add_separator()
    menu1.add_command(label="Quitter", command=fenetre.quit)
    menubar.add_cascade(label="Fichier", menu=menu1)
    
    fenetre.config(menu=menubar)      
    
    fenetre.mainloop()
    return
    
""" 
Fonction static générant un np.array depuis un crossword
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
Fonction static générant un crossword depuis un np.array
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
    On définit un dictionnaire de mots (un vrai dictionnaire) qui sera contenu dans une liste
    Pour cet exemple, le dico est hardcodé mais on peut imaginer un argument à la fonction qui permettra de définir le dico
    """
    """
    
    On définit l'ensemble des fonctions qui permettront de définir les contraintes (voir AC3 pour comprendre)
    La fonction testCharacter permet de savoir si le caractère i du mot w est égale à c
    La fonction testSameCharacters permet de savoir si le caractère i1 du mot w1 est égale au caractère i2 du mot w2
    La fonction differentWord permet de vérifier que les mots w1 et w2 sont bien différents
    """ 
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
    X = list(crossword['words'].keys())
    D = {}
    for x in X:
        D[x] = list(set(filter(lambda w: len(crossword['words'][x]['word']) == len(w),dico)))
        
    """
    On initialise R1 et R2
    On ajoute grâce à partial la fonction testLen où l'on va surchager le paramètre n (contrainte de mot respectant la taille de la case)
    On ajoute la fonction testCharacter où l'on surcharge i et c (contrainte pour forcer les caractères déjà présents)
    """
    R1 = {}
    R2 = {}   
    
    for k,w in crossword['words'].items():
        R1[k] = [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
        if not R1[k]:
            R1.pop(k)
        
    """
    On ajoute à l'ensemble des couples la contrainte permettant de vérifier que tous les mots sont différents
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
    
    """
    On définit un dictionnaire de mots (un vrai dictionnaire) qui sera contenu dans une liste
    Pour cet exemple, le dico est hardcodé mais on peut imaginer un argument à la fonction qui permettra de définir le dico
    """
    """
    
    On définit l'ensemble des fonctions qui permettront de définir les contraintes (voir AC3 pour comprendre)
    La fonction testCharacter permet de savoir si le caractère i du mot w est égale à c
    La fonction testSameCharacters permet de savoir si le caractère i1 du mot w1 est égale au caractère i2 du mot w2
    La fonction differentWord permet de vérifier que les mots w1 et w2 sont bien différents
    """ 
    def testCharacter(w,i,c):
        return w[i] == c    
    def testSameCharacters(w1,w2,i1,i2):
        return w1[i1] == w2[i2]
    def differentWord(w1,w2):
        return not (w1 == w2)
    """
    On définitX et le nom des variables de chaque mot par leur numéro respectif dans le dictionnaire words (défini plus haut) 
    On créé la matrice VM qui permet d'associer un poids au mot par variable. On ordonne le dictionnaire de facon croissante
    de telle sorte que si un mot est défini dans le dictionnairedeux fois avec deux poids différents, alors le poids supérieur écrasera toujours
    le poids inférieur
    On initialise le domaine D et on copie le dictionnaire de mots (le vrai) dans le domaine de chaque variable
    """
    X = list(crossword['words'].keys())
    VM = { w:{ x:v for x in X } for (w,v) in sorted(dico,key=lambda w: w[1])}
    D = {}
    for x in X:
        D[x] = list(set(filter(lambda w: len(crossword['words'][x]['word']) == len(w) , map(lambda w: w[0], dico))))
        
    """
    On initialise R1 et R2
    On ajoute grâce à partial la fonction testLen où l'on va surchager le paramètre n (contrainte de mot respectant la taille de la case)
    On ajoute la fonction testCharacter où l'on surcharge i et c (contrainte pour forcer les caractères déjà présents)
    """
    R1 = {}
    R2 = {}   
    
    for k,w in crossword['words'].items():
        R1[k] = [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
        if not R1[k]:
            R1.pop(k)
        
    """
    On ajoute à l'ensemble des couples la contrainte permettant de vérifier que tous les mots sont différents
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
    return sl.ValuedCSP(X,D,(R1,R2), VM, (lambda value, v: value * v), 1)
    
"""
Fonction permettant de trouver l'ensemble des mots de la grille crossword en np.array
et retourner un dictionnaire dont la clé d'index attribue un numéro unique au mot
Chaque mot comportera:
- son orientation 'H' ou 'V'
- Le mot sous forme de string
- un couple index (i,j) où i est l'indice ligne ou colonne selon l'orientation et 
j l'indice d'où commence le mot dans la ligne ou colonne
"""
def getWords(crossword):
    """ On récupère la liste des lignes de la matrice """
    rows = ["".join(np.reshape(n,crossword.shape[1]).tolist()) for n in np.vsplit(crossword,crossword.shape[0])];
    """ On récupère la liste des colonnes de la matrice"""
    columns = ["".join(np.reshape(n,crossword.shape[0]).tolist()) for n in np.hsplit(crossword,crossword.shape[1])];
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
Fonction permettant de créer la liste des contraintes des mots entre eux en retournant
une liste de dictionnaire avec un couple 'HORIZONTAL' et 'VERTICAL'
Chaque couple permet de donner l'indice du mot sous contrainte et le caractère sous contrainte
Soit le couple {'HORIZONTAL': (0,3), 'VERTICAL': (5,5)}, on lit donc que 
le mot 0, caractère 4 (indice partant de 0) doit être égale au mot 5, caractère 6
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
La fonction solve appelle la fonction solve de la variable CSP (voir classe CSP)
On récupère I qui est une solution sous la forme {var: val, var2: val2}
On les écrit donc dans le dictionnaire words qui permettra de reconstruire par la suite le mots croisés avec
les mots trouvés
Le dictionnaire doit être une liste de mots
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
La fonction solve_valued appelle la fonction solve de la variable ValuedCSP (voir classe ValuedCSP)
On récupère I qui est une solution sous la forme {var: val, var2: val2}
On les écrit donc dans le dictionnaire words qui permettra de reconstruire par la suite le mots croisés avec
les mots trouvés
Le dictionnaire doit être une liste de n-uplet de la forme (mot,valeur)
Si plusieurs occurence du mot apparaissent dans le dictionnaire ayant des valeurs différentes, on conservera seulement la plus grande
Renvoie False si aucune solution trouvée et True sinon
"""        
def solve_valued(crossword,dico):
    try:
        CSP = getCSPValued(crossword,dico)
        I = CSP.solve()
        for kd,d in I.items():
            crossword['words'][kd]['word'] = d
        return True
    except Exception as e:
        print(e.args[0])
        return False
    
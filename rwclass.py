# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 20:31:30 2016

@author: sylom
"""

import pickle
import re
import collections

"""
Fonction qui permet de charger un fichier
file : nom du fichier a charger
"""
def readFile(file):
    with open(file, 'rb') as f:
        return pickle.load(f)
       
"""
Fonction qui permet de sauvegarder un fichier
file : nom du fichier
obj : contenu à sauvegarder
"""
def writeFile(file,obj):
    with open(file, 'wb') as f:
        return pickle.dump(obj,f)
   
"""
Fonction qui retourne un dictionnaire à thème valué à partir d'un texte
"""     
def getValuedDictionaryFromText(text):
    words = [ str.upper(w) for w in re.findall('[a-zA-Z][a-zA-Z]+', text)]
    length = len(words)
    return [ (w,(c/length)) for w,c in collections.Counter(words).items()]
    
"""
Fonction qui retourne un dictionnaire valué en fusionnant un dictionnaire normal et un à thème
"""
def getDicoValued(dicoFaible, dicoFort):
    dicoFa = [ (d,0.1) for d in [str.upper(line.rstrip('\n')) for line in open(dicoFaible)]]
    dicoFo = [ (d,1) for d in [str.upper(line.rstrip('\n')) for line in open(dicoFort)]]
    return dicoFa + dicoFo
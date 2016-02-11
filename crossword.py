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
    """ La classe crossword qui définit la grille de mots croisés
    avec un paramètre comprenant la hauteur et la largeur de la grille"""
    
    def __init__(self, crossword):
        (self.height, self.width) = crossword.shape;
        self.words = self.getWords(crossword)
        self.constraints = self.getConstraints()
        self.AC3 = self.getCSP()
        
    def getCSP(self):
        
        dico = []
        dico += ['SITE','CANS']
        dico += ['BEES','SIDE']
        dico += ['ANT', 'SUN']
        dico += ['IDAS','AXIS','IDLY','DEER','EAST','READ','SUB','IVE','ENDED','TEE','LOS','SASSY','STAND','ALI','EVE','DRIVE','RED','SEE']
            
        def testLen(x,n):
            return len(x) == n    
        def testCharacter(w,i,c):
            return w[i] == c    
        def testSameCharacters(w1,w2,i1,i2):
            return w1[i1] == w2[i2]
        def differentWord(w1,w2):
            return not (w1 == w2)
        
        X = list(self.words.keys())
        D = {}
        for x in X:
            D[x] = dico.copy()
        R1 = {}
        R2 = {}   
        
        for k,w in self.words.items():
            R1[k] = [ft.partial(testLen, n=len(w['word']))]
            R1[k] += [ft.partial(testCharacter, i=m.start(), c=m.group(0)) for m in re.finditer('[a-zA-Z]', w['word'])]
 
        for x in X:
            for y in X: 
                if not x == y: 
                    R2[(x,y)] = [differentWord]
                    
        for c in self.constraints:
            (ih,ch) = c['HORIZONTAL']
            (iv,cv) = c['VERTICAL']
            R2[(ih,iv)] += [ft.partial(testSameCharacters, i1=ch, i2=cv)]
            R2[(iv,ih)] += [ft.partial(testSameCharacters, i1=cv, i2=ch)]
            
        return sl.AC3(X,D,(R1,R2))
        
    def getWords(self, crossword):
        rows = ["".join(np.reshape(n,self.width).tolist()) for n in np.vsplit(crossword,self.height)];
        columns = ["".join(np.reshape(n,self.height).tolist()) for n in np.hsplit(crossword,self.width)];
        words = {}
        index = 0
        for i in range(self.height):
            for m in re.finditer('\D\D+', rows[i]):
                 words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'H'}
                 index += 1
        for i in range(self.width):
            for m in re.finditer('\D\D+', columns[i]):
                 words [index] = {'word':m.group(0), 'index':(i,m.start()), 'orientation': 'V'}
                 index += 1
        return words
        
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
        return contraints
        
    def solve(self):
        return self.AC3.solve()